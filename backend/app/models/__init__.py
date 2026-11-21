from app.extensions import db
from app.models.user import User
from app.models.magazine import Magazine
from app.models.page import Page

def resequence_pages(magazine_id):
    """
    Ensures page_number values for a magazine are strictly contiguous 1..N
    preserving the current page_number ASC, id ASC logical order.
    Executes within the active database session.
    """
    pages = Page.query.filter_by(magazine_id=magazine_id).order_by(
        Page.page_number.asc(),
        Page.id.asc()
    ).all()

    for index, page in enumerate(pages, start=1):
        page.page_number = index

    db.session.flush()

__all__ = ["User", "Magazine", "Page", "resequence_pages"]
