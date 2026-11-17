from flask import Blueprint

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.analytics_admin_service import (
    get_admin_analytics
)


analytics_admin_bp = Blueprint(
    "analytics_admin",
    __name__
)


@analytics_admin_bp.route(
    "/",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def admin_analytics_route():

    return get_admin_analytics()