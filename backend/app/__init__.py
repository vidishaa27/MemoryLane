import os
from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db, migrate, cors

def create_app(config_class=None):
    """
    Application factory for MemoryLane Flask application.
    """
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_dir = os.path.join(backend_dir, "templates")
    static_dir = os.path.join(backend_dir, "static")

    app = Flask(
        __name__,
        template_folder=templates_dir,
        static_folder=static_dir
    )

    if config_class is None:
        app_env = os.getenv("APP_ENV", "development").lower()
        if app_env == "production":
            config_class = ProductionConfig
        elif app_env == "testing":
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    cors.init_app(app)

    # Register blueprints
    from app.routes import views_bp, auth_bp, magazines_bp, pages_bp
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(magazines_bp)
    app.register_blueprint(pages_bp)

    return app
