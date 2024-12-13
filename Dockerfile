# Gunakan image dasar Python
FROM python:3.9-slim

# Set working directory dalam container
WORKDIR /app

# Salin semua file aplikasi ke dalam container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Tentukan port yang akan digunakan
ENV PORT 8080

# Jalankan aplikasi Flask menggunakan gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]