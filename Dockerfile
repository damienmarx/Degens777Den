# Multi-stage build for optimized production image
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps --production

# Copy source
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/*.config.js ./
COPY frontend/tsconfig.json ./

# Build
RUN npm run build

# ==================== BACKEND STAGE ====================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create non-root user
RUN useradd -m -u 1000 degensden && \
    chown -R degensden:degensden /app

USER degensden

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start both services
CMD ["sh", "-c", "cd backend && python server.py & cd frontend/build && python -m http.server 3000"]
