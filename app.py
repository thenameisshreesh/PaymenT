from flask import Flask, render_template, request, redirect
import os
import requests
import uuid
import qrcode
from io import BytesIO
import base64
from flask_mail import Mail, Message

app = Flask(__name__)

# ============ Mail Config ============
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'shreeshpitambare084@gmail.com'
app.config['MAIL_PASSWORD'] = 'untk duvx aisq ssuq'  # ✅ App password, not your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'shreeshpitambare084@gmail.com'
mail = Mail(app)

# ============ Home Page ============
@app.route('/')
def index():
    return render_template('index.html')

# ============ Pay Route ============
@app.route('/pay', methods=['POST'])
def pay():
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    transaction_id = str(uuid.uuid4())
    amount = 1
    order_id = "Order" + str(uuid.uuid4())

    headers = {
        "x-client-id": "896457b3bd65c4bc202da34a48754698",
        "x-client-secret": "cfsk_ma_prod_58a4944f0018534a39d68c2e96a5337e_ca091af8",
        "x-api-version": "2022-01-01",
        "Content-Type": "application/json"
    }

    data = {
        "order_id": order_id,
        "order_amount": amount,
        "order_currency": "INR",
        "customer_details": {
            "customer_id": mobile,
            "customer_name": name,
            "customer_email": email,
            "customer_phone": mobile
        },
        "order_meta": {
        "return_url": f"https://payment-production-56f3.up.railway.app/payment_status?order_id={order_id}"
            
        }
    }

    res = requests.post("https://api.cashfree.com/pg/orders", json=data, headers=headers)
    res_data = res.json()

    if 'payment_link' in res_data:
        return redirect(res_data['payment_link'])
    else:
        return f"Error: {res_data}"

# ============ Payment Status ============
@app.route('/payment_status')
def payment_status():
    order_id = request.args.get('order_id')
    name = request.args.get('name')
    email = request.args.get('email')
    mobile = request.args.get('mobile')
    transaction_id = request.args.get('transaction_id')

    headers = {
        "x-client-id": "896457b3bd65c4bc202da34a48754698",
        "x-client-secret": "cfsk_ma_prod_58a4944f0018534a39d68c2e96a5337e_ca091af8",
        "x-api-version": "2022-01-01",
    }

    res = requests.get(f"https://api.cashfree.com/pg/orders/{order_id}", headers=headers)
    order_info = res.json()

    if order_info.get('order_status') == 'PAID':
        # ✅ Generate QR Code
        qr_data = f"{name}|{email}|{mobile}"
        qr_img = qrcode.make(qr_data)
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")

        # ✅ Send Email to User
        msg = Message('Payment Confirmation - Your QR Code', recipients=[email])
        msg.body = f"""Dear {name},

Thank you for registering for our event.
Transaction ID: {transaction_id}

Please find your unique QR code below. Show this at the entry gate.

Regards,
Event Team VEERA's NAIIL 💅
"""
        msg.attach("qr.png", "image/png", buffered.getvalue())
        try:
            mail.send(msg)
        except Exception as e:
            return f"Error sending mail: {e}", 500

        # ✅ Send Email to Admin
        admin_msg = Message('New Customer Registered', recipients=['shreeshpitambare777@gmail.com'])
        admin_msg.body = f"""New Customer Registered:

Name: {name}
Email: {email}
Transaction ID: {transaction_id}
"""
        try:
            mail.send(admin_msg)
        except Exception as e:
            return f"Error sending admin mail: {e}", 500

        return render_template("success.html")

    return "Payment failed or not completed. Please try again.", 400

# ============ Run App ============
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
