from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from datetime import date

from app.config.config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    with app.app_context():
        from app import models

    # ---------------- Blueprints register karo ----------------
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.society_routes import society_bp
    from app.routes.organizer_routes import organizer_bp
    from app.routes.venue_routes import venue_bp
    from app.routes.event_routes import event_bp
    from app.routes.registration_routes import registration_bp
    from app.routes.day_pass_routes import day_pass_bp
    from app.routes.pass_routes import pass_bp
    from app.routes.feedback_routes import feedback_bp
    from app.routes.analytics_organizer_routes import analytics_organizer_bp
    from app.routes.analytics_admin_routes import analytics_admin_bp
    from app.routes.chatbot_faq_routes import chatbot_faq_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(society_bp, url_prefix="/api/societies")
    app.register_blueprint(organizer_bp, url_prefix="/api/organizers")
    app.register_blueprint(venue_bp, url_prefix="/api/venues")
    app.register_blueprint(event_bp, url_prefix="/api/events")
    app.register_blueprint(registration_bp, url_prefix="/api/registrations")
    app.register_blueprint(day_pass_bp, url_prefix="/api/day-passes")
    app.register_blueprint(pass_bp, url_prefix="/api/pass")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(analytics_organizer_bp, url_prefix="/api/analytics/organizer")
    app.register_blueprint(analytics_admin_bp, url_prefix="/api/analytics/admin")
    app.register_blueprint(chatbot_faq_bp, url_prefix="/api/faq")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    # ------------------------------------------------------------

    @app.route('/')
    def health_check():
        return {"success": True, "message": "Festify backend is running"}

    @app.route('/db-check')
    def db_check():
        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return {"success": True, "message": "Database connected successfully!"}
        except Exception as e:
            return {"success": False, "message": "Database connection failed", "error": str(e)}, 500

    @app.route('/test-insert')
    def test_insert():
        from app.models.user import User
        try:
            new_user = User(
                name="Flask Test User",
                email="flasktest@example.com",
                password_hash="dummyhash",
                phone="8888888888",
                college_id_number="FLASK001",
                college_name="Test College",
                branch="IT",
                year_of_study=3,
                date_of_birth=date(2003, 1, 1),
                gender="Male",
                role="PARTICIPANT"
            )
            db.session.add(new_user)
            db.session.commit()
            return {"success": True, "message": "User inserted successfully!", "user_id": new_user.user_id}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}, 500

    return app