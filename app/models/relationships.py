from app.extensions import db

user_plant_likes = db.Table(
    'user_plant_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('plant_id', db.Integer, db.ForeignKey('plants.id'), primary_key=True)
)

user_plant_mylist = db.Table(
    'user_plant_mylist',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('plant_id', db.Integer, db.ForeignKey('plants.id'), primary_key=True)
)
