# Render Deployment - Complete Guide (No Shell Needed)

Since migration already ran locally, you can deploy directly to Render!

---

## ✅ Prerequisites
- ✅ Migration already completed locally
- ✅ Code pushed to GitHub
- ✅ Render account (free)

---

## 🚀 Step-by-Step Render Deployment

### **STEP 1: Create Render Account (2 min)**

1. Go to **https://render.com**
2. Click **"Sign up with GitHub"**
3. Authorize access to your repositories
4. Complete setup

---

### **STEP 2: Create PostgreSQL Database (3 min)**

1. From Render Dashboard: **New +** → **PostgreSQL**

2. Configure:
   - **Name:** `stockmaster-db`
   - **Database:** `stockmaster`
   - **User:** `stockmaster_user`
   - **Region:** Choose closest to you (e.g., `oregon`)
   - **Instance Type:** Free
   - **Data Retention:** Default (7 days)

3. Click **"Create Database"**

4. **WAIT** for database to be ready (shows "Available")

5. **COPY the connection string** that looks like:
   ```
   postgresql://stockmaster_user:XXXXXXXXXXXXXXXX@oregon-postgres.render.com:5432/stockmaster
   ```

   Save this somewhere (Notepad) - you'll need it in Step 3!

---

### **STEP 3: Create Web Service (3 min)**

1. Dashboard: **New +** → **Web Service**

2. Select repository: **OdooxSPIT**

3. **Configure Settings:**

   - **Name:** `stockmaster`
   - **Environment:** `Python 3`
   - **Build Command:** 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command:** 
     ```
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
     ```
   - **Instance Type:** Free
   - **Auto-Deploy:** Yes

4. **Click "Create Web Service"**

   (⚠️ Don't worry about build errors yet - we'll fix them)

---

### **STEP 4: Add Environment Variables (2 min)**

Once service page loads, go to **"Environment"** tab:

1. Click **"Add Environment Variable"** and enter **EACH** of these:

   ```
   DATABASE_URL
   postgresql://stockmaster_user:XXXXXXXXXXXXXXXX@oregon-postgres.render.com:5432/stockmaster
   ```
   (Paste the string from STEP 2)

   ```
   SECRET_KEY
   a7c3d8f2e9b1a4c6e8f0d2b4a6c8e0f2a4c6e8f0d2b4a6c8e0f2a4c6e8f0
   ```

   ```
   FLASK_ENV
   production
   ```

   ```
   DEBUG
   False
   ```

   ```
   MAIL_USERNAME
   your-email@gmail.com
   ```

   ```
   MAIL_PASSWORD
   your-gmail-app-password
   ```
   (See Gmail setup below)

   ```
   MAIL_SERVER
   smtp.gmail.com
   ```

   ```
   MAIL_PORT
   587
   ```

2. **Click "Save"** after EACH variable

3. Service should auto-restart

---

### **STEP 5: Get Gmail App Password (2 min)**

If using Gmail for email notifications:

1. Go to: **https://myaccount.google.com/apppasswords**

2. Select:
   - **Select app:** Mail
   - **Select device:** Windows Computer

3. Click **"Generate"**

4. **Copy the 16-character password** (Google shows it)

5. Paste as `MAIL_PASSWORD` in Render environment variables

If not using Gmail, just use any placeholder in `MAIL_PASSWORD`.

---

### **STEP 6: Verify Deployment (Ongoing)**

1. Go to **"Events"** tab (shows deployment logs)

2. Watch for status changes:
   - `Building...` (30-60 seconds)
   - `Deploying...` (10-20 seconds)
   - `Live` ✅ (You're good!)

3. When status is **"Live"**, your app is deployed!

4. **Get your URL:**
   - Look at top of page: `https://stockmaster.onrender.com` (or similar)
   - This is your live app URL!

---

### **STEP 7: Test Your App (1 min)**

1. **Open your URL:** https://stockmaster.onrender.com

2. **Login page should load**

3. **Default credentials:**
   - Email: `admin@stockmaster.com`
   - Password: `admin123`

4. **Try logging in** → Should see dashboard

---

## 🎉 You're Live!

### Access Your App
```
🌐 URL: https://stockmaster.onrender.com
📊 Dashboard: https://stockmaster.onrender.com/dashboard
📦 Products: https://stockmaster.onrender.com/products
```

### Share with Team
```
Production: https://stockmaster.onrender.com
Login: admin@stockmaster.com / admin123
```

---

## 🔄 Auto-Deploy from GitHub

**From now on:**
- Push code to GitHub: `git push origin main`
- Render automatically redeploys (~30 seconds)
- No manual deployment needed!

```powershell
# Make changes locally
git add -A
git commit -m "fix: update feature"
git push origin main

# Render auto-deploys
# Check: Render Dashboard → Events tab
```

---

## 📊 Monitoring & Logs

### View Live Logs
1. Service page → **Logs** tab
2. Shows real-time app activity
3. Red text = errors

### Check Status
1. Service page → **Overview** tab
2. Shows CPU/Memory usage
3. Shows "Live" status

### Restart Service
If something goes wrong:
1. Click **"Manual Deploy"** button
2. Or just push a new commit to GitHub

---

## 🆘 Troubleshooting

### "502 Bad Gateway" or App Errors
Check logs:
1. Go to service → **Logs** tab
2. Look for red error messages
3. Common issues:

#### Issue: "ModuleNotFoundError"
```
ERROR: No module named 'flask'
```
**Fix:** Ensure all packages in `requirements.txt` are installed
- Check logs for pip install output
- Requirements installed correctly if no errors

#### Issue: "DatabaseConnectionError"
```
ERROR: could not connect to server: Connection refused
```
**Fix:** 
- Check DATABASE_URL is exactly correct (from Step 2)
- Verify PostgreSQL service is "Available" in Render dashboard
- Click "Manual Deploy" to restart

#### Issue: "ProgrammingError: column does not exist"
```
ProgrammingError: (psycopg2.errors.UndefinedColumn)
```
**Fix:** Database migration didn't run
- This was pre-run locally ✅
- If still seeing this, database was reset
- Can't fix without shell (but shouldn't happen)

