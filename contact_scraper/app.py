#!/usr/bin/env python3
"""
Contact Scraper Web Dashboard
Flask-based web UI with authentication, rate limiting, and live monitoring.
"""

import os
import json
import threading
import uuid
import logging
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps

import psutil
import redis
from flask import (
    Flask, render_template, request, jsonify, 
    send_file, redirect, url_for, flash, session
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user, 
    login_required, current_user
)
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from contact_scraper import ContactScraper, logger as scraper_logger

# Configure logging
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Create logger for Flask app
app_logger = logging.getLogger('flask_app')
app_logger.setLevel(logging.DEBUG)

# File handler for error logs
error_log_file = LOG_DIR / f'flask_error_{datetime.now().strftime("%Y%m%d")}.log'
file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
file_handler.setLevel(logging.ERROR)

# File handler for all logs
all_log_file = LOG_DIR / f'flask_app_{datetime.now().strftime("%Y%m%d")}.log'
all_file_handler = logging.FileHandler(all_log_file, encoding='utf-8')
all_file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
all_file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
app_logger.addHandler(file_handler)
app_logger.addHandler(all_file_handler)
app_logger.addHandler(console_handler)

app = Flask(__name__)

# Secret key for sessions (in production, use environment variable)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-2026')

# Enable CSRF protection
csrf = CSRFProtect(app)

# Configure Redis for caching and rate limiting
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=2
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
    app_logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except (redis.ConnectionError, redis.TimeoutError):
    redis_client = None
    REDIS_AVAILABLE = False
    app_logger.warning("Redis not available, using in-memory storage")

# Setup Flask-Limiter for rate limiting
if REDIS_AVAILABLE:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        default_limits=["100 per hour", "20 per minute"],
        strategy="fixed-window"
    )
else:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["100 per hour", "20 per minute"],
        strategy="fixed-window"
    )

# Setup Flask-Login for authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the dashboard'
login_manager.login_message_category = 'warning'

# Store scrape jobs
jobs = {}
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# User database (in production, use a real database)
USERS = {
    'techforge': {
        'id': 'techforge',
        'password_hash': generate_password_hash('2026'),
        'active': True
    }
}


class User(UserMixin):
    """User class for Flask-Login."""
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.active = USERS.get(user_id, {}).get('active', False)
    
    def is_authenticated(self):
        return self.active
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id in USERS:
        return User(user_id, user_id)
    return None


class LoginForm(FlaskForm):
    """Login form with CSRF protection."""
    pass


class ScraperForm(FlaskForm):
    """Scraper form with CSRF protection."""
    pass


