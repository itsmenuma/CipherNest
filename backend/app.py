# app.py
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from encryptor import derive_key, encrypt_bytes, decrypt_bytes
from Crypto.Random import get_random_bytes
import io

# Config
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PASSWORD_FILE = os.path.join(DATA_DIR, 'data.txt.enc')  # encrypted password storage
SALT_FILE = os.path.join(DATA_DIR, 'salt.bin')
PBKDF2_ITERS = 200000

os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)  # allow frontend at different origin during development


def is_setup():
    return os.path.isfile(PASSWORD_FILE) and os.path.isfile(SALT_FILE)


@app.route('/setup', methods=['POST'])
def setup():
    """
    POST JSON: { "password": "thepassword" }
    This stores an encrypted password file locally. It's used to authenticate users.
    """
    data = request.json
    if not data or 'password' not in data:
        return jsonify({"error": "password required"}), 400

    password = data['password']
    if is_setup():
        return jsonify({"error": "already setup"}), 400

    # Derive key and store salt
    key, salt = derive_key(password, None, PBKDF2_ITERS)
    # We'll store the password plaintext encrypted (so backend can verify)
    enc = encrypt_bytes(password.encode('utf-8'), key)
    with open(PASSWORD_FILE, 'wb') as f:
        f.write(enc)
    with open(SALT_FILE, 'wb') as f:
        f.write(salt)
    return jsonify({"ok": True})


@app.route('/auth', methods=['POST'])
def auth():
    """
    POST JSON: { "password": "thepassword" }
    Verify password. Returns 200 if ok.
    """
    if not is_setup():
        return jsonify({"error": "not setup"}), 400
    data = request.json
    if not data or 'password' not in data:
        return jsonify({"error": "password required"}), 400
    password = data['password']
    salt = open(SALT_FILE, 'rb').read()
    key, _ = derive_key(password, salt, PBKDF2_ITERS)
    enc = open(PASSWORD_FILE, 'rb').read()
    try:
        dec = decrypt_bytes(enc, key).decode('utf-8')
    except Exception:
        return jsonify({"ok": False}), 401

    if dec == password:
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False}), 401


@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    """
    Accepts multipart file upload with key 'file' and JSON field 'password' (in form).
    Returns encrypted file as attachment (.enc)
    """
    if 'file' not in request.files:
        return jsonify({"error": "file required"}), 400
    password = request.form.get('password', None)
    if not password:
        return jsonify({"error": "password required"}), 400

    # Verify password quickly
    if not is_setup():
        return jsonify({"error": "server not setup"}), 400
    salt = open(SALT_FILE, 'rb').read()
    key, _ = derive_key(password, salt, PBKDF2_ITERS)
    # ensure password correct
    try:
        dec = decrypt_bytes(open(PASSWORD_FILE, 'rb').read(), key).decode('utf-8')
    except Exception:
        return jsonify({"error": "authentication failed"}), 401
    if dec != password:
        return jsonify({"error": "authentication failed"}), 401

    file = request.files['file']
    data = file.read()
    # For encrypting, derive a fresh per-file key from password+salt? We'll reuse same key here.
    encrypted = encrypt_bytes(data, key)
    # Return as file attachment
    out_name = file.filename + '.enc'
    return send_file(io.BytesIO(encrypted),
                     download_name=out_name,
                     as_attachment=True)


@app.route('/decrypt', methods=['POST'])
def decrypt_file_route():
    """
    Accepts multipart file upload (an encrypted .enc) and form password.
    Returns decrypted file as attachment.
    """
    if 'file' not in request.files:
        return jsonify({"error": "file required"}), 400
    password = request.form.get('password', None)
    if not password:
        return jsonify({"error": "password required"}), 400

    # auth
    if not is_setup():
        return jsonify({"error": "server not setup"}), 400
    salt = open(SALT_FILE, 'rb').read()
    key, _ = derive_key(password, salt, PBKDF2_ITERS)
    try:
        dec = decrypt_bytes(open(PASSWORD_FILE, 'rb').read(), key).decode('utf-8')
    except Exception:
        return jsonify({"error": "authentication failed"}), 401
    if dec != password:
        return jsonify({"error": "authentication failed"}), 401

    file = request.files['file']
    data = file.read()
    try:
        decrypted = decrypt_bytes(data, key)
    except Exception as e:
        return jsonify({"error": "decryption failed", "msg": str(e)}), 400

    # If original filename had .enc, strip it.
    filename = file.filename
    if filename.endswith('.enc'):
        filename = filename[:-4]
    return send_file(io.BytesIO(decrypted),
                     download_name=filename,
                     as_attachment=True)


if __name__ == '__main__':
    # For simple local run
    app.run(host='127.0.0.1', port=5000, debug=True)
