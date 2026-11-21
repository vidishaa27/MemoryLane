from app.extensions import db

class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    magazine_id = db.Column(db.Integer, db.ForeignKey("magazines.id"), nullable=False)
    page_number = db.Column(db.Integer)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    image_url = db.Column(db.Text)
    spotify_link = db.Column(db.Text)

    __table_args__ = (
        db.Index("idx_pages_magazine_id", "magazine_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "magazine_id": self.magazine_id,
            "page_number": self.page_number,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "spotify_link": self.spotify_link
        }
