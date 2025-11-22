# Deploy StockMaster to Render (Free) - Complete Guide

## ✅ Prerequisites
- ✅ Code pushed to GitHub (OdooxSPIT repository)
- ✅ Procfile created ✓
- ✅ requirements.txt updated ✓
- ✅ .env.example created ✓

## 🚀 Step 1: Create Render Account

1. Go to **https://render.com**
2. Click **"Sign up"** (recommend GitHub login)
3. Authorize Render to access your GitHub repositories
4. Complete profile setup

---

## 🗄️ Step 2: Create PostgreSQL Database

### Create Database Service
1. From Render dashboard: **New +** → **PostgreSQL**
2. Configure:
   - **Name:** `stockmaster-db`
   - **Database:** `stockmaster`
   - **User:** `stockmaster_user`
   - **Region:** Select closest region
   - **Instance Type:** Free
   - **Data Retention:** Leave default (7 days)

3. Click **Create Database**

### Save Connection Details
Once created, you'll see connection info. **COPY** this entire line:
```
postgresql://stockmaster_user:XXXXXXXXXXX@oregon-postgres.render.com:5432/stockmaster
```

**Save this** - you'll need it in Step 4.

---

## 🌐 Step 3: Create Web Service

### Deploy from GitHub
1. Dashboard: **New +** → **Web Service**
2. Select: `OdooxSPIT` repository
3. Configure:
   - **Name:** `stockmaster`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
   - **Instance Type:** Free
   - **Auto-Deploy:** Yes (from main branch)

4. Click **Create Web Service** (don't click Create yet - set env vars first!)

### Add Environment Variables
**IMPORTANT: Do this BEFORE deployment starts**

1. In Web Service page: **Environment** tab
2. Click **Add Environment Variable** for each:

```
DATABASE_URL = postgresql://stockmaster_user:XXXXXXXXXXX@oregon-postgres.render.com:5432/stockmaster
SECRET_KEY = a7c3d8f2e9b1a4c6e8f0d2b4a6c8e0f2a4c6e8f0d2b4a6c8e0f2a4c6e8f0
FLASK_ENV = production
DEBUG = False
MAIL_USERNAME = your-email@gmail.com
MAIL_PASSWORD = your-gmail-app-password
MAIL_SERVER = smtp.gmail.com
MAIL_PORT = 587
```

**How to generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Gmail App Password:**
1. Go: https://myaccount.google.com/apppasswords
2. Select: Mail → Windows Computer
3. Copy 16-char password → Paste as MAIL_PASSWORD

3. Click **Save** after each variable

---

## 🔄 Step 4: Run Database Migrations

### Wait for Deployment
- Render automatically starts building after you save env vars
- Wait for status: **"Live"** (green)
- Check logs: **Logs** tab

### Run Migration Command
Once deployed:
1. Open Web Service → **Shell** tab
2. Run:
```bash
python migrations/migrate_add_pricing.py
```

Expected output:
```
Adding column with: ALTER TABLE products ADD COLUMN cost_price...
Adding column with: ALTER TABLE products ADD COLUMN sale_price...
Adding column with: ALTER TABLE products ADD COLUMN currency...
Migration completed
```

---

## ✅ Step 5: Verify Deployment

### Check if Live
1. Go to Web Service page
2. Look for public URL: `https://stockmaster.onrender.com` (or similar)
3. Open in browser

### Test Login
```
URL: https://your-service-name.onrender.com/login
Email: admin@stockmaster.com
Password: admin123
```

### Check Status
- Dashboard page should show stats
- Products, Warehouses should load
- Email notifications should work

---

## 🔧 Troubleshooting

### "502 Bad Gateway" or "Application Error"
**Check logs:**
1. Web Service → **Logs** tab
2. Look for errors (red text)
3. Common issues:

```
ERROR: ModuleNotFoundError
→ Fix: Ensure requirements.txt has all packages

ERROR: DatabaseConnectionError
→ Fix: Check DATABASE_URL is correct

ERROR: No such file or directory 'app.py'
→ Fix: Ensure code is in root directory
```

### "Disallowed Host" Error
Add to `app.py`:
```python
app.config['PREFERRED_URL_SCHEME'] = 'https'
```

### Cold Start (App slow first time)
- Normal on free tier
- First request takes ~10-30 seconds
- Subsequent requests are fast

### Database Connection Issues
**Verify DATABASE_URL format:**
```
postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

**Test connection:**
```bash
# In Shell tab
python -c "from app import app, db; db.create_all()"
```

---

## 📊 After Deployment - Next Steps

### 1. Create Admin User (if needed)
```bash
# In Shell tab
python
>>> from app import app, db
>>> from models import User
>>> from werkzeug.security import generate_password_hash
>>> 
>>> admin = User(
...     name='Admin',
...     email='admin@stockmaster.com',
...     password=generate_password_hash('admin123'),
...     role='inventory_manager',
...     active=True
... )
>>> db.session.add(admin)
>>> db.session.commit()
>>> print("Admin user created!")
>>> exit()
```

### 2. Add Products
```bash
python migrations/seed_inr_data.py
```

### 3. Share URL
Your app is now live at: `https://stockmaster.onrender.com`

### 4. Monitor
- **Logs:** Check regularly for errors
- **Metrics:** View CPU/Memory usage
- **Auto-Deploy:** Enabled - pushes to GitHub auto-deploy

---

## 🎯 Key Information

| Item | Value |
|------|-------|
| **Hosting** | Render.com (Free) |
| **Database** | PostgreSQL (Free) |
| **URL** | https://stockmaster.onrender.com |
| **Status** | Live |
| **Auto-Deploy** | Yes (from GitHub main) |
| **Cost** | $0 (Free tier) |

---

## 📱 Access Your App

```
🌐 Web: https://stockmaster.onrender.com
📝 Login: admin@stockmaster.com / admin123
🔌 API: https://stockmaster.onrender.com/api/*
📊 Dashboard: https://stockmaster.onrender.com/dashboard
```

---

## 🔄 Updating After Deployment

Any changes pushed to GitHub are automatically deployed:

```powershell
# Local development
git add -A
git commit -m "fix: update feature"
git push origin main

# Render automatically deploys in ~30 seconds
# Check: Render Dashboard → Deployments tab
```

---

## 🆘 Support

- **Render Status:** https://render-status.com
- **PostgreSQL Issues:** Check database connection logs
- **Flask Issues:** Check app logs in Render dashboard
- **GitHub:** Push code updates automatically trigger redeploy

---

## 🎉 You're Live!

Your StockMaster inventory management system is now deployed on the internet!

**Share with your team:**
```
Production URL: https://stockmaster.onrender.com
```

---

**Deployment Date:** November 22, 2025  
**Version:** 1.0 - Live  
**Status:** ✅ Active
