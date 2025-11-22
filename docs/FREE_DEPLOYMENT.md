# Free Deployment Guide for StockMaster

Deploy StockMaster completely free using GitHub + free tier services.

## Free Deployment Options

### 1. **Render + Railway** (RECOMMENDED - Actually Free)
Render and Railway both offer genuine free tiers with no credit card required for initial projects.

### 2. **Heroku Free Tier** (DEPRECATED - No longer free)
❌ Heroku removed free tier in November 2022

### 3. **Vercel** (Frontend only)
❌ Not suitable for Python/Flask backend

---

## Option 1: Render.com (Best Free Option)

### ✅ Features
- **Free tier:** 1 free tier web service
- **Database:** Free PostgreSQL (included)
- **Bandwidth:** Unlimited
- **Uptime:** No auto-sleep (unlike Heroku)
- **No credit card required initially**

### Step-by-Step

#### 1. Prepare GitHub Repository
```bash
# Make sure code is pushed to GitHub
git status
git add -A
git commit -m "ready for deployment"
git push origin main
```

#### 2. Create Render Account
- Go to https://render.com
- Click "Sign up with GitHub"
- Authorize Render to access your repositories

#### 3. Create Web Service
1. Dashboard → **New +** → **Web Service**
2. Select repository: `OdooxSPIT`
3. Configure:
   - **Name:** `stockmaster`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free

#### 4. Add Environment Variables
In service settings → **Environment**:
```
DATABASE_URL=<will be set from database service>
SECRET_KEY=<generate one>
FLASK_ENV=production
MAIL_USERNAME=<your-gmail>
MAIL_PASSWORD=<your-gmail-app-password>
DEBUG=False
```

#### 5. Create PostgreSQL Database
1. Dashboard → **New +** → **PostgreSQL**
2. Configure:
   - **Name:** `stockmaster-db`
   - **Database:** `stockmaster`
   - **User:** `stockmaster_user`
   - **Region:** Choose closest to you
   - **Instance Type:** Free
3. Note the connection string → Copy to `DATABASE_URL`

#### 6. Deploy
Click **Deploy** → Render automatically deploys from GitHub

#### 7. Run Migrations
Once deployed, open shell in Render:
1. Dashboard → Service → `stockmaster`
2. Click **Shell** tab
3. Run migration:
```bash
python migrations/migrate_add_pricing.py
```

**Access your app:** https://stockmaster.onrender.com

---

## Option 2: Railway.app (Free Tier)

### ✅ Features
- **Free tier:** $5 monthly credit (enough for 1 app)
- **Auto-deployment from GitHub**
- **PostgreSQL included**
- **Much faster than Render**

### Step-by-Step

#### 1. Create Railway Account
- Go to https://railway.app
- Sign up with GitHub

#### 2. Create New Project
1. Click **Create New Project**
2. Select **Deploy from GitHub**
3. Choose `OdooxSPIT` repository
4. Authorize access

#### 3. Configure Services

**Web Service (App):**
- Select from detected services
- Start Command: `gunicorn app:app`
- Port: `8000`

**PostgreSQL Database:**
- Click **Add** → **PostgreSQL**
- Automatically configured

#### 4. Set Environment Variables
In Variables tab:
```
DATABASE_URL=postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/{{Postgres.PGDATABASE}}
SECRET_KEY=<generate>
FLASK_ENV=production
MAIL_USERNAME=<your-gmail>
MAIL_PASSWORD=<your-gmail-app-password>
```

#### 5. Deploy
Push to GitHub → Railway auto-deploys

**Access your app:** https://your-app-name.up.railway.app

---

## Option 3: Fly.io (Free Tier with Credit)

### ✅ Features
- **Free tier:** $5 monthly credit (sufficient for small app)
- **Global deployment**
- **PostgreSQL available**

### Step-by-Step

#### 1. Install Fly CLI
```bash
# Windows - using Powershell
iwr https://fly.io/install.ps1 -useb | iex

# Mac
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

#### 2. Create Fly Account
```bash
flyctl auth signup
```

#### 3. Create Fly App
```bash
cd e:\STOCKMASTER_ODOO
flyctl launch

# When prompted:
# - App name: stockmaster
# - Region: Choose closest
# - Database: Yes, PostgreSQL
# - Scaling: 1 VM
```

#### 4. Set Environment Variables
```bash
flyctl secrets set \
  SECRET_KEY="your-secret-key" \
  FLASK_ENV=production \
  MAIL_USERNAME=your-email@gmail.com \
  MAIL_PASSWORD=your-app-password
