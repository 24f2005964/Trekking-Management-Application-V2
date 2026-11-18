from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, StaffProfile

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    role = data.get('role', 'user').strip().lower()

    if not email or not password or not name:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    if role == 'admin':
        return jsonify({'error': 'Self-registration as Admin is prohibited.'}), 403

    if role not in ['user', 'staff']:
        role = 'user'

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists.'}), 409

    # Only Admin is pre-approved in the system.
    # No user is auto-approved upon registration; Staff strictly requires Admin approval.
    is_approved = False

    user = User(
        name=name,
        email=email,
        phone=phone or None,
        role=role,
        is_approved=is_approved,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == 'staff':
        profile = StaffProfile(
            user_id=user.id,
            bio=data.get('bio', 'Trek coordinator applicant'),
            emergency_contact=data.get('emergency_contact', ''),
            experience_years=int(data.get('experience_years', 1)),
            certification=data.get('certification', '')
        )
        db.session.add(profile)

    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Registration successful.',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    if not user.is_active:
        return jsonify({'error': 'Your account has been deactivated or blacklisted. Contact Admin.'}), 403

    if user.role == 'staff' and not user.is_approved:
        return jsonify({'error': 'Staff account pending Admin approval. Please contact administrator.'}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful.',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) if user_id else None
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out successfully.'}), 200

