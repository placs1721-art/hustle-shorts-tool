FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# Timeout გავზარდეთ 15 წუთამდე (900 წამი), რომ 1080p-მ მოასწროს დამუშავება [cite: 2026-02-26]
CMD ["gunicorn", "--timeout", "900", "--workers", "1", "--threads", "8", "-b", "0.0.0.0:5000", "app:app"]
