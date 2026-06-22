# Contact Details Web Scraper

## 🚀 Quick Start (One Command!)

```bash
./start.sh
```

That's it! The setup script will:
- ✅ Install all dependencies automatically
- ✅ Create virtual environment
- ✅ Check/install Redis (optional)
- ✅ Create required directories
- ✅ Start the Flask application

Then open: **http://localhost:5000**

**Login Credentials:**
- Username: `techforge`
- Password: `2026`

---

## 📚 Documentation

- **[FIRST_TIME_SETUP.md](FIRST_TIME_SETUP.md)** - Complete setup guide
- **[README_ENTERPRISE.md](README_ENTERPRISE.md)** - Enterprise features documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick usage guide
- **[OUTPUT_STRUCTURE.md](OUTPUT_STRUCTURE.md)** - Output files explanation

---

- ✅ Extract email addresses
- ✅ Extract phone numbers
- ✅ Extract physical addresses
- ✅ Automatically finds contact pages
- ✅ Works with business directories and company websites
- ✅ Export to CSV and JSON

## Installation

```bash
# Navigate to the scraper directory
cd contact_scraper

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python contact_scraper.py https://example.com
```

### Multiple URLs
```bash
python contact_scraper.py https://company1.com https://company2.com https://company3.com
```

### From a File (Recommended for many URLs)
```bash
# Create a file with one URL per line
python contact_scraper.py -f websites.txt
```

**websites.txt format:**
```
# Comments start with #
example.com
https://company1.com
https://company2.com/contact
```

### Organized Output (Default)
By default, results are saved in an organized structure with separate files:

```bash
python contact_scraper.py https://example.com
```

**Output files generated:**
- `contacts_emails_TIMESTAMP.csv` - All emails with source URLs
- `contacts_phones_TIMESTAMP.csv` - All phone numbers with source URLs
- `contacts_addresses_TIMESTAMP.csv` - All addresses with source URLs
- `contacts_organized_TIMESTAMP.json` - Complete organized JSON structure
- `contacts_summary_TIMESTAMP.txt` - Human-readable summary report

### Traditional Output Format
```bash
# CSV only
python contact_scraper.py https://example.com -o csv --organized false

# JSON only
python contact_scraper.py https://example.com -o json --organized false

# Both (default)
python contact_scraper.py https://example.com -o both --organized false
```

### Specify Results Directory
```bash
python contact_scraper.py -f websites.txt --results-dir my_results
```

### Advanced Options
```bash
python contact_scraper.py https://example.com --timeout 15 --max-pages 10
```

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output format: csv, json, or both | both |
| `--timeout` | Request timeout in seconds | 10 |
| `--max-pages` | Max contact pages to check per site | 5 |

## Output Files

### Organized Output (Default)

When using organized output (default), you get **5 separate files**:

#### 1. Emails CSV (`contacts_emails_TIMESTAMP.csv`)
```csv
Email,Source URL
info@example.com,https://example.com
support@example.com,https://example.com
```

#### 2. Phones CSV (`contacts_phones_TIMESTAMP.csv`)
```csv
Phone Number,Source URL
+1-555-123-4567,https://example.com
(123) 456-7890,https://company1.com
```

#### 3. Addresses CSV (`contacts_addresses_TIMESTAMP.csv`)
```csv
Address,Source URL
"123 Main St, New York, NY 10001",https://example.com
```

#### 4. Organized JSON (`contacts_organized_TIMESTAMP.json`)
```json
{
  "metadata": {
    "generated_at": "2026-03-16T12:15:48",
    "total_urls_scraped": 4,
    "total_contacts_found": {
      "emails": 5,
      "phones": 3,
      "addresses": 2
    }
  },
  "results": [
    {
      "source_url": "https://example.com",
      "contacts": {
        "emails": ["info@example.com"],
        "phones": ["+1-555-123-4567"],
        "addresses": ["123 Main St, New York, NY 10001"]
      }
    }
  ],
  "all_emails": [
    {"email": "info@example.com", "source": "https://example.com"}
  ],
  "all_phones": [
    {"phone": "+1-555-123-4567", "source": "https://example.com"}
  ],
  "all_addresses": [
    {"address": "123 Main St, New York, NY 10001", "source": "https://example.com"}
  ]
}
```

