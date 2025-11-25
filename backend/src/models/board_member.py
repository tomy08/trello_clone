from src.db import db


class BoardMember(db.Model):
    __tablename__ = "board_members"

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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
