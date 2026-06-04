from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from models import User, db
from functools import wraps
from flask import abort

admin = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin_user:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin.route("/admin/staff")
@login_required
@admin_required
def staff_list():
    staff_members = User.query.filter_by(role="staff").all()
    return render_template("admin/staff.html", staff_members=staff_members)


@admin.route("/admin/staff/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_staff():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username:
            flash("Username is required!", "error")
        elif not password:
            flash("Password is required!", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters!", "error")
        elif User.query.filter_by(username=username).first():
            flash(f"Username '{username}' already exists!", "error")
        else:                    # ← else belongs HERE inside the POST block
            new_staff = User(
                username=username,
                role="staff",
                is_admin=False
            )
            new_staff.set_password(password)
            db.session.add(new_staff)
            db.session.commit()
            flash(f"Staff account '{username}' created!", "success")
            return redirect(url_for("admin.staff_list"))

    return render_template("admin/create_staff.html")


@admin.route("/admin/staff/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_staff(id):
    staff = User.query.get_or_404(id)
    if staff.role == "admin":
        flash("Cannot delete admin accounts!", "error")
        return redirect(url_for('admin.staff_list'))
    db.session.delete(staff)
    db.session.commit()
    flash(f"Staff account '{staff.username}' removed.", "success")
    return redirect(url_for('admin.staff_list'))
