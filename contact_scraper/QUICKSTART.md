# 🚀 Quick Start Guide

## Start the Dashboard

```bash
cd /home/devaprakashr/contact_scraper
source venv/bin/activate
python app.py
```

Then open: **http://localhost:5000**

---

## 🔐 Login Credentials

```
Username: techforge
Password: 2026
```

---

## 📊 Features Overview

### 1. Live Server Monitor (Top-Right Corner)
Shows real-time:
- **CPU Usage** - Processor load percentage
- **Memory Usage** - RAM consumption percentage  
- **Active Jobs** - Currently running scrape jobs
- **Redis Status** - Cache connection indicator

### 2. Live Progress Tracking
When a job runs, you'll see:
- **Progress Bar** - 0-100% completion
- **URL Counters**:
  - 🔵 Total - Total URLs to process
  - 🟢 Passed - Successfully processed URLs
  - 🔴 Failed - Failed URLs
- **Current URL** - URL being processed now
- **Processing Time** - Live timer (MM:SS format)

### 3. Dashboard Stats
- Total Jobs - All jobs count
- Emails Found - Cumulative email count
- Phones Found - Cumulative phone count
- Addresses Found - Cumulative address count

### 4. Recent Jobs Table
Shows all jobs with:
- Job ID
- Status (Running/Completed/Failed)
- URL count
- Progress percentage
- Results (emails, phones, addresses badges)
- Processing time
- Download buttons (CSV, Summary)

---

## 🎯 Using the Scraper

### Step 1: Enter URLs
**Option A** - Type URLs:
```
https://example.com
https://company.com/contact
```

**Option B** - Upload file:
- Click "Upload URL File"
- Select `.txt` file with one URL per line

### Step 2: Configure Settings
- **Timeout**: Request timeout in seconds (default: 10)
- **Max Pages**: Max contact pages to check (default: 5)

### Step 3: Start Scraping
Click "Start Scraping" button

### Step 4: Monitor Progress
Watch the Live Progress panel for:
- Real-time progress updates
- URL counters (passed/failed)
- Current URL being processed
- Elapsed time

### Step 5: Download Results
After completion:
- Click download icon for CSV
- Click document icon for summary report

---

## 📁 Output Files

Each job creates 5 files in `results/`:

1. **contacts_emails_TIMESTAMP.csv** - All emails
2. **contacts_phones_TIMESTAMP.csv** - All phones
3. **contacts_addresses_TIMESTAMP.csv** - All addresses
4. **contacts_organized_TIMESTAMP.json** - Complete JSON
5. **contacts_summary_TIMESTAMP.txt** - Summary report

---

## 🔒 Security Features

### Authentication
- Login required for all pages
- Session-based authentication
- Remember me option

### CSRF Protection
- All forms have CSRF tokens
- Automatic token validation
- Prevents cross-site attacks

### Rate Limiting
- **Login**: 10 attempts/minute
- **Scrape API**: 5 requests/minute
- **Status API**: 30 requests/minute
- **Download**: 30 requests/minute

---

## 🛠️ Troubleshooting

### Can't Login?
- Check credentials: `techforge` / `2026`
- Clear browser cookies
- Refresh page

### Redis Not Connected?
```bash
# Start Redis
sudo systemctl start redis
# or
redis-server
```

### Rate Limit Exceeded?
- Wait 1 minute
- Or increase limits in `app.py`

### Server Monitor Not Updating?
- Check browser console for errors
- Ensure JavaScript is enabled
- Refresh page

---

## 📝 Logs

View logs in `logs/` directory:

```bash
# View Flask error log
tail -f logs/flask_error_*.log

# View all logs
tail -f logs/flask_app_*.log
```

---

## 🎨 UI Elements

### Server Monitor (Fixed Top-Right)
```
┌─────────────────────┐
│ ● Server Monitor   │
├─────────────────────┤
│ 🖥️ CPU      45%    │
│ ████████░░░░░░░    │
│ 💾 Memory   62%    │
│ ███████████░░░░    │
│ ⚡ Active Jobs: 2  │
│ ● Redis: Connected │
└─────────────────────┘
```

### Live Progress Panel
```
┌─────────────────────────────┐
│ ● Processing Job: abc12345 │
├─────────────────────────────┤
│ ████████████░░░░  75%      │
├─────────────────────────────┤
│  Total   Passed   Failed   │
│   10       8        2      │
├─────────────────────────────┤
│ 📍 Current:                │
│ https://example.com/page   │
├─────────────────────────────┤
│ Processing Time: 02:35     │
└─────────────────────────────┘
```

---

## 💡 Tips

1. **Batch URLs**: Upload large URL lists via file
2. **Monitor Resources**: Watch CPU/Memory for heavy jobs
3. **Adjust Timeout**: Increase for slow websites
4. **Check Summary**: View summary file for quick overview
5. **Rate Limits**: Space out large scraping jobs

---

## 📞 Support

Check logs for errors:
```bash
cd /home/devaprakashr/contact_scraper
cat logs/flask_error_$(date +%Y%m%d).log
```

---

**Enjoy scraping! 🚀**
