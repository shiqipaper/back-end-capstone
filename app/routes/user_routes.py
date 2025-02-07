from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.extensions import db, bcrypt
from app.models.user import User
from .route_utilities import validate_model
from ..s3_helper import generate_s3_url

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

@users_bp.post("/register")
@cross_origin()
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    if db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'User registered successfully', 'access_token': access_token}), 201

@users_bp.post("/login")
@cross_origin()
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@users_bp.get("/profile")
@jwt_required()
@cross_origin()
def get_user_profile():
    try:
        current_user_id = int(get_jwt_identity())
        user = validate_model(User, current_user_id)
        return jsonify({'username': user.username, 'email': user.email}), 200
    except ValueError:
        return jsonify({'message': 'Invalid user ID'}), 400

@users_bp.put("/update")
@jwt_required()
@cross_origin()
def update_user_profile():
    try:
        current_user_id = int(get_jwt_identity())
        user = validate_model(User, current_user_id)

        data = request.get_json()
        if 'email' in data and data['email']:
            user.email = data['email']

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except ValueError:
        return jsonify({'message': 'Invalid user ID'}), 400


@users_bp.route('/saved-plants', methods=['GET'])
@jwt_required()
def get_saved_plants():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)

        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        # Use the dynamic query
        paginated_plants = user.saved_plants.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        plants_data = [{
            'id': plant.id,
            'name': plant.name,
            'main_image_url': generate_s3_url(plant.main_image_url) if plant.main_image_url else None,
            'likes_count': plant.liked_by.count(),  # Now using count() instead of len()
            'saves_count': plant.saved_by_users.count()
        } for plant in paginated_plants.items]

        return jsonify({
            'plants': plants_data,
            'total_pages': paginated_plants.pages,
            'current_page': paginated_plants.page,
            'total_items': paginated_plants.total
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
