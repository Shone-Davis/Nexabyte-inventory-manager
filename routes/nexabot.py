from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import Product, User, db
from openai import OpenAI
from config import Config

nexabot = Blueprint("nexabot", __name__)
client = OpenAI(api_key=Config.OPENAI_API_KEY)


def get_inventory_context():
    products = Product.query.all()
    staff = User.query.filter_by(role="staff").all()

    product_lines = []
    for p in products:
        status = "Low Stock" if p.is_low_stock else "In Stock"
        product_lines.append(
            f"- {p.name} | Category: {p.category} | "
            f"Price: ${p.price} | Stock: {p.stock} | Status: {status} | "
            f"Inventory Value: ${p.total_value}"
        )

    staff_lines = []
    for s in staff:
        joined = s.created_at.strftime(
            '%B %d, %Y') if s.created_at else 'Unknown'
        staff_lines.append(f"- Username: {s.username} | Joined: {joined}")

    total_value = sum(p.total_value for p in products)
    low_stock = [p.name for p in products if p.is_low_stock]

    context = f"""You are Nexabot, an AI inventory assistant for NEXABYTE store.
You have access to real-time inventory and staff data below.
Answer questions accurately using ONLY this data. Be concise and direct.

STORE SUMMARY:
- Total Products: {len(products)}
- Total Inventory Value: ${round(total_value, 2)}
- Low Stock Items: {', '.join(low_stock) if low_stock else 'None'}
- Total Staff Members: {len(staff)}

PRODUCT LIST:
{chr(10).join(product_lines) if product_lines else 'No products'}

STAFF LIST:
{chr(10).join(staff_lines) if staff_lines else 'No staff members found'}

RULES:
- Answer only based on the data above
- If asked how many staff, use the Total Staff Members number
- If asked about a specific staff member, check the STAFF LIST
- If asked something not in this data, say: "I don't have that data in my current inventory records"
"""
    return context


@nexabot.route("/nexabot/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    history = data.get("history", [])  # get history

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        context = get_inventory_context()

        # Build messages array with full history
        messages = [{"role": "system", "content": context}]

        # add converstion history (excludes last message)
        if len(history) > 1:
            messages.extend(history[:-1])

        # add current message :
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.3,
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
