web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
release: python migrations/migrate_add_pricing.py
