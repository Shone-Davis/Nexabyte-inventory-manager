from flask import Blueprint, render_template, flash, request, redirect, url_for
from models import Product, db
from flask_login import login_required, current_user
from routes.admin import admin_required

products = Blueprint("products", __name__)

CATEGORIES = ["Laptops", "Phones", "Audio",
              "Tablets", "Accessories"]


@products.route("/products")
@login_required
def index():
    all_products = Product.query.all()
    return render_template("products/index.html", products=all_products)


@products.route("/products/add", methods=["GET", "POST"])
@login_required
@admin_required
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
            elif not category and category not in CATEGORIES:
                flash("Please select a category!", "error")
            elif price <= 0:
                flash("Price must be positive!", "error")
            elif stock < 0:
                flash("Stock levels cannot be negative", "error")
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
    return render_template("products/add.html", error=error, categories=CATEGORIES)


@products.route("/products/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f"Product '{product.name}' was successfully deleted.", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while deleting the product.", "error")

    return redirect(url_for('products.index'))


@products.route("/products/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    error = None
    product = Product.query.get_or_404(id)  # find product or show 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_raw = request.form.get("price", "0")
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        try:
            price = float(price_raw)
            stock = int(request.form.get("stock", 0))
            low_stock_threshold = int(
                request.form.get("low_stock_threshold", 10))

            if not name:
                flash("Product name required!", "error")
            elif not category or category not in CATEGORIES:
                flash("Select a category", "error")
            elif price <= 0:
                flash("Price must be positive", "error")
            elif stock < 0:
                flash("Stock levels cannot be negative!", "error")
            else:
                product.name = name
                product.price = price
                product.category = category
                product.stock = stock
                product.description = description
                product.low_stock_threshold = low_stock_threshold
                db.session.commit()
                flash(f"'{product.name}' updated!", "success")
                return redirect(url_for("products.index"))

        except ValueError:
            flash("Invalid price format!", "error")
    return render_template("products/edit.html", product=product, categories=CATEGORIES)


@products.route("/product/search")
@login_required
def search():
    query = request.args.get("q", "").strip().lower()
    results = Product.query.filter(
        Product.name.ilike(f"%{query}%")
    ).all()

    return render_template("products/search.html", query=query, results=results)


@products.route("/products/<int:id>")
@login_required
def detail(id):
    product = Product.query.get_or_404(id)
    return render_template("products/detail.html", product=product)
