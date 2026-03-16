# Contact Scraper - Organized Output Structure

This document explains the organized file structure for contact scraper results.

## File Structure After Scraping

```
contact_scraper/
├── results/
│   ├── contacts_emails_20260316_121548.csv       ← All emails
│   ├── contacts_phones_20260316_121548.csv       ← All phone numbers
│   ├── contacts_addresses_20260316_121548.csv    ← All addresses
│   ├── contacts_organized_20260316_121548.json   ← Complete structured data
│   ├── contacts_summary_20260316_121548.txt      ← Human-readable summary
│   ├── contacts_20260316_121548.csv              ← Traditional combined CSV
│   └── contacts_20260316_121548.json             ← Traditional combined JSON
└── logs/
    ├── error_20260316.log                        ← Error logs
    └── README.md                                  ← Logging documentation
```

## File Descriptions

### 1. contacts_emails_TIMESTAMP.csv
**Purpose:** Contains all extracted email addresses with their source URLs.

**Format:**
```csv
Email,Source URL
contact@example.com,https://example.com
support@company.com,https://company.com/about
```

**Use Case:** When you only need email addresses for email campaigns.

---

### 2. contacts_phones_TIMESTAMP.csv
**Purpose:** Contains all extracted phone numbers with their source URLs.

**Format:**
```csv
Phone Number,Source URL
+1-555-123-4567,https://example.com
(123) 456-7890,https://company.com/contact
```

**Use Case:** When you only need phone numbers for call campaigns.

---

### 3. contacts_addresses_TIMESTAMP.csv
**Purpose:** Contains all extracted physical addresses with their source URLs.

**Format:**
```csv
Address,Source URL
"123 Main St, New York, NY 10001",https://example.com
"456 Business Ave, Los Angeles, CA 90001",https://company.com
```

**Use Case:** When you only need addresses for mail campaigns or location analysis.

---

### 4. contacts_organized_TIMESTAMP.json
**Purpose:** Complete structured data with metadata and separated contact types.

**Format:**
```json
{
  "metadata": {
    "generated_at": "2026-03-16T12:15:48",
    "total_urls_scraped": 10,
    "total_contacts_found": {
      "emails": 25,
      "phones": 15,
      "addresses": 10
    }
  },
  "results": [
    {
      "source_url": "https://example.com",
      "contacts": {
        "emails": ["contact@example.com"],
        "phones": ["+1-555-123-4567"],
        "addresses": ["123 Main St, New York, NY 10001"]
      }
    }
  ],
  "all_emails": [
    {"email": "contact@example.com", "source": "https://example.com"}
  ],
  "all_phones": [
    {"phone": "+1-555-123-4567", "source": "https://example.com"}
  ],
  "all_addresses": [
    {"address": "123 Main St, New York, NY 10001", "source": "https://example.com"}
  ]
}
```

**Use Case:** When you need complete structured data for programmatic access or importing into databases.

---

### 5. contacts_summary_TIMESTAMP.txt
**Purpose:** Human-readable summary report of the scraping job.

**Format:**
```
============================================================
CONTACT SCRAPER - SUMMARY REPORT
============================================================

Generated: 2026-03-16 12:15:48
Total URLs Scraped: 10

------------------------------------------------------------
TOTAL CONTACTS FOUND
------------------------------------------------------------
Emails:    25
Phones:    15
Addresses: 10

------------------------------------------------------------
FILES GENERATED
------------------------------------------------------------
1. contacts_organized_20260316_121548.json
2. contacts_emails_20260316_121548.csv
3. contacts_phones_20260316_121548.csv
4. contacts_addresses_20260316_121548.csv
5. contacts_summary_20260316_121548.txt
```

**Use Case:** Quick overview of scraping results without opening multiple files.

---

### 6. contacts_TIMESTAMP.csv (Traditional)
**Purpose:** Legacy format with all contacts combined in one row per URL.

**Format:**
```csv
URL,Emails,Phones,Addresses
https://example.com,contact@example.com; support@example.com,+1-555-123-4567; +1-555-987-6543,"123 Main St, New York, NY 10001"
```

**Use Case:** Backward compatibility with existing workflows.

---

### 7. contacts_TIMESTAMP.json (Traditional)
**Purpose:** Legacy JSON format with all contacts per URL.

**Format:**
```json
[
  {
    "url": "https://example.com",
    "emails": ["contact@example.com", "support@example.com"],
    "phones": ["+1-555-123-4567", "+1-555-987-6543"],
    "addresses": ["123 Main St, New York, NY 10001"]
  }
]
```

**Use Case:** Backward compatibility with existing workflows.

---

## Usage Examples

### Open only emails in Excel
```bash
# On Linux
libreoffice results/contacts_emails_*.csv

# On macOS
open results/contacts_emails_*.csv

# On Windows
start results/contacts_emails_*.csv
```

### Import organized JSON into Python
```python
import json

with open('results/contacts_organized_20260316_121548.json') as f:
    data = json.load(f)

# Get all emails
emails = [item['email'] for item in data['all_emails']]

# Get results by URL
for result in data['results']:
    print(f"URL: {result['source_url']}")
    print(f"Emails: {result['contacts']['emails']}")
```

### Filter emails by domain
```python
import csv

domain_filter = 'gmail.com'
filtered_emails = []

with open('results/contacts_emails_*.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if domain_filter in row['Email']:
            filtered_emails.append(row)
```

### Count total contacts from summary
```bash
# Extract counts from summary file
grep "Emails:" results/contacts_summary_*.txt
grep "Phones:" results/contacts_summary_*.txt
grep "Addresses:" results/contacts_summary_*.txt
```

---

## Benefits of Organized Output

✅ **Separation of Concerns** - Each contact type in its own file
✅ **Easy Import** - Direct CSV import into Excel, Google Sheets, or CRM
✅ **Better Organization** - Clear file naming with timestamps
✅ **Complete Metadata** - JSON includes generation time and statistics
✅ **Source Tracking** - Every contact linked to its source URL
✅ **Human-Readable Summary** - Quick overview without opening data files
✅ **Backward Compatible** - Traditional formats still available

---

## Command Line Options

```bash
# Use organized output (default)
python contact_scraper.py -f websites.txt

# Specify custom results directory
python contact_scraper.py -f websites.txt --results-dir my_results

# Use traditional format instead
python contact_scraper.py -f websites.txt --organized false

# Combine options
python contact_scraper.py -f websites.txt \
    --timeout 15 \
    --max-pages 10 \
    --results-dir output/2026-03 \
    --organized true
```
