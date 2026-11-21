from flask import Blueprint, request, session
from app.extensions import db
from app.models.magazine import Magazine
from app.models.page import Page
from app.utils.sanitizer import sanitize_text

magazines_bp = Blueprint("magazines", __name__)

@magazines_bp.route("/magazines", methods=["GET"])
def get_magazines():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "Login required."
        }, 401

    magazines = Magazine.query.filter_by(user_id=user_id).order_by(Magazine.id.desc()).all()
    return {
        "magazines": [m.to_dict() for m in magazines]
    }

@magazines_bp.route("/magazines", methods=["POST"])
def create_magazine():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "Login required."
        }, 401

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")

    if not title:
        return {
            "message": "Magazine title is required."
        }, 400

    clean_title = sanitize_text(title)
    clean_description = sanitize_text(description or "")

    new_magazine = Magazine(
        user_id=user_id,
        title=clean_title,
        description=clean_description
    )
    db.session.add(new_magazine)
    db.session.commit()

    return {
        "message": "Magazine created successfully!",
        "id": new_magazine.id
    }, 201

@magazines_bp.route("/magazine/<int:magazine_id>", methods=["DELETE"])
def delete_magazine(magazine_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    magazine = Magazine.query.filter_by(id=magazine_id, user_id=user_id).first()
    if magazine is None:
        return {
            "message": "Magazine not found."
        }, 404

    # Delete all pages for this magazine, then delete the magazine
    Page.query.filter_by(magazine_id=magazine_id).delete()
    db.session.delete(magazine)
    db.session.commit()

    return {
        "message": "Magazine deleted successfully!"
    }, 200

@magazines_bp.route("/stats", methods=["GET"])
def get_stats():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    magazine_count = Magazine.query.filter_by(user_id=user_id).count()

    page_count = db.session.query(Page).join(
        Magazine, Page.magazine_id == Magazine.id
    ).filter(Magazine.user_id == user_id).count()

    song_count = db.session.query(Page).join(
        Magazine, Page.magazine_id == Magazine.id
    ).filter(
        Magazine.user_id == user_id,
        Page.spotify_link.isnot(None),
        Page.spotify_link != ""
    ).count()

    return {
        "magazines": magazine_count,
        "pages": page_count,
        "songs": song_count
    }, 200
