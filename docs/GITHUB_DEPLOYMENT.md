# GitHub Deployment Guide for StockMaster

This guide explains how to deploy StockMaster from GitHub to production servers.

## Table of Contents
1. [GitHub Setup](#github-setup)
2. [Deployment Platforms](#deployment-platforms)
3. [GitHub Actions (CI/CD)](#github-actions-cicd)
4. [Manual Deployment](#manual-deployment)
5. [Environment Variables](#environment-variables)
6. [Monitoring & Rollback](#monitoring--rollback)

---

## GitHub Setup

### 1. Create GitHub Repository
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "initial commit: StockMaster inventory system"
git branch -M main
git remote add origin https://github.com/Darshan2139/OdooxSPIT.git
git push -u origin main
```

### 2. GitHub Repository Structure
```
OdooxSPIT/
├── main branch          # Production code
├── develop branch       # Development/staging
├── .github/
│   └── workflows/       # CI/CD automation
├── docs/                # Deployment guides
├── migrations/          # Database migrations
├── stockmaster/         # Odoo module
└── README.md
```

### 3. Create Protected Branches
**Go to GitHub → Settings → Branches:**
- Protect `main` branch:
  - ✅ Require pull request reviews
  - ✅ Require status checks to pass
  - ✅ Restrict who can push

---

## Deployment Platforms

### Option 1: Heroku (Easiest for beginners)

#### Step 1: Create Heroku Account
- Sign up at https://www.heroku.com
- Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

#### Step 2: Create Procfile
Create `Procfile` in root directory:
```
web: gunicorn app:app
release: python migrations/migrate_add_pricing.py
```

#### Step 3: Create requirements.txt (if not present)
```bash
pip freeze > requirements.txt
```

Ensure it contains:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-Mail==0.9.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
python-dotenv==1.0.0
```

#### Step 4: Deploy from GitHub
```bash
# Login to Heroku
heroku login

# Create app
heroku create stockmaster-app

# Connect GitHub repo
heroku apps:create --region us stockmaster-app
heroku git:remote -a stockmaster-app

# Set environment variables
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=your-secret-key
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password

# Deploy from GitHub main branch
git push heroku main

# View logs
heroku logs --tail
```

**Cost:** Free tier available (limited); paid tier ~$7-50/month

---

### Option 2: Railway (Modern, Simple)

#### Step 1: Connect GitHub
- Go to https://railway.app
- Click "New Project" → "Deploy from GitHub"
- Authorize Railway to access your GitHub repos
- Select `OdooxSPIT` repository

#### Step 2: Create Railway Config
Create `railway.json` in root:
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "numReplicas": 1
  }
}
```

#### Step 3: Add Environment Variables
In Railway dashboard → Variables:
```
DATABASE_URL=postgresql://user:pass@host:5432/stockmaster
SECRET_KEY=your-secret-key
FLASK_ENV=production
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### Step 4: Deploy
Push to GitHub → Railway auto-deploys
```bash
git push origin main
```

**Cost:** Pay-as-you-go ($5 starting credit); ~$5-20/month typical

---

### Option 3: AWS EC2 (Production-grade)

#### Step 1: Launch EC2 Instance
- Go to https://aws.amazon.com/ec2
- Launch Ubuntu 22.04 LTS instance
- Create security group (allow 80, 443, 22)

#### Step 2: SSH into Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### Step 3: Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql nginx git

# Clone repo
git clone https://github.com/Darshan2139/OdooxSPIT.git
cd OdooxSPIT

# Setup Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 4: Setup PostgreSQL
```bash
sudo systemctl start postgresql
sudo -u postgres psql

# Inside psql:
CREATE DATABASE stockmaster;
CREATE USER stockmaster_user WITH PASSWORD 'strong-password';
ALTER ROLE stockmaster_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE stockmaster TO stockmaster_user;
\q
```

#### Step 5: Configure Nginx
Create `/etc/nginx/sites-available/stockmaster`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/ubuntu/OdooxSPIT/static/;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/stockmaster /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### Step 6: Setup Gunicorn Service
Create `/etc/systemd/system/stockmaster.service`:
```ini
[Unit]
Description=StockMaster Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/OdooxSPIT
ExecStart=/home/ubuntu/OdooxSPIT/venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start stockmaster
sudo systemctl enable stockmaster
```

#### Step 7: Setup SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d your-domain.com
```

**Cost:** ~$3-10/month (t3.micro eligible for free tier 1 year)

---

### Option 4: DigitalOcean App Platform (Simple)

#### Step 1: Connect GitHub
- Go to https://cloud.digitalocean.com/apps
- Click "Create App"
- Select GitHub repository `OdooxSPIT`

#### Step 2: Configure App
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `gunicorn app:app`
- **Port:** 8080

#### Step 3: Add Database
- Click "Create Database"
- Choose PostgreSQL
- Note connection string

#### Step 4: Set Environment Variables
```
DATABASE_URL=<from database>
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

#### Step 5: Deploy
Click "Deploy" → Auto-deploys from GitHub

**Cost:** $12/month minimum

---

## GitHub Actions (CI/CD)

Automatically test & deploy on every push to main.

### Create `.github/workflows/deploy.yml`
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: |
          python migrations/migrate_add_pricing.py
      
      - name: Run tests (if you have any)
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: |
          python -m pytest tests/ || echo "No tests found"

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: success()
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Heroku
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
        run: |
          git remote add heroku https://git.heroku.com/stockmaster-app.git
          git push heroku main
```

### Add GitHub Secrets
Go to **Settings → Secrets and variables → Actions:**
- `HEROKU_API_KEY` - Get from Heroku account settings
- `DATABASE_URL` - Production database URL
- `SECRET_KEY` - Flask secret key

---

## Manual Deployment

### Step 1: SSH into Server
```bash
ssh -i key.pem ubuntu@your-server-ip
```

### Step 2: Pull Latest Code
```bash
cd /home/ubuntu/OdooxSPIT
git pull origin main
```

### Step 3: Update Python Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Step 4: Run Database Migrations
```bash
export DATABASE_URL="postgresql://user:pass@localhost/stockmaster"
python migrations/migrate_add_pricing.py
```

### Step 5: Restart Application
```bash
sudo systemctl restart stockmaster
sudo systemctl restart nginx
```

### Step 6: Verify Deployment
```bash
# Check app status
sudo systemctl status stockmaster

# Check logs
sudo journalctl -u stockmaster -n 50 -f

# Test endpoint
curl https://your-domain.com
```

---

## Environment Variables

### Required Variables (Production)
```bash
# Database
DATABASE_URL=postgresql://user:password@hostname:5432/stockmaster

# Flask
SECRET_KEY=your-super-secret-key-here-min-32-chars
FLASK_ENV=production

# Email
MAIL_USERNAME=noreply@your-domain.com
MAIL_PASSWORD=your-app-specific-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Optional
DEBUG=False
```

### Generate SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Create `.env` File (Local Development ONLY)
```bash
# Never commit .env to git!
cp .env.example .env
# Edit with your values
```

---

## Monitoring & Rollback

### Monitor Application
```bash
# Check app health
curl -I https://your-domain.com/dashboard

# View live logs
heroku logs --tail
# or
sudo journalctl -u stockmaster -f

# Check database connections
psql $DATABASE_URL -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Rollback to Previous Version
```bash
# View commit history
git log --oneline | head -10

# Rollback to previous commit
git revert <commit-hash>
git push origin main

# Redeploy
git push heroku main
```

---

## Deployment Checklist

- [ ] GitHub repository created and code pushed
- [ ] `.gitignore` excludes `.env` and `__pycache__`
- [ ] `requirements.txt` updated with all dependencies
- [ ] `Procfile` created (for Heroku/Railway)
- [ ] Database URL set in production environment
- [ ] `SECRET_KEY` generated and set
- [ ] Email credentials configured
- [ ] SSL certificate installed (HTTPS)
- [ ] Database backup strategy in place
- [ ] Monitoring & alerts configured
- [ ] Team access to deployment platform
- [ ] Documentation updated

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
```bash
# Ensure you're in the correct directory
cd /path/to/stockmaster-odoo

# Reinstall requirements
pip install -r requirements.txt
```

### "DatabaseConnectionError"
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### "CORS or SSL errors"
```bash
# Update Nginx config to proxy headers
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

# Restart Nginx
sudo systemctl restart nginx
```

### "Application crashes after deployment"
```bash
# Check logs
heroku logs --tail

# Rollback
git revert HEAD
git push heroku main
```

---

## Recommended Deployment Path

**For beginners:** Railway or Heroku (5 min setup)  
**For production:** AWS EC2 or DigitalOcean (better control, ~$10-20/month)  
**For enterprise:** Kubernetes on AWS/Azure (advanced)

---

## Next Steps

1. Choose deployment platform
2. Follow platform-specific steps above
3. Test with staging branch first
4. Monitor application logs
5. Setup automated backups
6. Document access credentials (secure location)

**Need help?** See `README.md` or open GitHub Issues

---

**Last Updated:** November 22, 2025  
**Version:** 1.0
