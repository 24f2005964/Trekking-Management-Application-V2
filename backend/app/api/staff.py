from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import User, Trek, Booking
from app.utils.decorators import approved_staff_required
from app.utils.cache import invalidate_treks_cache, invalidate_dashboard_cache
from app.tasks.scheduled import send_custom_notification

staff_bp = Blueprint('staff', __name__, url_prefix='/api/v1/staff')

def _get_current_staff():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) if user_id else None
    if user is None:
        raise ValueError("Authenticated staff member not found.")
    return user

@staff_bp.route('/dashboard', methods=['GET'])
@approved_staff_required
def dashboard():
    staff = _get_current_staff()
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff.id).all()
    assigned_ids = [t.id for t in assigned_treks]

    total_assigned = len(assigned_treks)
    open_count = sum(1 for t in assigned_treks if t.status == 'Open')
    completed_count = sum(1 for t in assigned_treks if t.status == 'Completed')

    participants_count = 0
    if assigned_ids:
        participants_count = db.session.query(db.func.sum(Booking.seats_booked))\
            .filter(Booking.trek_id.in_(assigned_ids), Booking.status == 'Confirmed').scalar() or 0

    return jsonify({
        'counts': {
            'total_assigned': total_assigned,
            'open_treks': open_count,
            'completed_treks': completed_count,
            'total_participants': participants_count
        }
    }), 200


@staff_bp.route('/treks', methods=['GET'])
@approved_staff_required
def get_assigned_treks():
    staff = _get_current_staff()
    treks = Trek.query.filter_by(assigned_staff_id=staff.id).order_by(Trek.start_date.asc()).all()

    results = []
    for t in treks:
        d = t.to_dict()
        confirmed_count = db.session.query(db.func.sum(Booking.seats_booked))\
            .filter_by(trek_id=t.id, status='Confirmed').scalar() or 0
        d['confirmed_participants'] = confirmed_count
        results.append(d)

    return jsonify({'treks': results}), 200


@staff_bp.route('/treks/<int:trek_id>/slots', methods=['PUT'])
@approved_staff_required
def update_trek_slots(trek_id):
    staff = _get_current_staff()
    trek = db.session.get(Trek, trek_id)
    if not trek or trek.assigned_staff_id != staff.id:
        return jsonify({'error': 'Trek not found or not assigned to you.'}), 404

    data = request.get_json() or {}
    available_slots = data.get('available_slots')
    if available_slots is None:
        return jsonify({'error': 'available_slots is required.'}), 400

    available_slots = int(available_slots)
    if available_slots < 0 or available_slots > trek.total_slots:
        return jsonify({'error': f'Available slots must be between 0 and total capacity ({trek.total_slots}).'}), 400

    active_bookings = db.session.query(db.func.sum(Booking.seats_booked))\
        .filter_by(trek_id=trek.id, status='Confirmed').scalar() or 0
    max_available = max(0, trek.total_slots - int(active_bookings))
    if available_slots > max_available:
        return jsonify({
            'error': f'Cannot set available slots to {available_slots}. With {active_bookings} active booking(s), maximum remaining is {max_available}.'
        }), 400

    trek.available_slots = available_slots
    if trek.available_slots == 0 and trek.status == 'Open':
        trek.status = 'Closed'

    db.session.commit()
    invalidate_treks_cache()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Slots updated for {trek.name}.', 'trek': trek.to_dict()}), 200


@staff_bp.route('/treks/<int:trek_id>/status', methods=['PUT'])
@approved_staff_required
def update_trek_status(trek_id):
    staff = _get_current_staff()
    trek = db.session.get(Trek, trek_id)
    if not trek or trek.assigned_staff_id != staff.id:
        return jsonify({'error': 'Trek not found or not assigned to you.'}), 404

    data = request.get_json() or {}
    status = data.get('status')
    if status not in ['Open', 'Closed', 'Completed']:
        return jsonify({'error': 'Status must be Open, Closed, or Completed.'}), 400

    trek.status = status
    if status == 'Closed':
        trek.available_slots = 0
    elif status == 'Completed':
        trek.available_slots = 0
        # Mark confirmed bookings as Completed
        Booking.query.filter_by(trek_id=trek.id, status='Confirmed').update({'status': 'Completed'})
    elif status == 'Open':
        # When reopening, accurately restore remaining capacity based on active bookings
        active_booked = db.session.query(db.func.sum(Booking.seats_booked))\
            .filter(Booking.trek_id == trek.id, Booking.status == 'Confirmed').scalar() or 0
        trek.available_slots = max(0, trek.total_slots - int(active_booked))

    db.session.commit()
    invalidate_treks_cache()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Status updated to {status} for {trek.name}.', 'trek': trek.to_dict()}), 200


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@approved_staff_required
def get_participants(trek_id):
    staff = _get_current_staff()
    trek = db.session.get(Trek, trek_id)
    if not trek or trek.assigned_staff_id != staff.id:
        return jsonify({'error': 'Trek not found or not assigned to you.'}), 404

    bookings = Booking.query.filter_by(trek_id=trek.id).order_by(Booking.booking_date.asc()).all()
    roster = []
    for b in bookings:
        u = b.user
        roster.append({
            'booking_id': b.id,
            'trekker_name': u.name if u else 'N/A',
            'email': u.email if u else 'N/A',
            'phone': u.phone if u else 'N/A',
            'seats_booked': b.seats_booked,
            'status': b.status,
            'booking_date': b.booking_date.strftime('%Y-%m-%d %H:%M') if b.booking_date else 'N/A'
        })

    return jsonify({
        'trek_id': trek.id,
        'trek_name': trek.name,
        'total_slots': trek.total_slots,
        'available_slots': trek.available_slots,
        'participants_count': len([b for b in roster if b['status'] == 'Confirmed']),
        'roster': roster
    }), 200


@staff_bp.route('/treks/<int:trek_id>/send-reminder', methods=['POST'])
@approved_staff_required
def send_trek_reminder(trek_id):
    """
    Allows assigned staff guide to send reminders / custom alerts to their participants
    ('turant bhej sake' / 'baad me bhi bhej sake' / 'khud bhi bhej sake').
    """
    staff = _get_current_staff()
    trek = db.session.get(Trek, trek_id)
    if not trek or trek.assigned_staff_id != staff.id:
        return jsonify({'error': 'Trek not found or not assigned to you.'}), 404

    data = request.get_json() or {}
    subject = data.get('subject', f"Guide Update: {trek.name}").strip()
    message = data.get('message', '').strip()
    channel = data.get('channel', 'Email').strip()
    dispatch_type = data.get('dispatch_type', 'Instant').strip()
    scheduled_for = data.get('scheduled_for', '').strip() if dispatch_type == 'Scheduled Later' else None

    if not message:
        return jsonify({'error': 'Message content is required.'}), 400

    result = send_custom_notification(
        trek_id=trek.id,
        subject=subject,
        message=message,
        channel=channel,
        dispatch_type=dispatch_type,
        scheduled_for=scheduled_for,
        sent_by=f"Guide {staff.name}"
    )
    return jsonify(result), 200


