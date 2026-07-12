from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
import mysql.connector
import razorpay
from datetime import datetime, date
import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from collections import defaultdict
import qrcode
import base64
import os
from db_config import get_connection


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Razorpay credentials
RAZORPAY_KEY_ID = 'rzp_test_ybTUZEkIjq9Grs'
RAZORPAY_KEY_SECRET = 'Kjc77AU98Ygu75TgEUKarjOV'
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Database connection
def get_db_connection():
    return get_connection()
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('user_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/continue_as_user')
def continue_as_user():
    session['username'] = 'guest_user'
    session['role'] = 'user'
    session['cart'] = []
    return redirect(url_for('user_dashboard'))

@app.route('/user')
def user_dashboard():
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    category = request.args.get('category', '').strip()

    query = "SELECT * FROM menu WHERE stock > 0 AND is_deleted = FALSE"
    values = []

    if search_query:
        query += " AND name LIKE %s"
        values.append(f"%{search_query}%")
    if min_price:
        query += " AND price >= %s"
        values.append(min_price)
    if max_price:
        query += " AND price <= %s"
        values.append(max_price)
    if category:
        query += " AND category = %s"
        values.append(category)

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, tuple(values))
    menu_items = cursor.fetchall()
    cursor.close()
    db.close()

    cart_map = {str(item['id']): item['quantity'] for item in session.get('cart', [])}
    categories = ['Breakfast', 'Lunch', 'Snacks', 'Ice Creams', 'Beverages']
    return render_template('user_dashboard.html', menu=menu_items, cart_map=cart_map, categories=categories)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Active menu items
    cursor.execute("SELECT * FROM menu WHERE is_deleted = FALSE")
    menu_items = cursor.fetchall()

    # Deleted menu items
    cursor.execute("SELECT * FROM menu WHERE is_deleted = TRUE")
    deleted_menu = cursor.fetchall()

    # Feedback entries
    cursor.execute("SELECT * FROM feedback ORDER BY submitted_at DESC")
    feedbacks = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        'admin_dashboard.html',
        username=session['username'],
        menu=menu_items,
        deleted_menu=deleted_menu,
        feedbacks=feedbacks
    )
@app.route('/admin/delete_feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Feedback deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/report')
def sales_report():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    selected_date = request.args.get('selected_date', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    if not selected_date and not start_date and not end_date:
        selected_date = date.today().strftime('%Y-%m-%d')

    query = """
        SELECT m.name,
               SUM(oi.quantity) AS total_sold,
               SUM(oi.price * oi.quantity) AS total_revenue
        FROM order_items oi
        JOIN menu m ON oi.item_id = m.id
        WHERE m.is_deleted = FALSE
    """
    values = []

    if selected_date and is_valid_date(selected_date):
        query += " AND DATE(oi.sale_day) = %s"
        values.append(selected_date)
    else:
        if start_date and is_valid_date(start_date):
            query += " AND DATE(oi.sale_day) >= %s"
            values.append(start_date)
        if end_date and is_valid_date(end_date):
            query += " AND DATE(oi.sale_day) <= %s"
            values.append(end_date)

    query += " GROUP BY m.name ORDER BY total_sold DESC"

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, tuple(values))
        report_data = cursor.fetchall()

        total_revenue = sum(row['total_revenue'] for row in report_data)

        # --- Chart data for Google Charts ---
        chart_data = [['Item', 'Total Revenue']]
        quantity_chart_data = [['Item', 'Quantity Sold']]
        for row in report_data:
            chart_data.append([row['name'], float(row['total_revenue'])])
            quantity_chart_data.append([row['name'], int(row['total_sold'])])

    except Exception as e:
        flash(f"Error fetching report: {str(e)}", "danger")
        report_data = []
        total_revenue = 0.0
        chart_data = [['Item', 'Total Revenue']]
        quantity_chart_data = [['Item', 'Quantity Sold']]
    finally:
        cursor.close()
        db.close()

    return render_template('sales_report.html',
                           report=report_data,
                           selected_date=selected_date,
                           start_date=start_date,
                           end_date=end_date,
                           total_revenue=total_revenue,
                           chart_data=chart_data,
                           quantity_chart_data=quantity_chart_data)


