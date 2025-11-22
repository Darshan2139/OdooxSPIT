# 🚀 Deploy StockMaster NOW - 5 Minute Setup

**Everything is ready. Follow these 5 steps to go LIVE.**

---

## ⏱️ STEP 1: Create Render Account (2 min)
1. Go → https://render.com
2. Click "Sign up" → "Continue with GitHub"
3. Authorize access
4. ✅ Done

---

## 🗄️ STEP 2: Create Database (2 min)
1. Dashboard → "New +" → "PostgreSQL"
2. Fill:
   - Name: `stockmaster-db`
   - Database: `stockmaster`
   - User: `stockmaster_user`
   - Instance Type: **Free**
3. Click "Create Database"
4. **COPY this connection string** (you'll see it):
   ```
   postgresql://stockmaster_user:XXXX@oregon-postgres.render.com:5432/stockmaster
   ```
5. ✅ Save it (paste somewhere safe)

---

## 🌐 STEP 3: Create Web Service (1 min)
1. Dashboard → "New +" → "Web Service"
2. Select: **OdooxSPIT** repository
3. Fill:
   - Name: `stockmaster`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
   - Instance Type: **Free**
4. **DON'T CLICK CREATE YET** - keep this page open

---

## 🔐 STEP 4: Add Environment Variables (depends on Step 2)

**Click "Advanced"** → **"Add Environment Variable"** for each:

```bash
DATABASE_URL = [PASTE THE CONNECTION STRING FROM STEP 2]
SECRET_KEY = a7c3d8f2e9b1a4c6e8f0d2b4a6c8e0f2a4c6e8f0d2b4a6c8e0f2a4c6e8f0
FLASK_ENV = production
DEBUG = False
MAIL_USERNAME = your-email@gmail.com
MAIL_PASSWORD = [GET FROM GMAIL - see below]
MAIL_SERVER = smtp.gmail.com
MAIL_PORT = 587
```

### Get Gmail App Password (Required)
1. Go → https://myaccount.google.com/apppasswords
2. Select: **Mail** → **Windows Computer**
3. Click "Generate"
4. Copy the 16-char password → Paste as `MAIL_PASSWORD`

### Add all variables
- Click "Save" after EACH one
- Should have 8 variables total

---

## ▶️ STEP 5: Deploy & Run Migration (You're Live!) (2 min)

1. Click **"Create Web Service"**
2. Wait for status → **"Live"** (green) (~2-3 min)
3. Open **"Shell"** tab
4. Run this command:
   ```bash
   python migrations/migrate_add_pricing.py
   ```
5. Wait for "Migration completed" message
6. ✅ **LIVE!**

---

## 🎉 You're Deployed!

### Access Your App
```
🌐 URL: https://stockmaster.onrender.com
📝 Login: admin@stockmaster.com / admin123
```

### Live Dashboard
- View inventory
- Manage products
- Track stock

### Auto-Update
Push code to GitHub → Auto-deploys in 30 seconds!

---

## ✅ Checklist

- [ ] Created Render account
- [ ] Created PostgreSQL database
- [ ] Created Web Service
- [ ] Added all 8 environment variables
- [ ] Deployed (status = Live)
- [ ] Ran migration command
- [ ] Accessed https://stockmaster.onrender.com
- [ ] Logged in with admin@stockmaster.com / admin123

---

## 🆘 If Something Goes Wrong

### "502 Bad Gateway"
→ Check logs: Web Service → Logs tab
→ Usually means app crashed - look for red errors

### "DatabaseConnectionError"
→ Check DATABASE_URL is exactly correct (from Step 2)
→ Click "Restart" button in Service page

### "App taking forever to start"
→ Normal first time (cold start)
→ Subsequent requests will be fast

### Specific errors?
See detailed guide: `RENDER_DEPLOYMENT_STEPS.md`

---

## 🎯 Next Steps (After Live)

### Option A: Add Sample Data
```bash
# In Render Shell
python -c "
from app import app, db
from models import Category, Warehouse, Partner, Product
with app.app_context():
    # Create sample category
    cat = Category(name='Electronics', active=True)
    db.session.add(cat)
    db.session.commit()
    print('Sample data added!')
"
```

### Option B: Invite Team
Share: `https://stockmaster.onrender.com`

### Option C: Custom Domain
Settings → Custom Domain (optional, need domain)

---

## 📞 Support

Need help?
- Check logs in Render dashboard
- See `RENDER_DEPLOYMENT_STEPS.md` for detailed troubleshooting
- GitHub Issues: Report problems

---

**✅ Status:** Ready to Deploy  
**Time to Live:** ~10 minutes  
**Cost:** FREE  

🚀 **START NOW** → https://render.com
