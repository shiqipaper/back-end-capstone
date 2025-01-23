from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
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
    return jsonify(plant.to_detail_dict()), 200

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
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    plant = db.session.get(Plant, plant_id)

    if not plant:
        return jsonify({'error': 'Plant not found'}), 404

    if plant in user.liked_plants:
        user.liked_plants.remove(plant)
        message = "Plant unliked successfully"
    else:
        user.liked_plants.append(plant)
        message = "Plant liked successfully"

    db.session.commit()
    return jsonify({'message': message, 'likes_count': len(plant.users)}), 200

@plants_bp.post("/<plant_id>/save")
@jwt_required()
@cross_origin()
def save_plant(plant_id):
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    plant = db.session.get(Plant, plant_id)

    if not plant:
        return jsonify({'error': 'Plant not found'}), 404

    if plant in user.saved_plants:
        user.saved_plants.remove(plant)
        message = "Plant removed from My List"
    else:
        user.saved_plants.append(plant)
        message = "Plant saved to My List"

    db.session.commit()
    return jsonify({'message': message, 'saved_count': len(plant.saved_by_users)}), 200
