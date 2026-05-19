from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Product
dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("dashboard.landing"))


@dashboard.route("/dashboard")
@login_required
def index():
    total_products = Product.query.count()
    total_value = sum(p.total_value for p in Product.query.all())
    low_stock = Product.query.filter(
        Product.stock <= Product.low_stock_threshold).all()
    categories = db_category_counts()
    recent_products = Product.query.order_by(
        Product.created_at.desc()).limit(5).all()

    return render_template("dashboard/index.html",
                           total_products=total_products,
                           total_value=round(total_value, 2),
                           low_stock=low_stock,
                           low_stock_count=len(low_stock),
                           recent_products=recent_products
                           )


def db_category_counts():
    from models import db
    from sqlalchemy import func
    return Product.query.with_entities(
        Product.category,
        func.count(Product.id).label("count")
    ).group_by(Product.category).all()


@dashboard.route("/landing")
def landing():
    return render_template("landing.html")