def get_server_stats():
    """Get current server CPU and memory usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / (1024 ** 3), 2),
            'memory_total_gb': round(memory.total / (1024 ** 3), 2),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        app_logger.error(f"Error getting server stats: {e}")
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_used_gb': 0,
            'memory_total_gb': 0,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


def cache_get(key):
    """Get value from Redis cache."""
    if REDIS_AVAILABLE and redis_client:
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            app_logger.error(f"Redis cache get error: {e}")
    return None


def cache_set(key, value, ttl=3600):
    """Set value in Redis cache with TTL."""
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            app_logger.error(f"Redis cache set error: {e}")


def run_scraper_job(job_id: str, urls: list, timeout: int, max_pages: int):
    """Run scraper in background thread with live progress tracking."""
    try:
        app_logger.info(f"Starting job {job_id} for {len(urls)} URLs")
        jobs[job_id]['status'] = 'running'
        jobs[job_id]['started_at'] = datetime.now().isoformat()
        jobs[job_id]['start_time'] = time.time()
        jobs[job_id]['urls_total'] = len(urls)
        jobs[job_id]['urls_passed'] = 0
        jobs[job_id]['urls_failed'] = 0
        jobs[job_id]['processing_time'] = 0

        scraper = ContactScraper(timeout=timeout, max_pages=max_pages, results_dir=RESULTS_DIR)
        results = []

        for i, url in enumerate(urls, 1):
            jobs[job_id]['progress'] = int((i / len(urls)) * 100)
            jobs[job_id]['current_url'] = url
            jobs[job_id]['current_index'] = i
            app_logger.debug(f"Job {job_id}: Processing {url}")

            try:
                result = scraper.scrape_url(url)
                results.append(result)
                
                # Check if scraping was successful (found any contacts or at least completed)
                if result.get('emails') or result.get('phones') or result.get('addresses'):
                    jobs[job_id]['urls_passed'] += 1
                else:
                    # Consider it passed if no error but no contacts found
                    jobs[job_id]['urls_passed'] += 1
                    
            except Exception as e:
                app_logger.error(f"Error scraping {url}: {e}")
                jobs[job_id]['urls_failed'] += 1
                # Add failed result
                results.append({
                    'url': url,
                    'emails': [],
                    'phones': [],
                    'addresses': [],
                    'error': str(e)
                })
            
            # Update processing time
            jobs[job_id]['processing_time'] = round(time.time() - jobs[job_id]['start_time'], 2)
            
            # Cache live progress
            cache_set(f"job_progress:{job_id}", {
                'progress': jobs[job_id]['progress'],
                'current_url': jobs[job_id]['current_url'],
                'current_index': jobs[job_id]['current_index'],
                'urls_total': jobs[job_id]['urls_total'],
                'urls_passed': jobs[job_id]['urls_passed'],
                'urls_failed': jobs[job_id]['urls_failed'],
                'processing_time': jobs[job_id]['processing_time']
            }, ttl=300)

        # Save results in organized structure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save organized results
        organized_files = scraper.save_organized_results(results)
        
        # Also save traditional formats for compatibility
        csv_path = os.path.join(RESULTS_DIR, f'contacts_{timestamp}.csv')
        json_path = os.path.join(RESULTS_DIR, f'contacts_{timestamp}.json')
        scraper.save_to_csv(results, csv_path)
        scraper.save_to_json(results, json_path)

        jobs[job_id]['results'] = results
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        jobs[job_id]['end_time'] = time.time()
        jobs[job_id]['processing_time'] = round(jobs[job_id]['end_time'] - jobs[job_id]['start_time'], 2)
        jobs[job_id]['csv_file'] = os.path.basename(csv_path)
        jobs[job_id]['json_file'] = os.path.basename(json_path)
        jobs[job_id]['organized_files'] = {
            'emails': os.path.basename(organized_files['emails_csv']),
            'phones': os.path.basename(organized_files['phones_csv']),
            'addresses': os.path.basename(organized_files['addresses_csv']),
            'organized_json': os.path.basename(organized_files['organized_json']),
            'summary': os.path.basename(organized_files['summary'])
        }
        jobs[job_id]['total_found'] = {
            'emails': sum(len(r['emails']) for r in results),
            'phones': sum(len(r['phones']) for r in results),
            'addresses': sum(len(r['addresses']) for r in results)
        }

        # Cache final results
        cache_set(f"job_result:{job_id}", jobs[job_id], ttl=7200)

        app_logger.info(f"Job {job_id} completed successfully: {jobs[job_id]['total_found']}")

    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        jobs[job_id]['end_time'] = time.time()
        jobs[job_id]['processing_time'] = round(jobs[job_id]['end_time'] - jobs[job_id]['start_time'], 2)
        app_logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        cache_set(f"job_result:{job_id}", jobs[job_id], ttl=7200)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            error = 'Please enter both username and password'
        elif username not in USERS:
            error = 'Invalid username or password'
            app_logger.warning(f"Failed login attempt for unknown user: {username}")
        else:
            user_data = USERS[username]
            if check_password_hash(user_data['password_hash'], password):
                user = User(username, username)
                login_user(user, remember=remember)
                app_logger.info(f"User {username} logged in successfully")
                
                # Redirect to original destination or index
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                error = 'Invalid username or password'
                app_logger.warning(f"Failed login attempt for user: {username}")
    
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    """Logout endpoint."""
    logout_user()
    app_logger.info(f"User {current_user.username} logged out")
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Dashboard home page."""
    return render_template('dashboard.html')


@app.route('/api/scrape', methods=['POST'])
@login_required
@csrf.exempt  # We'll handle CSRF via headers in JS
@limiter.limit("5 per minute")
def start_scrape():
    """Start a new scrape job."""
    try:
        data = request.json

        # Get URLs from input or file
        urls_input = data.get('urls', '')
        urls_file = data.get('urls_file', '')

        urls = []
        if urls_input:
            urls = [u.strip() for u in urls_input.split('\n') if u.strip() and not u.strip().startswith('#')]
        elif urls_file:
            try:
                with open(urls_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                app_logger.info(f"Loaded {len(urls)} URLs from file: {urls_file}")
            except FileNotFoundError as e:
                app_logger.error(f"URL file not found: {urls_file}: {e}")
                return jsonify({'error': 'File not found'}), 400
            except PermissionError as e:
                app_logger.error(f"Permission denied reading file: {urls_file}: {e}")
                return jsonify({'error': 'Permission denied'}), 403
            except Exception as e:
                app_logger.error(f"Error reading URL file {urls_file}: {e}", exc_info=True)
                return jsonify({'error': 'Failed to read file'}), 500

        if not urls:
            app_logger.warning("No URLs provided in scrape request")
            return jsonify({'error': 'No URLs provided'}), 400

        # Create job
        job_id = str(uuid.uuid4())[:8]
        jobs[job_id] = {
            'id': job_id,
            'status': 'pending',
            'progress': 0,
            'urls_count': len(urls),
            'urls_total': len(urls),
            'urls_passed': 0,
            'urls_failed': 0,
            'current_url': None,
            'current_index': 0,
            'started_at': None,
            'completed_at': None,
            'start_time': None,
            'end_time': None,
            'processing_time': 0,
            'results': None,
            'error': None,
            'csv_file': None,
            'json_file': None,
            'organized_files': None,
            'total_found': None
        }

        # Start background thread
        timeout = data.get('timeout', 10)
        max_pages = data.get('max_pages', 5)

        app_logger.info(f"Created job {job_id} for {len(urls)} URLs by user {current_user.username}")

        thread = threading.Thread(
            target=run_scraper_job,
            args=(job_id, urls, timeout, max_pages)
        )
        thread.daemon = True
        thread.start()

        return jsonify({'job_id': job_id, 'message': 'Scrape job started'})
    except Exception as e:
        app_logger.error(f"Error starting scrape job: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/status/<job_id>')
@login_required
@limiter.limit("30 per minute")
def job_status(job_id):
    """Get job status with live progress."""
    try:
        # Try cache first
        cached = cache_get(f"job_progress:{job_id}")
        if cached and job_id in jobs:
            # Merge cached progress with job data
            jobs[job_id].update(cached)
        
        if job_id not in jobs:
            app_logger.warning(f"Job not found: {job_id}")
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(jobs[job_id])
    except Exception as e:
        app_logger.error(f"Error getting job status for {job_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/jobs')
@login_required
@limiter.limit("20 per minute")
def list_jobs():
    """List all jobs."""
    try:
        return jsonify(list(jobs.values()))
    except Exception as e:
        app_logger.error(f"Error listing jobs: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/download/<filename>')
@login_required
@limiter.limit("30 per minute")
def download_file(filename):
    """Download result file."""
    try:
        file_path = os.path.join(RESULTS_DIR, filename)
        if os.path.exists(file_path):
            app_logger.info(f"Downloading file: {filename}")
            return send_file(file_path, as_attachment=True)
        app_logger.warning(f"File not found for download: {filename}")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        app_logger.error(f"Error downloading file {filename}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/results/<job_id>')
@login_required
@limiter.limit("20 per minute")
def get_results(job_id):
    """Get job results."""
    try:
        if job_id not in jobs:
            app_logger.warning(f"Job not found: {job_id}")
            return jsonify({'error': 'Job not found'}), 404

        job = jobs[job_id]
        if job['status'] != 'completed':
            app_logger.warning(f"Job {job_id} not completed (status: {job['status']})")
            return jsonify({'error': 'Job not completed'}), 400

        return jsonify(job['results'])
    except Exception as e:
        app_logger.error(f"Error getting results for job {job_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/server-stats')
@login_required
@limiter.limit("60 per minute")
def server_stats():
    """Get live server statistics (CPU, Memory)."""
    try:
        stats = get_server_stats()
        
        # Add Redis status
        stats['redis_available'] = REDIS_AVAILABLE
        if REDIS_AVAILABLE:
            try:
                redis_info = redis_client.info('memory')
                stats['redis_memory_used'] = round(redis_info.get('used_memory_human', '0B'), 2)
            except:
                stats['redis_memory_used'] = 'N/A'
        
        # Add active jobs count
        stats['active_jobs'] = sum(1 for j in jobs.values() if j['status'] == 'running')
        stats['total_jobs'] = len(jobs)
        
        return jsonify(stats)
    except Exception as e:
        app_logger.error(f"Error getting server stats: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/csrf-token')
@login_required
def get_csrf_token():
    """Get CSRF token for AJAX requests."""
    return jsonify({'csrf_token': generate_csrf()})


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    if request.is_json:
        return jsonify({'error': 'Not found'}), 404
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    app_logger.warning(f"Rate limit exceeded for {request.remote_addr}")
    if request.is_json:
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    flash('Rate limit exceeded. Please try again later.', 'warning')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app_logger.error(f"Internal server error: {error}")
    if request.is_json:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    app_logger.info("Starting Flask contact scraper dashboard with authentication")
    app.run(debug=True, host='0.0.0.0', port=5000)
