from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .relationships import user_plant_likes, user_plant_mylist
from typing import List, Optional

from ..s3_helper import generate_s3_url


class Plant(db.Model):
    __tablename__ = 'plants'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str]
    main_image_url: Mapped[Optional[str]]

    users = db.relationship('User', secondary=user_plant_likes, back_populates='liked_plants')
    saved_by_users = db.relationship('User', secondary=user_plant_mylist, back_populates='saved_plants')
    images: Mapped[List["PlantImage"]] = relationship(back_populates="plant", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(back_populates="plant", cascade="all, delete-orphan")

    def to_list_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'main_image_url': generate_s3_url(self.main_image_url) if self.main_image_url else None,
            'likes_count': len(self.users)
        }

    def to_detail_dict(self):
        main_image = {'id': 0, 'image_url': generate_s3_url(self.main_image_url)} if self.main_image_url else None
        all_images = [main_image] + [image.to_dict() for image in self.images] if main_image else self.images
        all_images.sort(key=lambda img: img['id'])
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'likes_count': len(self.users),
            'saved_count': len(self.saved_by_users),
            'images': all_images,
            'comments': [comment.to_dict() for comment in self.comments]
        }

    @classmethod
    def from_dict(cls, plant_data):
        return cls(
            name=plant_data["name"],
            description=plant_data["description"],
            main_image_url=plant_data.get("main_image_url")
        )

class PlantImage(db.Model):
    __tablename__ = 'plant_images'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey('plants.id'))
    image_url: Mapped[str]

    plant: Mapped["Plant"] = relationship(back_populates="images")

    def to_dict(self):
        return {
            'id': self.id,
            'plant_id': self.plant_id,
            'image_url': generate_s3_url(self.image_url) if self.image_url else None
        }

    @classmethod
    def from_dict(cls, image_data):
        return cls(
            plant_id=image_data["plant_id"],
            image_url=image_data["image_url"]
        )
