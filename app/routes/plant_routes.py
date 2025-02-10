from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin
from app.extensions import db
from app.models.comment import Comment
from app.models.plant import Plant
from app.models.user import User
from .route_utilities import validate_model, create_model
from ..s3_helper import upload_file_to_s3

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

plants_bp = Blueprint("plants_bp", __name__, url_prefix="/plants")

@plants_bp.get("")
@cross_origin()
def get_homepage_plants():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '', type=str)

    query = db.select(Plant)
    if search_query:
        query = query.where(Plant.name.ilike(f'%{search_query}%'))

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return jsonify({
        'plants': [plant.to_list_dict() for plant in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@plants_bp.get("/<plant_id>")
@cross_origin()
def get_plant_details(plant_id):
    plant = validate_model(Plant, plant_id)
    return jsonify(plant.to_detail_dict(current_user=get_current_user())), 200

@plants_bp.post("/<plant_id>/comments")
@jwt_required()
@cross_origin()
def add_comment(plant_id):
    plant = validate_model(Plant, plant_id)
    content = request.form.get('content')
    image_file = request.files.get('image')

    if not content:
        return jsonify({"error": "Content is required"}), 400

    image_key = None
    if image_file:
        if not image_file.content_type.startswith('image/'):
            return jsonify({"error": "Invalid file type. Only images allowed"}), 400

        if request.content_length > MAX_FILE_SIZE + 1024:
            return jsonify({"error": "File size exceeds 5MB limit"}), 413
        image_key = upload_file_to_s3(image_file)
        if not image_key:
            return jsonify({"error": "Failed to upload image"}), 500

    user_id = get_jwt_identity()

    comment_data = {
        "content": content,
        "user_id": user_id,
        "plant_id": plant.id,
        "image_key": image_key  # Store just the key
    }

    return jsonify(create_model(Comment, comment_data)), 201


@plants_bp.get("/<plant_id>/comments")
@cross_origin()
def get_comments(plant_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    plant = validate_model(Plant, plant_id)
    comments_query = Comment.query.filter_by(plant_id=plant_id).order_by(Comment.created_at.desc())

    pagination = comments_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'comments': [comment.to_dict() for comment in pagination.items],
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'total_comments': pagination.total
    }), 200


@plants_bp.post("/<plant_id>/like")
@jwt_required()
@cross_origin()
def like_plant(plant_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 400

    plant = validate_model(Plant, plant_id)

    if plant in current_user.liked_plants:
        current_user.liked_plants.remove(plant)
        liked = False
    else:
        current_user.liked_plants.append(plant)
        liked = True

    db.session.commit()
    return jsonify({
        "liked": liked,
        "likes_count": plant.liked_by.count()
    }), 200


@plants_bp.post("/<plant_id>/save")
@jwt_required()
@cross_origin()
def save_plant(plant_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 400
    plant = validate_model(Plant, plant_id)

    if plant in current_user.saved_plants:
        current_user.saved_plants.remove(plant)
        saved = False
    else:
        current_user.saved_plants.append(plant)
        saved = True

    db.session.commit()
    return jsonify({
        "saved": saved,
        "saves_count": plant.saved_by_users.count()
    }), 200

def get_current_user():
    verify_jwt_in_request(optional=True)
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return None
    current_user = User.query.get(int(current_user_id))
    if not current_user:
        return None
    return current_user