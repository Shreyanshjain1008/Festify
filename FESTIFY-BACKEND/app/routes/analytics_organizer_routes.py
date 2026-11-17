from flask import Blueprint, g

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.analytics_organizer_service import (
    get_organizer_analytics
)


analytics_organizer_bp = Blueprint(
    "analytics_organizer",
    __name__
)


@analytics_organizer_bp.route(
    "/<int:organizer_id>",
    methods=["GET"]
)
@token_required
@roles_required("ORGANIZER", "ADMIN")
def organizer_analytics_route(organizer_id):

    return get_organizer_analytics(
        organizer_id
    )