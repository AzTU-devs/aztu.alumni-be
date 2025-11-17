#!/bin/bash
set -e

echo "🔧 Loading environment variables..."
: "${POSTGRES_HOST:?POSTGRES_HOST not set}"
: "${POSTGRES_PORT:?POSTGRES_PORT not set}"
: "${POSTGRES_DB:?POSTGRES_DB not set}"
: "${POSTGRES_USER:?POSTGRES_USER not set}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}"

echo "🕓 Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "PostgreSQL is up - continuing..."

echo "Running database migrations..."
alembic upgrade head

echo " Checking & creating superuser..."

python <<EOF
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

username = "karam"
email = "karamshukurlu@gmail.com"
password = "karam"

user = db.query(User).filter(User.username == username).first()

if not user:
    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_superuser=True,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    print("✅ Superuser created")
else:
    print("Superuser already exists")
EOF

if [ -d "static" ]; then
    echo "Collecting static files..."
    mkdir -p /app/staticfiles
    cp -r static/* /app/staticfiles
fi

echo "🚀 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