#### Issue: "App taking 30+ seconds to respond"
**Normal:** Cold start on free tier
- First request takes 10-30 seconds
- Subsequent requests are instant
- This is expected behavior

### Service Won't Deploy
1. Check **Logs** for build errors
2. Ensure `requirements.txt` has all dependencies
3. Ensure `Procfile` exists
4. Try **Manual Deploy** button

---

## 🎯 After Deployment - Setup

### 1. Change Admin Password (Recommended)
- Login as admin@stockmaster.com / admin123
- Go to Profile → Change Password

### 2. Add Team Members
- Go to Settings → Users
- Add team email addresses
- Send them login URL

### 3. Add Inventory Data
Once logged in:
- Create Categories
- Create Warehouses & Locations
- Add Products
- Start tracking inventory!

### 4. Setup Email Notifications (Optional)
- Already configured with Gmail settings
- Low stock alerts will send automatically

---

## 📈 Performance Tips

### Optimize Response Times
1. Service should respond in 100-200ms
2. If slow, check database logs
3. First request cold start is normal

### Monitor Resource Usage
1. Dashboard → Overview
2. CPU/Memory usage shown
3. Free tier has limits, should be fine for small inventory

### Scale if Needed
- Add database replicas (paid)
- Increase workers in Procfile
- Use CDN for static files

---

## 🔐 Security Checklist

- [x] SECRET_KEY is set (random 32+ chars)
- [x] FLASK_ENV = production
- [x] DEBUG = False
- [x] Database credentials in environment variables
- [x] Email credentials secure
- [x] HTTPS enabled (Render provides free SSL)
- [ ] Change default admin password
- [ ] Configure firewall rules (if needed)

---

## 🗑️ Environment Variables Reference

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Random 32+ chars | `a7c3d8f2e9b1...` |
| `FLASK_ENV` | production | `production` |
| `DEBUG` | False for production | `False` |
| `MAIL_USERNAME` | Gmail email | `your-email@gmail.com` |
| `MAIL_PASSWORD` | Gmail app password | `16-char code` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |

---

## 🎊 Deployment Complete!

### ✅ What You Have:
- ✅ Live app at https://stockmaster.onrender.com
- ✅ PostgreSQL database with pricing schema
- ✅ Auto-deploy from GitHub
- ✅ Email notifications setup
- ✅ 100% free tier

### 📊 Stats:
- **Uptime:** 24/7
- **Cost:** Free
- **Auto-backup:** 7 days
- **Response time:** <200ms typical

---

## 📞 Support

### If Something Goes Wrong:
1. **Check Logs:** Service → Logs tab
2. **Check Status:** render-status.com
3. **Check Database:** Databases page
4. **Manual Deploy:** Click "Manual Deploy" button

### Common Help:
- Render Docs: https://render.com/docs
- Flask Docs: https://flask.palletsprojects.com
- PostgreSQL: https://www.postgresql.org/docs

---

## 🚀 Next: Make Changes

Your app is live! To make changes:

```powershell
# Edit files locally
# Test locally with: python app.py

# When ready:
git add .
git commit -m "feature: add new feature"
git push origin main

# Render auto-deploys in 30 seconds!
```

---

## 📋 Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| 1. Create account | 2 min | ✅ |
| 2. Create database | 3 min | ✅ |
| 3. Create web service | 3 min | ✅ |
| 4. Add env vars | 2 min | ✅ |
| 5. Get Gmail password | 2 min | ✅ |
| 6. Deploy | 1-2 min | ✅ |
| 7. Test | 1 min | ✅ |
| **Total** | **~15 min** | ✅ **LIVE!** |

---

**🎉 Your StockMaster is now deployed on Render!**

**Live URL:** https://stockmaster.onrender.com  
**Status:** Active 24/7  
**Cost:** Free  
**Auto-Deploy:** Enabled

**Happy inventory management! 📦**

---

*Last Updated: November 22, 2025*  
*Deployment Guide v1.0 - Render*
