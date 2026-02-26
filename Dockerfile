FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# დავამატეთ --preload და შევამცირეთ threads, რომ RAM არ გაივსოს [cite: 2026-02-26]
CMD ["gunicorn", "--timeout", "600", "--workers", "1", "--threads", "1", "--preload", "-b", "0.0.0.0:5000", "app:app"]
