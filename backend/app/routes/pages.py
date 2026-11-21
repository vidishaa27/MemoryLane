from flask import Blueprint, request, session
from app.extensions import db
from app.models.magazine import Magazine
from app.models.page import Page
from app.models import resequence_pages
from app.utils.sanitizer import sanitize_text, sanitize_html, sanitize_url

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/pages", methods=["POST"])
def add_page():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    data = request.get_json() or {}
    magazine_id = data.get("magazine_id")
    if not magazine_id:
        return {
            "message": "Magazine ID is required."
        }, 400

    magazine = Magazine.query.filter_by(id=magazine_id, user_id=user_id).first()
    if magazine is None:
        return {
            "message": "Magazine not found."
        }, 404

    resequence_pages(magazine_id)

    max_num = db.session.query(db.func.max(Page.page_number)).filter_by(
        magazine_id=magazine_id
    ).scalar()
    next_page_number = (max_num + 1) if max_num is not None else 1

    clean_title = sanitize_text(data.get("title", ""))
    clean_content = sanitize_html(data.get("content", ""))
    clean_image_url = sanitize_url(data.get("image_url", ""))
    clean_spotify_link = sanitize_url(data.get("spotify_link", ""))

    new_page = Page(
        magazine_id=magazine_id,
        page_number=next_page_number,
        title=clean_title,
        content=clean_content,
        image_url=clean_image_url,
        spotify_link=clean_spotify_link
    )
    db.session.add(new_page)
    db.session.commit()

    resequence_pages(magazine_id)
    db.session.commit()

    return {
        "message": "Page added successfully!"
    }, 201

@pages_bp.route("/pages/<int:magazine_id>", methods=["GET"])
def get_pages(magazine_id):
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

    pages = Page.query.filter_by(magazine_id=magazine_id).order_by(
        Page.page_number.asc()
    ).all()

    return {
        "pages": [p.to_dict() for p in pages]
    }

@pages_bp.route("/page/<int:page_id>", methods=["GET"])
def get_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    page = db.session.get(Page, page_id)
    if page is None:
        return {
            "message": "Page not found."
        }, 404

    magazine = Magazine.query.filter_by(id=page.magazine_id, user_id=user_id).first()
    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    return page.to_dict(), 200

@pages_bp.route("/page/<int:page_id>", methods=["PUT"])
def update_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    page = db.session.get(Page, page_id)
    if page is None:
        return {
            "message": "Page not found."
        }, 404

    magazine = Magazine.query.filter_by(id=page.magazine_id, user_id=user_id).first()
    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    data = request.get_json() or {}
    page.title = sanitize_text(data.get("title", ""))
    page.content = sanitize_html(data.get("content", ""))
    page.image_url = sanitize_url(data.get("image_url", ""))
    page.spotify_link = sanitize_url(data.get("spotify_link", ""))

    db.session.commit()

    return {
        "message": "Page updated successfully!"
    }, 200

@pages_bp.route("/page/<int:page_id>", methods=["DELETE"])
def delete_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    page = db.session.get(Page, page_id)
    if page is None:
        return {
            "message": "Page not found."
        }, 404

    magazine = Magazine.query.filter_by(id=page.magazine_id, user_id=user_id).first()
    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    magazine_id = page.magazine_id
    db.session.delete(page)
    db.session.commit()

    resequence_pages(magazine_id)
    db.session.commit()

    return {
        "message": "Page deleted successfully!"
    }, 200

@pages_bp.route("/page/<int:page_id>/move", methods=["PUT"])
def move_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    data = request.get_json() or {}
    direction = data.get("direction")

    if direction not in ["up", "down"]:
        return {
            "message": "Invalid direction."
        }, 400

    page = db.session.get(Page, page_id)
    if page is None:
        return {
            "message": "Page not found."
        }, 404

    magazine = Magazine.query.filter_by(id=page.magazine_id, user_id=user_id).first()
    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    resequence_pages(magazine.id)
    db.session.commit()

    # Refresh page instance after resequencing
    page = db.session.get(Page, page_id)

    if direction == "up":
        neighbor = Page.query.filter(
            Page.magazine_id == magazine.id,
            Page.page_number < page.page_number
        ).order_by(Page.page_number.desc()).first()
    else:
        neighbor = Page.query.filter(
            Page.magazine_id == magazine.id,
            Page.page_number > page.page_number
        ).order_by(Page.page_number.asc()).first()

    if neighbor is None:
        return {
            "message": "Cannot move further."
        }, 400

    page.page_number, neighbor.page_number = neighbor.page_number, page.page_number
    db.session.commit()

    resequence_pages(magazine.id)
    db.session.commit()

    return {
        "message": "Page moved successfully!"
    }, 200
