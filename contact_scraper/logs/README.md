# Error Logs

This directory contains error logs for the contact scraper application.

## Log Files

### Contact Scraper Logs
- **File**: `error_YYYYMMDD.log`
- **Description**: Contains ERROR and CRITICAL level logs from the contact scraper CLI tool.
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Flask App Logs
- **File**: `flask_error_YYYYMMDD.log` - ERROR and CRITICAL level logs only
- **File**: `flask_app_YYYYMMDD.log` - All DEBUG level and above logs
- **Description**: Contains logs from the Flask web dashboard.
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Log Levels

- **DEBUG**: Detailed information for troubleshooting (Flask app only)
- **INFO**: General operational messages
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (actual failures)
- **CRITICAL**: Critical errors (application may be unstable)

## Common Error Types

### Request Errors
- **Timeout**: Server took too long to respond
- **HTTPError**: HTTP status code errors (404, 500, etc.)
- **ConnectionError**: Network connectivity issues

### File Errors
- **FileNotFoundError**: Input file or result file not found
- **PermissionError**: Insufficient permissions to read/write files

### Job Errors
- Job failures are logged with full stack traces for debugging

## Viewing Logs

```bash
# View today's error log (CLI)
cat logs/error_$(date +%Y%m%d).log

# View today's Flask error log
cat logs/flask_error_$(date +%Y%m%d).log

# View all Flask logs
cat logs/flask_app_$(date +%Y%m%d).log

# Follow logs in real-time
tail -f logs/error_*.log
```

## Log Rotation

Logs are created daily. Old logs are kept indefinitely. To clean up old logs:

```bash
# Delete logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```
