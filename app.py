from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models.user import db, User
from models.interview import Interview, Answer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints register karo
    from routes.auth_routes import auth
    from routes.dashboard_routes import dashboard
    from routes.interview_routes import interview
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(interview)

    @app.route('/')
    def home():
        return render_template('index.html')

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

    app.run(debug=True)