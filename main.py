import json
from flask import Flask, request, jsonify
from google.cloud import storage, firestore
import tensorflow as tf
import numpy as np
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Konfigurasi Google Cloud
BUCKET_NAME = "tanipredict-models"
MODELS = {
    "tomato": "tomato.h5",
    "chili": "chili.h5"
}
CACHE_DIR = "./models"
os.makedirs(CACHE_DIR, exist_ok=True)

# Firestore Client
db = firestore.Client()

# Fungsi untuk mendownload dan membaca file JSON dari Google Cloud Storage
def download_disease_names(plant_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{plant_name}.json")
    json_data = blob.download_as_text()
    return json.loads(json_data)

# Fungsi Download Model
def download_model(model_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(MODELS[model_name])
    local_path = os.path.join(CACHE_DIR, model_name + ".h5")
    if not os.path.exists(local_path):
        print(f"Downloading {model_name} model...")
        blob.download_to_filename(local_path)
    return tf.keras.models.load_model(local_path, compile=False)

# Inisialisasi Model
models = {name: download_model(name) for name in MODELS}

# Fungsi Prediksi
def predict(image, model):
    image = tf.image.decode_image(image, channels=3)
    image = tf.image.resize(image, [150, 150]) / 255.0
    image = tf.expand_dims(image, axis=0)
    predictions = model.predict(image)[0]
    confidence = np.max(predictions)
    disease_index = np.argmax(predictions)
    return disease_index, confidence

# Validasi Ukuran File
def validate_file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= 1 * 1024 * 1024  # Maksimal 1 MB

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

# Endpoint Tomato
@app.route("/predict/tomato", methods=["POST"])
def predict_tomato():
    try:
        # Validasi input tanaman
        plant_name = request.form.get("plant")
        if plant_name != "tomato":
            return jsonify({"error": "Invalid plant name. This endpoint only accepts 'tomato'."}), 400
        
        # Mengambil nama penyakit dari file JSON
        disease_names = download_disease_names("tomato")["penyakit tanaman"]

        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image provided"}), 400
        if not validate_file_size(file):  # Gunakan fungsi validasi
            return jsonify({"error": "File size exceeds 1 MB"}), 400
        
        model = models["tomato"]
        disease_idx, confidence = predict(file.read(), model)
        
        # Ambil nama penyakit dari dictionary berdasarkan indeks
        disease_name = list(disease_names.keys())[disease_idx]  # Mengambil nama penyakit berdasarkan indeks
        
        result = {
            "id": str(uuid.uuid4()),
            "plant": "tomato",
            "result": disease_name,
            "confidenceScore": float(confidence),
            "isAboveThreshold": bool(confidence > 0.8),
            "createdAt": datetime.utcnow().isoformat(),
        }
        db.collection("predictions").add(result)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint Chili
@app.route("/predict/chili", methods=["POST"])
def predict_chili():
    try:
        # Validasi input tanaman
        plant_name = request.form.get("plant")
        if plant_name != "chili":
            return jsonify({"error": "Invalid plant name. This endpoint only accepts 'chili'."}), 400
        
        # Mengambil nama penyakit dari file JSON
        disease_names = download_disease_names("chili")["penyakit tanaman"]

        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image provided"}), 400
        if not validate_file_size(file):  # Gunakan fungsi validasi
            return jsonify({"error": "File size exceeds 1 MB"}), 400
        
        model = models["chili"]
        disease_idx, confidence = predict(file.read(), model)
        
        # Ambil nama penyakit dari dictionary berdasarkan indeks
        disease_name = list(disease_names.keys())[disease_idx]  # Mengambil nama penyakit berdasarkan indeks
        
        result = {
            "id": str(uuid.uuid4()),
            "plant": "chili",
            "result": disease_name,
            "confidenceScore": float(confidence),
            "isAboveThreshold": bool(confidence > 0.8),
            "createdAt": datetime.utcnow().isoformat(),
        }
        db.collection("predictions").add(result)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))