```

#### 5. Deploy
```bash
flyctl deploy
```

**Access your app:** https://stockmaster.fly.dev

---

## Free Database Options

### 1. **Render PostgreSQL** (Recommended)
- Included with Render web service free tier
- 256MB storage
- Completely free

### 2. **Railway PostgreSQL**
- Included in $5 credit
- 5GB storage
- Completely free (within credits)

### 3. **Fly PostgreSQL**
- Part of Fly app deployment
- Included in $5 credit
- Completely free

### 4. **Self-hosted on Oracle Cloud** (Advanced)
- https://www.oracle.com/cloud/free/
- 2 vCPU, 1GB RAM always free
- Good for learning, not recommended for production

---

## Generate SECRET_KEY (Required)

```powershell
# Windows PowerShell
python -c "import secrets; print(secrets.token_hex(32))"
```

Example output: `a7c3d8f2e9b1a4c6e8f0d2b4a6c8e0f2a4c6e8f0d2b4a6c8e0f2a4c6e8f0`

---

## Get Gmail App Password (For Email Notifications)

**Without Gmail 2FA:**
Use your regular Gmail password

**With Gmail 2FA (Recommended):**
1. Go to https://myaccount.google.com/apppasswords
2. Select: Mail → Windows Computer
3. Generate 16-character password
4. Use that as `MAIL_PASSWORD`

---

## Deployment Comparison

| Platform | Cost | Setup Time | Start Time | Storage | Database | Best For |
|----------|------|-----------|-----------|---------|----------|----------|
| **Render** | Free | 10 min | 30s | 256MB | PostgreSQL | Best overall |
| **Railway** | Free* | 10 min | 5s | 5GB | PostgreSQL | Fastest |
| **Fly.io** | Free* | 15 min | 10s | 3GB | PostgreSQL | Global |

*Within free tier credit

---

## Quick Deploy Checklist

- [ ] Code pushed to GitHub (`git push origin main`)
- [ ] GitHub account created
- [ ] Choose platform (Render recommended)
- [ ] Create account on platform
- [ ] Connect GitHub repository
- [ ] Generate `SECRET_KEY` 
- [ ] Configure environment variables
- [ ] Deploy
- [ ] Run database migrations
- [ ] Test at: https://your-app-url.com

---

## Verify Deployment

### Test if app is running
```bash
# Replace with your actual URL
curl https://stockmaster.onrender.com
curl https://your-app.up.railway.app
curl https://stockmaster.fly.dev
```

### Check logs
**Render:**
Dashboard → Service → Logs tab

**Railway:**
Dashboard → Project → Deployments → Logs

**Fly.io:**
```bash
flyctl logs
```

---

## Common Issues & Fixes

### "Application Error" or "502 Bad Gateway"
```bash
# Check if migrations ran
# Render: Click Shell → python migrations/migrate_add_pricing.py
# Railway: Check logs for errors
# Fly: flyctl ssh console → python migrations/migrate_add_pricing.py
```

### "ModuleNotFoundError"
- Ensure `requirements.txt` is in root directory
- Check build logs for pip install errors

### "DatabaseConnectionError"
- Verify `DATABASE_URL` is correct
- Render: DB connection auto-set
- Railway: Use provided connection string

### "Cold Starts" (App takes 10+ seconds)
- Normal on free tier
- Render/Railway/Fly all have cold starts
- Not noticeable for internal use

---

## After Deployment

### 1. Test Features
```
http://your-app-url/login
http://your-app-url/dashboard
http://your-app-url/products
```

Default credentials:
- Email: `admin@stockmaster.com`
- Password: `admin123`

### 2. Create Custom Domain (Optional, Free)
- Render: Settings → Custom Domain → Add domain
- Railway: Add custom domain in settings
- Use free domain from: https://freenom.com or https://www.github.io

### 3. Setup Monitoring (Optional)
- Enable Render/Railway notifications
- Monitor logs regularly
- Set up GitHub Actions for auto-testing

### 4. Backup Database (Optional)
```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Keep backups in GitHub Releases or Google Drive
```

---

## Free Options Comparison

| Feature | Render | Railway | Fly.io |
|---------|--------|---------|--------|
| Free Tier | ✅ Genuine | ✅ $5 Credit | ✅ $5 Credit |
| Setup | Easy | Easy | Medium |
| Speed | Medium | Fast | Fast |
| UI | Great | Great | CLI |
| Support | Good | Great | Good |

### **Recommendation:** Start with **Render** - simplest, genuinely free

---

## Next Steps

1. Choose platform (Render recommended)
2. Follow deployment steps above
3. Test app at provided URL
4. Share link with team
5. Monitor logs in dashboard

---

## Cost Breakdown After 1 Year

| Platform | Cost |
|----------|------|
| Render | $0 (Free tier) |
| Railway | $0 (Monthly $5 covers) |
| Fly.io | $0 ($5 credit covers) |
| Custom Domain | $0-12/year (optional) |
| Email Service | $0 (Gmail free) |

**Total:** Completely free! 🎉

---

**Last Updated:** November 22, 2025  
**Version:** Free Deployment 1.0
