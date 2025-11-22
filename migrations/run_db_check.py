"""Quick DB check to run the dashboard product count query."""
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# prevent routes import
os.environ.setdefault('SKIP_IMPORT_ROUTE', '1')

from app import app
from models import Product

with app.app_context():
    try:
        cnt = Product.query.filter_by(active=True).count()
        print('Active products count:', cnt)
    except Exception as e:
        print('Error when querying products:', e)
        raise
