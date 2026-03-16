# Contact Scraper - Enterprise Edition

A professional web-based contact scraper with **authentication**, **rate limiting**, **live progress tracking**, and **server monitoring**.

## 🚀 New Features (Enterprise Edition)

### 🔐 Security Features
- **User Authentication** - Secure login system (Username: `techforge`, Password: `2026`)
- **CSRF Protection** - Cross-Site Request Forgery protection on all forms
- **Rate Limiting** - Redis-based rate limiting to prevent abuse
  - Default: 100 requests/hour, 20 requests/minute
  - Login: 10 attempts/minute
  - API endpoints: Custom limits per endpoint

### 📊 Live Monitoring
- **Real-time Progress Tracking**
  - Live URL counter (Total, Passed, Failed)
  - Current URL being processed
  - Processing time timer
  - Progress bar with percentage
  
- **Server Monitor** (Top-right corner)
  - Live CPU usage (%)
  - Live Memory usage (%)
  - Active jobs count
  - Redis connection status

### 💾 Caching
- **Redis Caching** for job progress and results
- Automatic cache invalidation
- TTL-based cache expiration

---

## 📋 Login Credentials

```
Username: techforge
Password: 2026
```

⚠️ **Important**: Change these credentials in production by modifying the `USERS` dictionary in `app.py` or use environment variables.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Redis server (optional but recommended for rate limiting and caching)

### Install Dependencies

```bash
cd contact_scraper

# Activate virtual environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Install Redis (Optional but Recommended)

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew install redis
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

---

## 🚀 Usage

### Start the Web Dashboard

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python app.py
```

Then open your browser to: **http://localhost:5000**

### Login

1. You'll be redirected to the login page
2. Enter credentials:
   - **Username**: `techforge`
   - **Password**: `2026`
3. Click "Sign In"

### Start a Scrape Job

1. Enter URLs in the text area (one per line) OR upload a `.txt` file
2. Configure timeout and max pages
3. Click "Start Scraping"
4. Watch live progress in the "Live Progress" panel

### Monitor Server Resources

The server monitor in the top-right corner shows:
- **CPU Usage** - Current CPU utilization
- **Memory Usage** - RAM utilization
- **Active Jobs** - Number of running scrape jobs
- **Redis Status** - Connection status

---

## 📁 Organized Output Files

Each completed job generates **5 organized files**:

| File | Description |
|------|-------------|
| `contacts_emails_TIMESTAMP.csv` | All emails with source URLs |
| `contacts_phones_TIMESTAMP.csv` | All phone numbers with source URLs |
| `contacts_addresses_TIMESTAMP.csv` | All addresses with source URLs |
| `contacts_organized_TIMESTAMP.json` | Complete structured JSON |
| `contacts_summary_TIMESTAMP.txt` | Human-readable summary |

---

## 🔧 Configuration

### Environment Variables

```bash
# Secret key for sessions (REQUIRED in production)
export SECRET_KEY="your-secure-random-key-here"

# Redis configuration (optional)
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"
```

### Rate Limiting Configuration

Edit in `app.py`:

```python
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    default_limits=["100 per hour", "20 per minute"],  # Change here
    strategy="fixed-window"
)
```

### User Credentials

Edit in `app.py`:

```python
USERS = {
    'techforge': {
        'id': 'techforge',
        'password_hash': generate_password_hash('2026'),
        'active': True
    }
    # Add more users here
}
```

---

## 📊 API Endpoints

