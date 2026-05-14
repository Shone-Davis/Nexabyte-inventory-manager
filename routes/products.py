from flask import Blueprint, render_template, flash, request, redirect, url_for
from models import Product, db
from flask_login import login_required

products = Blueprint("products", __name__)


@products.route("/products")
@login_required
def index():
    all_products = Product.query.all()
    return render_template("products/index.html", products=all_products)


@products.route("/products/add", methods=["GET", "POST"])
@login_required
def add():
    error = None
    if request.method == "POST":
        name = request.form.get('name', "").strip()
        price_raw = request.form.get('price', "0")
        description = request.form.get('description', "").strip()
        category = request.form.get('category', "").strip()
        try:
            price = float(price_raw)
            stock = int(request.form.get('stock', 0))
            low_stock_threshold = int(
                request.form.get("low_stock_threshold", 10))

            if not name:
                flash("Product name required!", "error")
            elif not category:
                flash("Please select a category!", "error")
            elif price <= 0:
                flash("Price must be positive!", "error")
            else:
                new_product = Product(
                    name=name,
                    price=price,
                    category=category,
                    stock=stock,
                    description=description,
                    low_stock_threshold=low_stock_threshold
                )
                db.session.add(new_product)
                db.session.commit()
                flash(f"{name} added successfully!", "success")
                return redirect(url_for("products.index"))
        except ValueError:
            flash("Invalid price format!", "error")
    return render_template("products/add.html", error=error)
