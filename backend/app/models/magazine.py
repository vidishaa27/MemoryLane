from app.extensions import db

class Magazine(db.Model):
    __tablename__ = "magazines"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    pages = db.relationship("Page", backref="magazine", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        db.Index("idx_magazines_user_id", "user_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description
        }
