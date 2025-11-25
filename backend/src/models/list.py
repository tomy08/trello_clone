from src.db import db
from datetime import datetime


class List(db.Model):
    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    cards = db.relationship("Card", back_populates="list", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<List ID: {self.id}, Title: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "board_id": self.board_id,
            "position": self.position,
            "cards": [card.to_dict() for card in self.cards],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
