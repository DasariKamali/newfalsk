from flask import Flask

def create_app():
    app = Flask(__name__)
    from .views import forecasting_bp
    app.register_blueprint(forecasting_bp)

    return app
