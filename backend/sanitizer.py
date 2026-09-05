import re
import bleach
from urllib.parse import urlparse

# Allowed HTML tags for Quill rich-text content
ALLOWED_QUILL_TAGS = [
    'p', 'br', 'h1', 'h2', 'h3', 'strong', 'b', 'em', 'i', 'u',
    'ul', 'ol', 'li', 'a', 'span'
]

# Allowed attributes for Quill rich-text content
ALLOWED_QUILL_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'span': ['class'],
    'p': ['class'],
    'h1': ['class'],
    'h2': ['class'],
    'h3': ['class'],
    'ul': ['class'],
    'ol': ['class'],
    'li': ['class'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def sanitize_text(text: str) -> str:
    """
    Sanitizes plain-text fields (magazine title, description, page title).
    Strips all HTML markup and script/style text content, returning clean plain text.
    """
    if not text:
        return ""

    # Strip script and style blocks entirely along with their content
    cleaned = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'<style.*?>.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Strip remaining HTML tags
    sanitized = bleach.clean(cleaned, tags=[], strip=True)
    return sanitized.strip()

def sanitize_html(html_content: str) -> str:
    """
    Sanitizes rich-text HTML content from Quill editor.
    Preserves legitimate formatting while removing scripts, dangerous tags, and event handlers.
    """
    if not html_content:
        return ""

    # Strip script and style blocks entirely along with their content
    cleaned = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'<style.*?>.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Use Bleach with explicit tag/attribute allowlist
    sanitized = bleach.clean(
        cleaned,
        tags=ALLOWED_QUILL_TAGS,
        attributes=ALLOWED_QUILL_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    return sanitized.strip()

def sanitize_url(url: str) -> str:
    """
    Validates and sanitizes image_url and spotify_link fields.
    Rejects javascript:, data:, vbscript: and non-HTTP(S) dangerous schemes.
    """
    if not url:
        return ""

    cleaned_url = url.strip()

    # Reject dangerous protocols explicitly
    lower_url = cleaned_url.lower()
    if (lower_url.startswith("javascript:") or
        lower_url.startswith("data:") or
        lower_url.startswith("vbscript:")):
        return ""

    parsed = urlparse(cleaned_url)

    # Allow relative URLs (like /static/image.png) or standard HTTP/HTTPS schemes
    if parsed.scheme == "" or parsed.scheme in ["http", "https"]:
        return cleaned_url

    return ""
