from flask import Flask, render_template
from config import Config
from models import db, User, Product
from flask_login import LoginManager
from flask_migrate import Migrate

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth
    from routes.products import products
    from routes.dashboard import dashboard
    from routes.admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(dashboard)
    app.register_blueprint(admin)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    # Create tables and seed admin
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username=app.config["ADMIN_USERNAME"]).first():
            admin = User(
                username=app.config["ADMIN_USERNAME"], role="admin", is_admin=True)
            admin.set_password(app.config["ADMIN_PASSWORD"])
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")

        # Seed sample products if empty
        if Product.query.count() == 0:
            samples = [
                Product(name="MacBook Pro M3", price=1999.99, category="Laptops",
                        stock=15, description="Apple M3 chip, 16GB RAM", low_stock_threshold=5),
                Product(name="iPhone 15 Pro",  price=999.99,  category="Phones",
                        stock=8,  description="Titanium design, A17 Pro", low_stock_threshold=5),
                Product(name="AirPods Pro",    price=249.99,  category="Audio",
                        stock=3,  description="Active noise cancellation", low_stock_threshold=5),
                Product(name="iPad Air M2",    price=599.99,  category="Tablets",
                        stock=20, description="M2 chip, 10.9 inch display", low_stock_threshold=5),
                Product(name="Magic Keyboard", price=99.99,   category="Accessories",
                        stock=2,  description="Wireless, Touch ID", low_stock_threshold=5),
            ]
            db.session.add_all(samples)
            db.session.commit()
            print("Sample products added!")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