@app.route('/add_menu', methods=['POST'])
def add_menu():
    if 'username' in session and session['role'] == 'admin':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        stock = request.form['stock']
        image = request.files['image'].read() if 'image' in request.files and request.files['image'].filename else None

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO menu (name, price, category, stock, image) VALUES (%s, %s, %s, %s, %s)",
                       (name, price, category, stock, image))
        db.commit()
        cursor.close()
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_menu/<int:item_id>')
def delete_menu(item_id):
    if 'username' in session and session['role'] == 'admin':
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE menu SET is_deleted = TRUE WHERE id = %s", (item_id,))
        db.commit()
        cursor.close()
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/update_stock/<int:item_id>', methods=['GET', 'POST'])
def update_stock(item_id):
    if 'username' in session and session['role'] == 'admin':
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == 'POST':
            new_stock = request.form['stock']
            cursor.execute("UPDATE menu SET stock = %s WHERE id = %s", (new_stock, item_id))
            db.commit()
            cursor.close()
            db.close()
            flash("Stock updated successfully.")
            return redirect(url_for('admin_dashboard'))

        cursor.execute("SELECT * FROM menu WHERE id = %s AND is_deleted = FALSE", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('update_stock.html', item=item) if item else redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/menu_image/<int:item_id>')
def menu_image(item_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT image FROM menu WHERE id = %s AND is_deleted = FALSE", (item_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return Response(result[0], mimetype='image/jpeg') if result and result[0] else ('', 404)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = int(request.form['item_id'])
    quantity = int(request.form.get('quantity', 1))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu WHERE id = %s AND is_deleted = FALSE", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    db.close()

    if item and item['stock'] >= quantity:
        cart = session.get('cart', [])
        for entry in cart:
            if entry['id'] == item_id:
                entry['quantity'] += quantity
                break
        else:
            cart.append({
                'id': item['id'],
                'name': item['name'],
                'price': float(item['price']),
                'quantity': quantity
            })
        session['cart'] = cart
        flash(f"Added {quantity} x {item['name']} to cart.")
    else:
        flash("Item is out of stock or quantity exceeds availability.")
    return redirect(url_for('user_dashboard'))

@app.route('/view_cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        removed_item = cart.pop(index)
        flash(f"Removed {removed_item['name']} from cart.")
        session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/increment_quantity/<int:index>')
def increment_quantity(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart[index]['quantity'] += 1
        session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/decrement_quantity/<int:index>')
def decrement_quantity(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        if cart[index]['quantity'] > 1:
            cart[index]['quantity'] -= 1
        else:
            flash(f"Removed {cart[index]['name']} from cart.")
            cart.pop(index)
        session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    flash("Cart cleared.")
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total=total)

@app.route('/payment')
def payment():
    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty!")
        return redirect(url_for('user_dashboard'))

    total = int(sum(item['price'] * item['quantity'] for item in cart) * 100)
    order = razorpay_client.order.create({
        'amount': total,
        'currency': 'INR',
        'payment_capture': 1
    })

    session['order_id'] = order['id']
    return render_template('payment.html',
                           total=total,
                           razorpay_order_id=order['id'],
                           razorpay_key_id=RAZORPAY_KEY_ID)

@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    data = request.get_json()
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        })

        payment_id = data.get('razorpay_payment_id')
        cart = session.get('cart', [])
        if not cart:
            return jsonify({'error': 'Cart is empty'}), 400

        now = datetime.now()
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO orders (payment_id) VALUES (%s)", (payment_id,))
        db.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        order_id = cursor.fetchone()[0]

        for item in cart:
            cursor.execute("""
                INSERT INTO order_items (order_id, item_id, quantity, price, sale_day)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item['id'], item['quantity'], item['price'], now))
            cursor.execute("UPDATE menu SET stock = stock - %s WHERE id = %s", (item['quantity'], item['id']))
        db.commit()
        cursor.close()
        db.close()

        session['cart'] = []
        return jsonify({'token_number': order_id})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'error': 'Payment verification failed'}), 400
@app.route('/payment_success')
def payment_success():
    if 'username' not in session:
        return redirect(url_for('login'))

    order_id = request.args.get('token')
    if not order_id:
        flash("Invalid order reference.", "danger")
        return redirect(url_for('user_dashboard'))

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT oi.item_id, m.name AS item_name, oi.quantity, oi.price
            FROM order_items oi
            JOIN menu m ON oi.item_id = m.id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()

        total_amount = sum(item['quantity'] * item['price'] for item in items)

        # Generate QR code as base64
        feedback_url = url_for('feedback', _external=True)
        qr = qrcode.make(feedback_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        flash(f"Error loading receipt: {str(e)}", "danger")
        items = []
        total_amount = 0.0
        qr_base64 = ""
    finally:
        cursor.close()
        db.close()

    return render_template('payment_success.html',
                           token=order_id,
                           items=items,
                           total_amount=total_amount,
                           qr_code=qr_base64)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        comments = request.form['comments']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO feedback (name, rating, comments) VALUES (%s, %s, %s)", (name, rating, comments))
        db.commit()
        cursor.close()
        db.close()

    return render_template('feedback.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

