import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify, send_file, current_app
from app.extensions import db, cache
from app.models import User, StaffProfile, Trek, Booking, ReminderConfig, NotificationLog
from app.utils.decorators import admin_required
from app.utils.cache import invalidate_dashboard_cache, invalidate_treks_cache
from app.tasks.scheduled import generate_monthly_report, send_daily_reminders, send_custom_notification, post_to_google_chat
from app.services.email_service import dispatch_email_message

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='cache:admin:dashboard')
def dashboard():
    total_treks = Trek.query.count()
    open_treks = Trek.query.filter_by(status='Open').count()
    completed_treks = Trek.query.filter_by(status='Completed').count()

    total_trekkers = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    pending_staff = User.query.filter_by(role='staff', is_approved=False).count()
    approved_staff = User.query.filter_by(role='staff', is_approved=True).count()

    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status='Confirmed').count()
    cancelled_bookings = Booking.query.filter_by(status='Cancelled').count()

    # Calculate total capacity and seats booked
    total_capacity = db.session.query(db.func.sum(Trek.total_slots)).scalar() or 0
    available_capacity = db.session.query(db.func.sum(Trek.available_slots)).scalar() or 0

    return jsonify({
        'counts': {
            'total_treks': total_treks,
            'open_treks': open_treks,
            'completed_treks': completed_treks,
            'total_trekkers': total_trekkers,
            'total_staff': total_staff,
            'pending_staff': pending_staff,
            'approved_staff': approved_staff,
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_capacity': total_capacity,
            'available_capacity': available_capacity
        }
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    role_filter = request.args.get('role')
    search = request.args.get('q', '').strip()

    query = User.query
    if role_filter and role_filter != 'all':
        query = query.filter_by(role=role_filter)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(db.or_(User.name.ilike(search_pattern), User.email.ilike(search_pattern)))

    users = query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@admin_bp.route('/users/<int:user_id>/approve', methods=['PUT'])
@admin_required
def approve_staff(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if user.role != 'staff':
        return jsonify({'error': 'Only staff accounts can be approved.'}), 400

    user.is_approved = True
    db.session.commit()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Staff member {user.name} approved successfully.', 'user': user.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@admin_required
def toggle_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if user.role == 'admin':
        return jsonify({'error': 'Administrator account cannot be deactivated.'}), 403

    user.is_active = not user.is_active
    db.session.commit()
    invalidate_dashboard_cache()

    status_str = 'activated' if user.is_active else 'deactivated / blacklisted'
    return jsonify({'message': f'User {user.name} has been {status_str}.', 'user': user.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if user.role == 'admin':
        return jsonify({'error': 'Administrator account cannot be deleted.'}), 403

    user_name = user.name

    # If trekker, release slots from confirmed bookings
    if user.bookings:
        for b in user.bookings:
            if b.status == 'Confirmed' and b.trek:
                b.trek.available_slots = min(b.trek.total_slots, b.trek.available_slots + b.seats_booked)
                if b.trek.status == 'Closed' and b.trek.available_slots > 0:
                    b.trek.status = 'Open'

    # If staff, unassign from treks
    if user.assigned_treks:
        for t in user.assigned_treks:
            t.assigned_staff_id = None

    db.session.delete(user)
    db.session.commit()

    invalidate_dashboard_cache()
    invalidate_treks_cache()

    return jsonify({'message': f'User {user_name} has been permanently deleted.'}), 200


@admin_bp.route('/staff', methods=['POST'])
@admin_required
def add_staff():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    password = data.get('password', 'staff123')
    phone = data.get('phone', '').strip()

    if not email or not name:
        return jsonify({'error': 'Email and Name are required.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists.'}), 409

    staff_user = User(
        name=name,
        email=email,
        phone=phone or None,
        role='staff',
        is_approved=True,  # Directly created by admin, auto-approved
        is_active=True
    )
    staff_user.set_password(password)
    db.session.add(staff_user)
    db.session.flush()

    profile = StaffProfile(
        user_id=staff_user.id,
        bio=data.get('bio', 'Trek coordinator added by Admin'),
        emergency_contact=data.get('emergency_contact', ''),
        experience_years=int(data.get('experience_years', 2)),
        certification=data.get('certification', '')
    )
    db.session.add(profile)
    db.session.commit()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Staff member {name} added successfully.', 'user': staff_user.to_dict()}), 201


@admin_bp.route('/treks', methods=['GET'])
@admin_required
def get_treks():
    treks = Trek.query.order_by(Trek.start_date.asc()).all()
    return jsonify({'treks': [t.to_dict() for t in treks]}), 200


@admin_bp.route('/treks', methods=['POST'])
@admin_required
def create_trek():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    location = data.get('location', '').strip()
    difficulty = data.get('difficulty', 'Moderate')
    duration_days = int(data.get('duration_days', 1))
    total_slots = int(data.get('total_slots', 20))
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not name or not location or not start_date_str or not end_date_str:
        return jsonify({'error': 'Trek name, location, start date, and end date are required.'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if end_date < start_date:
        return jsonify({'error': 'End date cannot be earlier than start date.'}), 400

    assigned_staff_id = data.get('assigned_staff_id')
    if assigned_staff_id:
        assigned_staff_id = int(assigned_staff_id)

    trek = Trek(
        name=name,
        description=data.get('description', ''),
        location=location,
        difficulty=difficulty,
        duration_days=duration_days,
        total_slots=total_slots,
        available_slots=total_slots,
        start_date=start_date,
        end_date=end_date,
        status=data.get('status', 'Open'),
        assigned_staff_id=assigned_staff_id
    )

    db.session.add(trek)
    db.session.commit()
    invalidate_treks_cache()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Trek {name} created successfully.', 'trek': trek.to_dict()}), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@admin_required
def update_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found.'}), 404

    data = request.get_json() or {}
    if 'name' in data:
        trek.name = data['name'].strip()
    if 'description' in data:
        trek.description = data['description']
    if 'location' in data:
        trek.location = data['location'].strip()
    if 'difficulty' in data:
        trek.difficulty = data['difficulty']
    if 'duration_days' in data:
        trek.duration_days = int(data['duration_days'])
    if 'status' in data:
        new_status = data['status']
        if new_status in ['Open', 'Closed', 'Completed']:
            trek.status = new_status
            if new_status == 'Closed':
                trek.available_slots = 0
            elif new_status == 'Completed':
                trek.available_slots = 0
                Booking.query.filter_by(trek_id=trek.id, status='Confirmed').update({'status': 'Completed'})
            elif new_status == 'Open':
                active_booked = db.session.query(db.func.sum(Booking.seats_booked))\
                    .filter(Booking.trek_id == trek.id, Booking.status == 'Confirmed').scalar() or 0
                trek.available_slots = max(0, trek.total_slots - int(active_booked))
    if 'assigned_staff_id' in data:
        trek.assigned_staff_id = int(data['assigned_staff_id']) if data['assigned_staff_id'] else None

    if 'start_date' in data:
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    if 'total_slots' in data:
        new_total = int(data['total_slots'])
        active_bookings = db.session.query(db.func.sum(Booking.seats_booked))\
            .filter_by(trek_id=trek.id, status='Confirmed').scalar() or 0
        if new_total < int(active_bookings):
            return jsonify({
                'error': f'Cannot reduce total capacity to {new_total}. There are already {active_bookings} active booking(s).'
            }), 400
        diff = new_total - trek.total_slots
        trek.total_slots = new_total
        trek.available_slots = max(0, trek.available_slots + diff)

    db.session.commit()
    invalidate_treks_cache()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Trek {trek.name} updated successfully.', 'trek': trek.to_dict()}), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@admin_required
def delete_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found.'}), 404

    name = trek.name
    db.session.delete(trek)
    db.session.commit()
    invalidate_treks_cache()
    invalidate_dashboard_cache()

    return jsonify({'message': f'Trek {name} deleted successfully.'}), 200


@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['PUT'])
@admin_required
def assign_staff(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found.'}), 404

    data = request.get_json() or {}
    staff_id = data.get('staff_id')

    if staff_id:
        staff = db.session.get(User, int(staff_id))
        if not staff or staff.role != 'staff':
            return jsonify({'error': 'Assigned user must be a registered Staff member.'}), 400
        if not staff.is_approved:
            return jsonify({'error': 'Assigned staff must be approved.'}), 400
        trek.assigned_staff_id = staff.id
    else:
        trek.assigned_staff_id = None

    db.session.commit()
    invalidate_treks_cache()
    invalidate_dashboard_cache()

    return jsonify({'message': 'Staff assigned successfully.', 'trek': trek.to_dict()}), 200


@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


@admin_bp.route('/reports/generate', methods=['POST'])
@admin_required
def generate_report_now():
    """
    On-demand execution of the monthly activity report generator (PDF + HTML).
    """
    result = generate_monthly_report()
    pdf_file = result.get('pdf_file')
    return jsonify({
        'message': 'Monthly trekking activity report generated successfully in PDF format.',
        'details': result,
        'pdf_file': pdf_file,
        'download_url': f'/api/v1/admin/reports/download/{pdf_file}' if pdf_file else None
    }), 200


@admin_bp.route('/reports/download/<filename>', methods=['GET'])
@admin_required
def download_report_file(filename):
    """
    Direct authenticated download of a generated monthly PDF or HTML report.
    """
    export_folder = current_app.config.get('EXPORT_FOLDER', './exports')
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(export_folder, safe_filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Report file not found.'}), 404

    mimetype = 'application/pdf' if safe_filename.endswith('.pdf') else 'text/html'
    return send_file(
        os.path.abspath(file_path),
        as_attachment=True,
        download_name=safe_filename,
        mimetype=mimetype
    )


@admin_bp.route('/reports/download-latest-pdf', methods=['GET'])
@admin_required
def download_latest_pdf():
    """
    Generates and immediately streams the latest monthly report as a PDF attachment.
    """
    result = generate_monthly_report()
    export_folder = current_app.config.get('EXPORT_FOLDER', './exports')
    pdf_file = str(result.get('pdf_file', ''))
    file_path = os.path.join(export_folder, pdf_file)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Could not locate generated PDF report.'}), 500

    return send_file(
        os.path.abspath(file_path),
        as_attachment=True,
        download_name=pdf_file,
        mimetype='application/pdf'
    )


@admin_bp.route('/reports/list', methods=['GET'])
@admin_required
def list_generated_reports():
    """
    Lists available generated monthly reports in the exports directory.
    """
    export_folder = current_app.config.get('EXPORT_FOLDER', './exports')
    os.makedirs(export_folder, exist_ok=True)
    files = []
    for fname in os.listdir(export_folder):
        if fname.endswith(('.pdf', '.html')) and fname.startswith('monthly_report_'):
            fpath = os.path.join(export_folder, fname)
            files.append({
                'filename': fname,
                'type': 'PDF' if fname.endswith('.pdf') else 'HTML',
                'size_bytes': os.path.getsize(fpath),
                'created_at': datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S'),
                'download_url': f'/api/v1/admin/reports/download/{fname}'
            })
    files.sort(key=lambda x: x['filename'], reverse=True)
    return jsonify({'reports': files}), 200


# =============================================================================
# TREK REMINDER & NOTIFICATION SCHEDULER (Instant / Schedule Later / Custom)
# =============================================================================

@admin_bp.route('/reminders/config', methods=['GET'])
@admin_required
def get_reminder_config():
    """
    Get current automated daily reminder schedule settings.
    """
    config = ReminderConfig.query.first()
    if not config:
        config = ReminderConfig(
            scheduled_time='08:00',
            days_before=2,
            channel='Email',
            webhook_url='',
            is_active=True
        )
        db.session.add(config)
        db.session.commit()
    return jsonify({'config': config.to_dict()}), 200


@admin_bp.route('/reminders/config', methods=['PUT'])
@admin_required
def update_reminder_config():
    """
    Edit and save the automated reminder schedule:
    - scheduled_time (HH:MM)
    - days_before (threshold days before trek)
    - channel (Email / Webhook / Email & Webhook / SMS)
    - webhook_url (Google Chat webhook)
    - is_active (toggle scheduler active/paused)
    """
    data = request.get_json() or {}
    config = ReminderConfig.query.first()
    if not config:
        config = ReminderConfig()
        db.session.add(config)

    if 'scheduled_time' in data:
        config.scheduled_time = str(data['scheduled_time']).strip()
    if 'days_before' in data:
        config.days_before = max(1, int(data['days_before']))
    if 'channel' in data:
        config.channel = str(data['channel']).strip()
    if 'webhook_url' in data:
        config.webhook_url = str(data['webhook_url']).strip()
    if 'is_active' in data:
        config.is_active = bool(data['is_active'])
    if 'smtp_enabled' in data:
        config.smtp_enabled = bool(data['smtp_enabled'])
    if 'smtp_host' in data:
        config.smtp_host = str(data['smtp_host']).strip()
    if 'smtp_port' in data:
        config.smtp_port = int(data['smtp_port'])
    if 'smtp_user' in data:
        config.smtp_user = str(data['smtp_user']).strip()
    if 'smtp_pass' in data and data['smtp_pass']:
        config.smtp_pass = str(data['smtp_pass']).strip()
    if 'smtp_from' in data:
        config.smtp_from = str(data['smtp_from']).strip()

    db.session.commit()
    return jsonify({
        'message': 'Reminder schedule updated successfully.',
        'config': config.to_dict()
    }), 200


@admin_bp.route('/reminders/send-now', methods=['POST'])
@admin_required
def trigger_reminders_now():
    """
    'Turant bhej sake' — Instant dispatch of upcoming trek reminders.
    Scans upcoming treks and immediately delivers reminders to all confirmed trekkers.
    """
    result = send_daily_reminders(force=True, trigger_source='Admin Instant Dispatch')
    sent_count = result.get('reminders_sent', 0)
    return jsonify({
        'message': f"Immediate reminder dispatch completed: {sent_count} reminder(s) delivered.",
        'details': result,
        'reminders_sent': sent_count,
        'gchat_status': result.get('gchat_status'),
        'smtp_status': result.get('smtp_status'),
        'webhook_configured': result.get('webhook_configured', False),
        'smtp_configured': result.get('smtp_configured', False)
    }), 200


@admin_bp.route('/reminders/custom', methods=['POST'])
@admin_required
def send_custom_reminder():
    """
    'Khud bhi bhej sake' / 'Baad me bhi bhej sake':
    Manual creation of a custom reminder / notice with custom instructions.
    Can be dispatched immediately ('Instant') or scheduled for later ('Scheduled Later').
    """
    data = request.get_json() or {}
    trek_id = data.get('trek_id')
    if trek_id:
        trek_id = int(trek_id)

    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()
    channel = data.get('channel', 'Email').strip()
    dispatch_type = data.get('dispatch_type', 'Instant').strip() # 'Instant' or 'Scheduled Later'
    scheduled_for = data.get('scheduled_for', '').strip() if dispatch_type == 'Scheduled Later' else None

    if not subject or not message:
        return jsonify({'error': 'Subject and message body are required.'}), 400

    result = send_custom_notification(
        trek_id=trek_id,
        subject=subject,
        message=message,
        channel=channel,
        dispatch_type=dispatch_type,
        scheduled_for=scheduled_for,
        sent_by='Administrator'
    )

    if result.get('status') == 'error':
        return jsonify({'error': result.get('message')}), 400

    return jsonify(result), 200


@admin_bp.route('/reminders/logs', methods=['GET'])
@admin_required
def get_reminder_logs():
    """
    Fetches history of sent and scheduled reminders / notifications.
    """
    logs = NotificationLog.query.order_by(NotificationLog.created_at.desc()).limit(50).all()
    return jsonify({'logs': [l.to_dict() for l in logs]}), 200


@admin_bp.route('/reminders/test-webhook', methods=['POST'])
@admin_required
def test_google_chat_webhook():
    """
    Sends a test ping to the configured Google Chat webhook URL.
    """
    data = request.get_json() or {}
    webhook_url = data.get('webhook_url', '').strip()
    if not webhook_url:
        config = ReminderConfig.query.first()
        webhook_url = config.webhook_url if config else ''

    if not webhook_url:
        return jsonify({'error': 'No Google Chat webhook URL provided or configured.'}), 400

    test_msg = (
        "🏔️ *TMA V2 — Google Chat Webhook Test*\n"
        "Connection successful! Automated daily reminders and notifications are configured."
    )
    res = post_to_google_chat(webhook_url, test_msg)
    if res.get('success'):
        return jsonify({'message': 'Webhook test ping delivered successfully to Google Chat Space!'}), 200
    else:
        err = res.get('error', 'Unknown network error')
        return jsonify({'error': f"Webhook ping failed: {err}. Please verify the Webhook URL."}), 400


@admin_bp.route('/reminders/test-live-email', methods=['POST'])
@admin_required
def test_live_email():
    """
    Test sending a real email via SMTP to any specified email inbox.
    """
    data = request.get_json() or {}
    target_email = data.get('email', '').strip()
    if not target_email or '@' not in target_email:
        return jsonify({'error': 'A valid recipient email address is required.'}), 400

    config = ReminderConfig.query.first()
    if not config or not config.smtp_enabled:
        return jsonify({'error': 'Live SMTP is currently disabled. Please enable it and provide SMTP credentials below.'}), 400

    res = dispatch_email_message(
        recipient_email=target_email,
        recipient_name='TMA Tester',
        subject='[TEST] TMA TrekSync Real Email Test',
        message=(
            'Congratulations! Your TMA V2 SMTP live email dispatch is working perfectly.\n\n'
            'Users and trekkers will now receive notifications directly in their real external inboxes (e.g. Gmail).'
        ),
        sender='TMA V2 Operations'
    )

    if res.get('smtp_sent'):
        return jsonify({
            'message': f"Test email successfully dispatched to {target_email}!",
            'details': res
        }), 200
    else:
        err = res.get('smtp_error') or 'Unknown SMTP error'
        return jsonify({
            'error': f"Failed to deliver email over SMTP: {err}. Please check your SMTP host, port, and App Password.",
            'details': res
        }), 400


@admin_bp.route('/reminders/sent-emails', methods=['GET'])
@admin_required
def list_sent_emails():
    """
    List all dispatched email reminder files from the server archive.
    """
    logs_dir = current_app.config.get('EXPORT_FOLDER', './exports')
    reminders_dir = os.path.join(logs_dir, 'email_reminders')
    os.makedirs(reminders_dir, exist_ok=True)

    email_files = []
    for fname in os.listdir(reminders_dir):
        if fname.endswith('.txt'):
            fpath = os.path.join(reminders_dir, fname)
            snippet = ""
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    snippet = f.read(500)
            except Exception:
                pass
            email_files.append({
                'filename': fname,
                'snippet': snippet,
                'created_at': datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S'),
                'size_bytes': os.path.getsize(fpath)
            })

    email_files.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'emails': email_files[:50]}), 200


@admin_bp.route('/reminders/sent-emails/<path:filename>', methods=['GET'])
@admin_required
def get_sent_email_content(filename):
    """
    View the full content of an individual sent email text file.
    """
    logs_dir = current_app.config.get('EXPORT_FOLDER', './exports')
    reminders_dir = os.path.join(logs_dir, 'email_reminders')
    safe_filename = os.path.basename(filename)
    fpath = os.path.join(reminders_dir, safe_filename)
    if not os.path.exists(fpath):
        return jsonify({'error': 'Email archive file not found.'}), 404

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    return jsonify({'filename': safe_filename, 'content': content}), 200