#### 5. Summary Report (`contacts_summary_TIMESTAMP.txt`)
```
============================================================
CONTACT SCRAPER - SUMMARY REPORT
============================================================

Generated: 2026-03-16 12:15:48
Total URLs Scraped: 4

------------------------------------------------------------
TOTAL CONTACTS FOUND
------------------------------------------------------------
Emails:    5
Phones:    3
Addresses: 2

------------------------------------------------------------
FILES GENERATED
------------------------------------------------------------
1. contacts_organized_20260316_121548.json
2. contacts_emails_20260316_121548.csv
3. contacts_phones_20260316_121548.csv
4. contacts_addresses_20260316_121548.csv
5. contacts_summary_20260316_121548.txt
```

### Traditional Format (Legacy)

If you prefer the traditional combined format:

#### CSV Format
```
URL,Emails,Phones,Addresses
https://example.com,info@example.com; support@example.com,+1-555-123-4567,123 Main St, New York, NY 10001
```

#### JSON Format
```json
[
  {
    "url": "https://example.com",
    "emails": ["info@example.com"],
    "phones": ["+1-555-123-4567"],
    "addresses": ["123 Main St, New York, NY 10001"]
  }
]
```

## Examples

### Scrape from a business directory
```bash
python contact_scraper.py "https://yellowpages.com/search?search_terms=plumbers+new+york"
```

### Scrape from company websites
```bash
python contact_scraper.py https://company1.com/contact https://company2.com
```

### Batch processing from a file
```bash
# Create a list of URLs in urls.txt
while read url; do
    python contact_scraper.py "$url" -o csv
done < urls.txt
```

## Notes

- ⚠️ Always respect `robots.txt` and website terms of service
- ⚠️ Use reasonable timeouts to avoid overloading servers
- ⚠️ Some websites may have anti-scraping measures
- ⚠️ Results may vary depending on website structure

## Troubleshooting

**No contacts found?**
- The website may use JavaScript to load content (requires Selenium)
- Contact info might be in images or PDFs
- The site may have anti-bot protection

**Request timeout errors?**
- Increase timeout: `--timeout 30`
- Check your internet connection
- The website may be blocking automated requests

## License

MIT License - Feel free to modify and use for your projects!

---

## Error Logging

The scraper includes comprehensive error logging to help you troubleshoot issues.

### Log Files Location

All logs are stored in the `logs/` directory:

- **`logs/error_YYYYMMDD.log`** - Error logs from the CLI scraper
- **`logs/flask_error_YYYYMMDD.log`** - Error logs from the Flask web dashboard
- **`logs/flask_app_YYYYMMDD.log`** - All logs (DEBUG+) from the Flask dashboard

### Viewing Logs

```bash
# View today's error log
cat logs/error_$(date +%Y%m%d).log

# View Flask error log
cat logs/flask_error_$(date +%Y%m%d).log

# Follow logs in real-time
tail -f logs/error_*.log
```

### Log Format

```
2026-03-16 11:59:19 - contact_scraper - ERROR - Connection error fetching https://example.com: [details]
2026-03-16 11:59:19 - contact_scraper - INFO - Starting scrape for URL: https://example.com
```

### Log Levels

- **INFO** - General progress information
- **WARNING** - Non-critical issues (e.g., failed to fetch a page)
- **ERROR** - Actual errors (e.g., connection failures, timeouts)
- **DEBUG** - Detailed debugging information (Flask app only)

### Common Errors

| Error Type | Description | Solution |
|------------|-------------|----------|
| Timeout | Server took too long | Increase `--timeout` value |
| HTTPError | HTTP status errors (404, 503) | Check URL or try later |
| ConnectionError | Network issues | Check internet connection |
| SSL Error | Certificate verification failed | Website may have SSL issues |

---

## Web Dashboard (New!)

A beautiful web UI is available for easier operation.

### Start the Dashboard

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py
```

Then open your browser to: **http://localhost:5000**

### Dashboard Features

- 📊 **Live Stats** - See total emails, phones, addresses found
- 🔄 **Real-time Progress** - Watch scraping progress live
- 📋 **Results Table** - View all extracted contacts in a table
- 💾 **One-click Export** - Download CSV or JSON instantly
- 📜 **Job History** - Track all your scraping jobs
- 📤 **File Upload** - Upload URL lists or paste directly