All API endpoints require authentication.

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/login` | POST | User login | 10/min |
| `/logout` | GET | User logout | - |
| `/api/scrape` | POST | Start scrape job | 5/min |
| `/api/status/<job_id>` | GET | Get job status | 30/min |
| `/api/jobs` | GET | List all jobs | 20/min |
| `/api/results/<job_id>` | GET | Get job results | 20/min |
| `/api/download/<filename>` | GET | Download result file | 30/min |
| `/api/server-stats` | GET | Get server statistics | 60/min |
| `/api/csrf-token` | GET | Get CSRF token | - |

---

## 🎯 Dashboard Features

### Live Progress Panel
- **Job ID** - Unique identifier for each job
- **Progress Bar** - Visual progress indicator (0-100%)
- **URL Counters** - Total, Passed, Failed counts
- **Current URL** - URL currently being processed
- **Processing Time** - Elapsed time timer

### Stats Dashboard
- Total jobs count
- Total emails found (cumulative)
- Total phones found (cumulative)
- Total addresses found (cumulative)

### Recent Jobs Table
- Job ID
- Status (Running/Completed/Failed)
- Number of URLs
- Progress percentage
- Results summary (emails, phones, addresses)
- Processing time
- Download actions

---

## 🔒 Security Best Practices

### For Production Deployment

1. **Change Default Credentials**
   ```python
   # In app.py
   USERS = {
       'your-username': {
           'id': 'your-username',
           'password_hash': generate_password_hash('strong-password'),
           'active': True
       }
   }
   ```

2. **Set Strong Secret Key**
   ```bash
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   ```

3. **Enable HTTPS**
   - Use a reverse proxy (nginx, Apache)
   - Obtain SSL certificate (Let's Encrypt)

4. **Configure Firewall**
   - Allow only necessary ports
   - Restrict access by IP if possible

5. **Enable Redis Authentication**
   ```bash
   # In redis.conf
   requirepass your-redis-password
   ```

---

## 🐛 Troubleshooting

### Redis Connection Error

```
Redis not available, using in-memory storage
```

**Solution**: Start Redis server
```bash
sudo systemctl start redis
# or
redis-server
```

### Rate Limit Exceeded

```
429 Too Many Requests
```

**Solution**: Wait a minute or increase rate limits in `app.py`

### Login Fails

**Solution**: 
1. Check username/password (default: `techforge`/`2026`)
2. Clear browser cookies
3. Check Flask logs for errors

### CSRF Token Error

**Solution**: 
1. Refresh the page
2. Clear browser cache
3. Ensure JavaScript is enabled

---

## 📝 Logs

Logs are stored in `logs/` directory:

- `flask_error_YYYYMMDD.log` - Error logs
- `flask_app_YYYYMMDD.log` - All application logs
- `error_YYYYMMDD.log` - Scraper error logs

View logs:
```bash
# View today's error log
tail -f logs/flask_error_$(date +%Y%m%d).log

# View all logs
tail -f logs/flask_app_*.log
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│                  (Dashboard UI)                         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Flask Application                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Auth       │  │   Rate       │  │   CSRF       │  │
│  │  (Login)    │  │   Limiting   │  │  Protection  │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Live      │  │   Server     │  │   Contact    │  │
│  │  Progress   │  │  Monitoring  │  │   Scraper    │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└────────────┬──────────────────────────────┬───────────┘
             │                              │
             ▼                              ▼
    ┌────────────────┐            ┌────────────────┐
    │     Redis      │            │  File System   │
    │  - Caching     │            │  - Results     │
    │  - Rate Limit  │            │  - Logs        │
    └────────────────┘            └────────────────┘
```

---

## 📄 License

MIT License - Feel free to modify and use for your projects!

---

## 🤝 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review this README
3. Check Flask console output

---

## 🎉 Features Summary

✅ **Authentication** - Secure login system  
✅ **CSRF Protection** - Form security  
✅ **Rate Limiting** - Redis-based API protection  
✅ **Redis Caching** - Fast data access  
✅ **Live Progress** - Real-time job tracking  
✅ **URL Counters** - Total/Passed/Failed  
✅ **Processing Timer** - Live elapsed time  
✅ **Server Monitor** - CPU & Memory usage  
✅ **Organized Output** - Separate files by type  
✅ **Error Logging** - Comprehensive logging  
✅ **Responsive UI** - Mobile-friendly design  
✅ **Download Options** - Multiple export formats
