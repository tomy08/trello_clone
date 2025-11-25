from src.db import db


class Board(db.Model):
    __tablename__ = "boards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    todo = db.Column(db.ARRAY(db.String), nullable=True)
    doing = db.Column(db.ARRAY(db.String), nullable=True)
    done = db.Column(db.ARRAY(db.String), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User")

    def __repr__(self):
        return f"<Board {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }
