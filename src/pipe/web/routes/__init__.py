"""Flask route blueprints for the web application.

This module organizes routes into separate files using Flask Blueprints,
similar to Laravel's route groups with prefixes.
"""

from pipe.web.routes.bff import bff_bp
from pipe.web.routes.pages import pages_bp
from pipe.web.routes.search import search_bp
from pipe.web.routes.session import session_bp
from pipe.web.routes.settings import settings_bp

__all__ = [
    "bff_bp",
    "pages_bp",
    "search_bp",
    "session_bp",
    "settings_bp",
]
