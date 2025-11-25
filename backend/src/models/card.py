from src.db import db
from datetime import datetime


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    list = db.relationship("List", back_populates="cards")

    def __repr__(self):
        return f"<Card ID: {self.id}, Title: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "list_id": self.list_id,
            "position": self.position,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "archived": self.archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
