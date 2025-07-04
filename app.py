from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from waitress import serve

app = Flask(__name__)
app.secret_key = 'techzone_secret_key'
CORS(app, resources={r"/order": {"origins": "*"}})

# Login credentials
VALID_USERNAME = "tech1"
VALID_PASSWORD = "virtual@123"

# Gmail config
GMAIL_USER = os.getenv('GMAIL_USER', 'johnjain2002@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'pyzq szzu rvqy vloo')
GMAIL_SMTP = 'smtp.gmail.com'
GMAIL_PORT = 465

# ------------------ LOGIN ROUTES ------------------ #
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['username'] = username
            return redirect(url_for('main'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# @app.route('/main')
# def main():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     return render_template('main.html')

# @app.route('/templates/products')
# def products():
#     return render_template('products.html')

# @app.route('/verification')
# def verification():
#     return render_template('verification.html')  # if you have this file

# @app.route('/index')
# def index():
#     return render_template('index.html')

# @app.route('/index.html')
# def index_html():
#     return render_template('index.html')

# @app.route('/main')
# def main():
#     return render_template('main.html')

# @app.route('/products')
# def products():
#     return render_template('products.html')


@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/verification')
def verification():
    return render_template('verification.html')

@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

# ------------------ LOGOUT ROUTE ------------------ #
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ------------------ ORDER EMAIL ROUTE ------------------ #
@app.route('/order', methods=['POST'])
def order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        recipient_email = data.get('email')
        cart_items = data.get('items', [])

        if not recipient_email:
            return jsonify({"status": "error", "message": "Email is required"}), 400

        # Totals
        subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        shipping = 0 if subtotal > 100 else 10
        gst = subtotal * 0.18
        total = subtotal + shipping + gst

        # Create email
        msg = MIMEMultipart()
        msg['Subject'] = "Order Confirmation - TechZONE"
        msg['From'] = GMAIL_USER
        msg['To'] = recipient_email

        html = f"""
        <html>
            <body>
                <h2>Thank you for your order!</h2>
                <p>Order Summary:</p>
                <table border="1" cellpadding="5" cellspacing="0">
                    <tr>
                        <th>Item</th><th>Price</th><th>Quantity</th><th>Total</th>
                    </tr>
                    {"".join(
                        f"<tr><td>{item['title']}</td><td>${item['price']}</td><td>{item['quantity']}</td><td>${float(item['price']) * int(item['quantity']):.2f}</td></tr>"
                        for item in cart_items
                    )}
                </table>
                <p><strong>Subtotal:</strong> ${subtotal:.2f}</p>
                <p><strong>Shipping:</strong> ${shipping:.2f}</p>
                <p><strong>GST (18%):</strong> ${gst:.2f}</p>
                <p><strong>Total:</strong> ${total:.2f}</p>
                <p>We'll process your order shortly. Delivery will be within 3-5 business days.</p>
                <p>Thank you for shopping with us!</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP_SSL(GMAIL_SMTP, GMAIL_PORT) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

        return jsonify({
            "status": "success",
            "message": "Order confirmed! Check your email.",
            "redirect": f"/index.html?email={recipient_email}"
        })

    except smtplib.SMTPAuthenticationError:
        return jsonify({"status": "error", "message": "Email server authentication failed"}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

# ------------------ MAIN ------------------ #
if __name__ == '__main__':
    app.run(debug=True, port=5000)
