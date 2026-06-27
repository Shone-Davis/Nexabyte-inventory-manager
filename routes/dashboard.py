from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
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

    # products addup history weekly
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    # products added this week
    new_this_week = Product.query.filter(
        Product.created_at >= one_week_ago
    ).count()

    total_last_week = total_products - new_this_week
    # inventory value last week
    old_products = Product.query.filter(
        Product.created_at < one_week_ago
    ).all()
    value_last_week = sum(p.total_value for p in old_products)

    # Value exchange percentage
    if value_last_week > 0:
        value_change = round(
            ((total_value - value_last_week) / value_last_week) * 100, 1
        )
    else:
        value_change = 0

    return render_template("dashboard/index.html",
                           total_products=total_products,
                           total_value=round(total_value, 2),
                           low_stock=low_stock,
                           low_stock_count=len(low_stock),
                           recent_products=recent_products,
                           category_labels=category_labels,
                           category_counts=category_counts,
                           stock_labels=stock_labels,
                           stock_values=stock_values,
                           new_this_week=new_this_week,
                           total_last_week=total_last_week,
                           value_change=value_change
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
