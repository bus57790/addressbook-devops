import json
import os
import qrcode

# Sample users matching the schema expected by the Flask app
sample_users = [
    {
        "full_name": "Ada Lovelace",
        "phone": "+1-555-0101",
        "email": "ada@example.com",
        "address": "10 Binary Way, London, UK",
    },
    {
        "full_name": "Alan Turing",
        "phone": "+1-555-0102",
        "email": "alan@example.com",
        "address": "42 Enigma Ave, Bletchley, UK",
    },
    {
        "full_name": "Grace Hopper",
        "phone": "+1-555-0103",
        "email": "grace@example.com",
        "address": "1952 Compiler Rd, Arlington, VA",
    },
    {
        "full_name": "Linus Torvalds",
        "phone": "+1-555-0104",
        "email": "linus@example.com",
        "address": "100 Linux Blvd, Portland, OR",
    },
]

# Output directory for generated images
output_dir = "sample_qr_codes"
os.makedirs(output_dir, exist_ok=True)

for user in sample_users:
    # Convert user dict to JSON string payload
    payload = json.dumps(user)

    # Configure QR code generator
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    # Create image and save
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"{user['full_name'].lower().replace(' ', '_')}_qr.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)

    print(f"✅ Generated: {filepath}")

print(f"\nAll QR codes saved in '{output_dir}/' directory.")
