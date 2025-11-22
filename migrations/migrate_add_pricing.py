"""Migration script: add pricing columns and price_history table.

Run this once (while your virtualenv is active and DATABASE_URL is configured):

    python migrations/migrate_add_pricing.py

It will add `cost_price`, `sale_price`, `currency` to `products` if they don't exist,
and create the `price_history` table.
"""
import sys
import os
from sqlalchemy import text, inspect

# Ensure project root is on sys.path so we can import app and models
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import os as _os
# Prevent importing routes when importing app for migrations
_os.environ.setdefault('SKIP_IMPORT_ROUTE', '1')

from app import db, app
import models


def column_exists(engine, table_name, column_name):
    try:
        insp = inspect(engine)
        cols = [c['name'] for c in insp.get_columns(table_name)]
        return column_name in cols
    except Exception:
        # fallback: try a simple query
        try:
            res = engine.execute(text(f"SELECT {column_name} FROM {table_name} LIMIT 1"))
            return True
        except Exception:
            return False


def add_column(engine, table_name, column_def_sql):
    try:
        print(f"Adding column with: {column_def_sql}")
        # Use a connection/transaction for SQLAlchemy 1.x and 2.x compatibility
        with engine.begin() as conn:
            conn.execute(text(column_def_sql))
        print("OK")
    except Exception as e:
        print(f"Failed to add column: {e}")


def main():
    with app.app_context():
        engine = db.engine
    # Add columns to products table if missing
    # Use Postgres types (double precision, varchar)
    if not column_exists(engine, 'products', 'cost_price'):
        add_column(engine, 'products', "ALTER TABLE products ADD COLUMN cost_price double precision DEFAULT 0.0")
    else:
        print("Column products.cost_price already exists")

    if not column_exists(engine, 'products', 'sale_price'):
        add_column(engine, 'products', "ALTER TABLE products ADD COLUMN sale_price double precision DEFAULT 0.0")
    else:
        print("Column products.sale_price already exists")

    if not column_exists(engine, 'products', 'currency'):
        add_column(engine, 'products', "ALTER TABLE products ADD COLUMN currency VARCHAR(8) DEFAULT 'USD'")
    else:
        print("Column products.currency already exists")

    # Create price_history table (will create only if not exists)
    try:
        models.PriceHistory.__table__.create(bind=engine, checkfirst=True)
        print("price_history table created or already exists")
    except Exception as e:
        print(f"Failed to create price_history table: {e}")

    print("Migration completed.")


if __name__ == '__main__':
    main()
