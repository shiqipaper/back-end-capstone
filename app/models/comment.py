from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from app.s3_helper import generate_s3_url

class Comment(db.Model):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=db.func.current_timestamp())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    plant_id: Mapped[int] = mapped_column(ForeignKey('plants.id'))
    image_key = db.Column(db.String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="comments")
    plant: Mapped["Plant"] = relationship(back_populates="comments")

    def to_dict(self):
        return {
            'id': self.id,
            'plant_id': self.plant_id,
            'username': self.user.username,
            'content': self.content,
            'image_url': generate_s3_url(self.image_key) if self.image_key else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def from_dict(cls, comment_data):
        return cls(
            content=comment_data["content"],
            user_id=comment_data["user_id"],
            plant_id=comment_data["plant_id"],
            image_key=comment_data["image_key"]
        )
