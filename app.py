import os
import json
import psycopg2
from flask import Flask, request, jsonify, render_template_string
import qrcode
import io
import base64
from PIL import Image
from pyzbar.pyzbar import decode

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "addressbook")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            email VARCHAR(100),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT full_name, phone, email, address FROM contacts ORDER BY id DESC;")
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>QR Address Book</title></head>
    <body style="font-family:sans-serif; margin:30px;">
        <h2>QR Address Book</h2>
        <form action="/add_qr" method="post" enctype="multipart/form-data">
            <label><b>Upload QR Code Image to Add Contact:</b></label><br><br>
            <input type="file" name="qr_image" accept="image/*" required>
            <button type="submit">Process & Add</button>
        </form>
        <hr>
        <h3>Stored Contacts</h3>
        <table border="1" cellpadding="8" style="border-collapse:collapse;">
            <tr><th>Name</th><th>Phone</th><th>Email</th><th>Address</th></tr>
            {% for c in contacts %}
            <tr><td>{{c[0]}}</td><td>{{c[1]}}</td><td>{{c[2]}}</td><td>{{c[3]}}</td></tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, contacts=contacts)

@app.route("/add_qr", methods=["POST"])
def add_from_qr():
    if "qr_image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["qr_image"]
    img = Image.open(file.stream)
    decoded_objs = decode(img)
    
    if not decoded_objs:
        return jsonify({"error": "No valid QR code found in image"}), 400
        
    raw_data = decoded_objs[0].data.decode("utf-8")
    data = json.loads(raw_data)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contacts (full_name, phone, email, address) VALUES (%s, %s, %s, %s);",
        (data.get("full_name"), data.get("phone"), data.get("email"), data.get("address"))
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"status": "Contact added successfully", "data": data}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
