from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Product
from sqlalchemy import func
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
    recent_products = Product.query.order_by(
        Product.created_at.desc()).limit(5).all()

    # category data for doughnut chart
    category_data = Product.query.with_entities(
        Product.category,
        func.count(Product.id).label("count")
    ).group_by(Product.category).all()

    category_labels = [row.category for row in category_data]
    category_counts = [row.count for row in category_data]

    # stock data for the bar cahrt ( Top 5 by stock)
    top_products = Product.query.order_by(
        Product.stock.desc()
    ).limit(5).all()

    stock_labels = [p.name for p in top_products]
    stock_values = [p.stock for p in top_products]

    return render_template("dashboard/index.html",
                           total_products=total_products,
                           total_value=round(total_value, 2),
                           low_stock=low_stock,
                           low_stock_count=len(low_stock),
                           recent_products=recent_products,
                           category_labels=category_labels,
                           category_counts=category_counts,
                           stock_labels=stock_labels,
                           stock_values=stock_values
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
