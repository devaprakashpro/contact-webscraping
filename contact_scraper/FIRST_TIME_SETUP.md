# 🚀 First Time Setup - Contact Scraper Enterprise

## Quick Start (One Command!)

```bash
./start.sh
```

That's it! The script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Check/install Redis (optional)
5. ✅ Create required directories
6. ✅ Start the Flask application

Then open your browser to: **http://localhost:5000**

---

## 📋 Login Credentials

```
Username: techforge
Password: 2026
```

---

## 📦 What the Setup Script Does

### Step-by-Step Breakdown

```
╔════════════════════════════════════════════════════════╗
║   Contact Scraper - Enterprise Edition Setup          ║
╚════════════════════════════════════════════════════════╝

[INFO] Step 1/7: Checking Python installation...
[✓] Python found: Python 3.10.12

[INFO] Step 2/7: Setting up virtual environment...
[✓] Virtual environment created
[✓] Virtual environment activated

[INFO] Step 3/7: Installing Python dependencies...
[✓] All Python dependencies installed

[INFO] Step 4/7: Checking Redis installation...
[✓] Redis is running

[INFO] Step 5/7: Creating required directories...
[✓] Created logs/ directory
[✓] Created results/ directory

[INFO] Step 6/7: Setting file permissions...
[✓] Permissions set

[INFO] Step 7/7: Starting Flask application...

╔════════════════════════════════════════════════════════╗
║              Setup Complete! Starting Server...        ║
╚════════════════════════════════════════════════════════╝

  ✓ Application URL: http://localhost:5000

  ✓ Login Credentials:
      Username: techforge
      Password: 2026

  ✓ Redis Status: Connected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press Ctrl+C to stop the server

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔧 Manual Installation (If start.sh fails)

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv redis-server

# Clone/navigate to project
cd contact_scraper

# Run setup script
./start.sh
```

### macOS

```bash
# Install system dependencies
brew install python3 redis

# Clone/navigate to project
cd contact_scraper

# Run setup script
./start.sh
```

### CentOS/RHEL

```bash
# Install system dependencies
sudo yum install -y python3 python3-pip redis

# Clone/navigate to project
cd contact_scraper

# Run setup script
./start.sh
```

---

## 🐛 Troubleshooting

### Error: Python 3 not found

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# macOS
brew install python3

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### Error: Permission denied

**Solution:**
```bash
chmod +x start.sh
./start.sh
```

### Error: Redis not available

**Solution (Optional - app works without Redis):**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
```

### Error: Port 5000 already in use

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or edit app.py to use different port
# Change: app.run(..., port=5000)
# To: app.run(..., port=5001)
```

### Error: pip install fails

**Solution:**
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Then run setup again
./start.sh
```

---

## 📁 Project Structure After Setup

```
contact_scraper/
├── start.sh                  ← One-command setup script
├── app.py                    ← Flask web application
├── contact_scraper.py        ← Core scraping logic
├── requirements.txt          ← Python dependencies
├── websites.txt              ← Sample URLs file
├── README.md                 ← Main documentation
├── README_ENTERPRISE.md      ← Enterprise features docs
├── QUICKSTART.md             ← Quick start guide
├── OUTPUT_STRUCTURE.md       ← Output files explanation
├── venv/                     ← Virtual environment (created)
├── logs/                     ← Log files (created)
│   ├── flask_app_*.log
│   ├── flask_error_*.log
│   └── error_*.log
├── results/                  ← Scraped results (created)
│   ├── contacts_emails_*.csv
│   ├── contacts_phones_*.csv
│   ├── contacts_addresses_*.csv
│   ├── contacts_organized_*.json
│   └── contacts_summary_*.txt
├── templates/                ← HTML templates
│   ├── dashboard.html
│   ├── login.html
│   └── error.html
└── static/                   ← Static files (CSS, JS)
```

---

## ✅ Verification Checklist

After running `./start.sh`, verify:

- [ ] Virtual environment created (`venv/` directory exists)
- [ ] All dependencies installed (no pip errors)
- [ ] Directories created (`logs/`, `results/`, `templates/`, `static/`)
- [ ] Flask server starts without errors
- [ ] Can access http://localhost:5000
- [ ] Can login with credentials
- [ ] Server monitor shows in top-right corner

---

## 🎯 Next Steps After Setup

1. **Open Browser**: http://localhost:5000
2. **Login**: Use credentials `techforge` / `2026`
3. **Enter URLs**: Type or upload URLs to scrape
4. **Start Scraping**: Click "Start Scraping" button
5. **Monitor Progress**: Watch live progress updates
6. **Download Results**: Get CSV, JSON, or summary files

---

## 📊 Features Available

### Live Dashboard
- ✅ Real-time server monitoring (CPU, Memory)
- ✅ Live job progress tracking
- ✅ URL counters (Total/Passed/Failed)
- ✅ Processing time timer
- ✅ Recent jobs table

### Security
- ✅ User authentication
- ✅ CSRF protection
- ✅ Rate limiting (Redis-based)
- ✅ Session management

### Output
- ✅ Organized CSV files (emails, phones, addresses)
- ✅ Structured JSON output
- ✅ Summary reports
- ✅ One-click downloads

---

## 🔄 Updating Dependencies

If you need to update dependencies later:

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 🧹 Cleanup (If Needed)

To remove everything and start fresh:

```bash
# Deactivate virtual environment
deactivate 2>/dev/null || true

# Remove virtual environment
rm -rf venv

# Remove installed packages
rm -rf __pycache__
rm -rf *.pyc

# Remove logs and results (optional)
rm -rf logs/*
rm -rf results/*

# Run setup again
./start.sh
```

---

## 📞 Support

### Check Logs
```bash
# View latest errors
tail -f logs/flask_error_*.log

# View all logs
tail -f logs/flask_app_*.log
```

### System Requirements
- Python 3.8 or higher
- 1GB RAM minimum (2GB recommended)
- 500MB free disk space
- Redis server (optional but recommended)

---

## 🎉 You're Ready!

Just run:
```bash
./start.sh
```

And start scraping! 🚀

---

**Happy Scraping!** 🎊
