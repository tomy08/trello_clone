from src.db import db
from datetime import datetime


class BoardMember(db.Model):
    __tablename__ = "board_members"
    __table_args__ = (
        db.UniqueConstraint("board_id", "user_id", name="unique_board_member"),
    )

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    board = db.relationship("Board")
    user = db.relationship("User")

    def __repr__(self):
        return f"<BoardMember Board ID: {self.board_id}, User ID: {self.user_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "board_id": self.board_id,
            "user_id": self.user_id,
        }
