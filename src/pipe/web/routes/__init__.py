"""Flask route blueprints for the web application.

This module organizes routes into separate files using Flask Blueprints,
similar to Laravel's route groups with prefixes.
"""

from pipe.web.routes.bff import bff_bp
from pipe.web.routes.fs import fs_bp
from pipe.web.routes.meta import meta_bp
from pipe.web.routes.session import session_bp
from pipe.web.routes.session_management import session_management_bp
from pipe.web.routes.session_tree import session_tree_bp
from pipe.web.routes.settings import settings_bp
from pipe.web.routes.turn import turn_bp

__all__ = [
    "bff_bp",
    "fs_bp",
    "meta_bp",
    "session_bp",
    "session_management_bp",
    "session_tree_bp",
    "settings_bp",
    "turn_bp",
]
