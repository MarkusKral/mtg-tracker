# MTG Tournament Tracker - Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend code
COPY frontend/ ./frontend/

# Create directories for persistent data
RUN mkdir -p /app/data /app/backend/uploads/avatars

WORKDIR /app/backend

# Environment variables (can be overridden)
ENV DATABASE_URL=sqlite:////app/data/mtg_tournament.db
ENV UPLOAD_DIR=/app/backend/uploads
ENV ADMIN_PASSWORD=admin
ENV JWT_SECRET=change-this-to-a-random-secret-in-production
ENV JWT_ALGORITHM=HS256
ENV JWT_EXPIRATION_HOURS=24
ENV ALLOWED_ORIGINS=*

EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

