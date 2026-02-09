# Gunakan Python versi ringan
FROM python:3.9-slim

# Set folder kerja di dalam container
WORKDIR /app

# Salin requirements dulu biar caching jalan (biar build cepat)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode backend ke dalam container
COPY . .

# Buat user non-root (Keamanan standar Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose port 7860 (Ini port wajib Hugging Face, bukan 8000)
EXPOSE 7860

# Jalankan server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]