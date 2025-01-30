from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin
from app.extensions import db
from app.models.comment import Comment
from app.models.plant import Plant
from app.models.user import User
from .route_utilities import validate_model, create_model

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
    validate_model(Plant, plant_id)

    data = request.get_json()
    content = data.get('content')

    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

    if not content:
        return jsonify({"error": "Content is required"}), 400

    comment_data = {
        "content": content,
        "user_id": user_id,
        "plant_id": plant_id
    }
    return jsonify(create_model(Comment, comment_data)), 201

@plants_bp.get("/<plant_id>/comments")
@cross_origin()
def get_comments(plant_id):
    plant = validate_model(Plant, plant_id)
    return jsonify([comment.to_dict() for comment in plant.comments]), 200


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