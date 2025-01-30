from app.extensions import db, bcrypt
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .relationships import user_plant_likes, user_plant_mylist
from typing import List

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str]

    liked_plants = db.relationship('Plant', secondary=user_plant_likes, back_populates='liked_by')
    saved_plants = db.relationship(
        'Plant',
        secondary=user_plant_mylist,
        back_populates='saved_by_users',
        lazy='dynamic'
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


    @classmethod
    def from_dict(cls, user_data):
        user = cls(
            username=user_data["username"],
            email=user_data["email"]
        )
        user.set_password(user_data["password"])
        return user
