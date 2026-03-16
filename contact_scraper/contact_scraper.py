#!/usr/bin/env python3
"""
Contact Details Web Scraper
Extracts email, phone, and address from company websites and directories.
"""

import re
import json
import csv
import argparse
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Set
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# Configure logging
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger('contact_scraper')
logger.setLevel(logging.DEBUG)

# File handler for error logs
error_log_file = LOG_DIR / f'error_{datetime.now().strftime("%Y%m%d")}.log'
file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
file_handler.setLevel(logging.ERROR)

# Console handler for info logs
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class ContactScraper:
    """Scraper for extracting contact details from websites."""

    # Regex patterns for contact information
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )

    PHONE_PATTERNS = [
        re.compile(r'\+?[\d\s\-\(\)]{10,}'),  # International format
        re.compile(r'\(\d{3}\)\s*\d{3}[-]?\d{4}'),  # (123) 456-7890
        re.compile(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'),  # 123-456-7890
    ]

    def __init__(self, timeout: int = 10, max_pages: int = 5, results_dir: str = 'results'):
        self.timeout = timeout
        self.max_pages = max_pages
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.visited_urls: Set[str] = set()
        self.logger = logger
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        try:
            self.logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error fetching {url}: {e}")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error fetching {url} (Status: {e.response.status_code}): {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error fetching {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}", exc_info=True)
            return None
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        emails = self.EMAIL_PATTERN.findall(text)
        # Filter out common image/file extensions
        emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
        return list(set(emails))
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        phones = []
        for pattern in self.PHONE_PATTERNS:
            matches = pattern.findall(text)
            for match in matches:
                # Clean and validate phone number
                cleaned = re.sub(r'[^\d+]', '', match)
                if len(cleaned) >= 10:  # Minimum digits for a phone number
                    phones.append(match.strip())
        return list(set(phones))
    
    def extract_address(self, soup: BeautifulSoup) -> List[str]:
        """Extract physical addresses from HTML."""
        addresses = []
        
        # Common address patterns
        address_patterns = [
            re.compile(r'\d+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}', re.IGNORECASE),
            re.compile(r'\d+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,\s*[A-Z]{2}', re.IGNORECASE),
        ]
        
        # Look for address-related keywords in elements
        address_keywords = ['address', 'location', 'headquarters', 'office', 'street', 'ave', 'blvd', 'road']
        
        # Search in common address containers
        for tag in soup.find_all(['p', 'div', 'span', 'li', 'address']):
            text = tag.get_text(strip=True)
            if len(text) < 20 or len(text) > 200:
                continue
                
            # Check if element contains address-like content
            for pattern in address_patterns:
                matches = pattern.findall(text)
                if matches:
                    addresses.extend(matches)
            
            # Check for address keywords
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in address_keywords):
                # Clean and add if it looks like an address
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                for line in lines:
                    if len(line) > 15 and any(kw in line.lower() for kw in address_keywords):
                        addresses.append(line)
        
        return list(set(addresses))[:3]  # Limit to 3 addresses
    
    def find_contact_pages(self, base_url: str, html: str) -> List[str]:
        """Find links to contact pages."""
        contact_urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        contact_keywords = ['contact', 'about', 'about-us', 'get-in-touch', 'reach-us']
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text(strip=True).lower()
            
            # Check if link or text contains contact keywords
            if any(keyword in href for keyword in contact_keywords) or \
               any(keyword in text for keyword in contact_keywords):
                full_url = urljoin(base_url, link['href'])
                if full_url not in self.visited_urls:
                    contact_urls.append(full_url)
        
        return contact_urls[:self.max_pages]
    
    def scrape_url(self, url: str) -> Dict:
        """Scrape contact details from a single URL."""
        self.logger.info(f"Starting scrape for URL: {url}")

        result = {
            'url': url,
            'emails': [],
            'phones': [],
            'addresses': []
        }

        # Fetch main page
        html = self.fetch_page(url)
        if not html:
            self.logger.warning(f"Failed to fetch main page for {url}")
            return result

        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            # Extract from main page
            result['emails'] = self.extract_emails(text)
            result['phones'] = self.extract_phones(text)
            result['addresses'] = self.extract_address(soup)

            # Find and scrape contact pages
            contact_pages = self.find_contact_pages(url, html)
            self.visited_urls.add(url)

            for contact_url in contact_pages:
                if contact_url in self.visited_urls:
                    continue

                self.visited_urls.add(contact_url)
                self.logger.info(f"Checking contact page: {contact_url}")

                contact_html = self.fetch_page(contact_url)
                if contact_html:
                    contact_soup = BeautifulSoup(contact_html, 'html.parser')
                    contact_text = contact_soup.get_text()

                    # Merge results
                    result['emails'].extend(self.extract_emails(contact_text))
                    result['phones'].extend(self.extract_phones(contact_text))
                    result['addresses'].extend(self.extract_address(contact_soup))
                else:
                    self.logger.warning(f"Failed to fetch contact page: {contact_url}")

            # Deduplicate
            result['emails'] = list(set(result['emails']))
            result['phones'] = list(set(result['phones']))
            result['addresses'] = list(set(result['addresses']))

            self.logger.info(f"Completed scrape for {url}: Found {len(result['emails'])} emails, "
                           f"{len(result['phones'])} phones, {len(result['addresses'])} addresses")

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}", exc_info=True)

        return result
    
    def save_to_csv(self, results: List[Dict], filename: str = 'contacts.csv'):
        """Save results to CSV file."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Emails', 'Phones', 'Addresses'])

                for result in results:
                    writer.writerow([
                        result['url'],
                        '; '.join(result['emails']),
                        '; '.join(result['phones']),
                        '; '.join(result['addresses'])
                    ])
            self.logger.info(f"Results saved to CSV: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving CSV file {filename}: {e}", exc_info=True)
            raise

    def save_to_json(self, results: List[Dict], filename: str = 'contacts.json'):
        """Save results to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Results saved to JSON: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving JSON file {filename}: {e}", exc_info=True)
            raise

    def save_organized_results(self, results: List[Dict], base_filename: str = 'contacts'):
        """Save results in organized structure with separate files for each contact type."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path(self.results_dir) if hasattr(self, 'results_dir') else Path('.')
            output_dir.mkdir(exist_ok=True)

            # Organized JSON structure
            organized_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_urls_scraped': len(results),
                    'total_contacts_found': {
                        'emails': sum(len(r['emails']) for r in results),
                        'phones': sum(len(r['phones']) for r in results),
                        'addresses': sum(len(r['addresses']) for r in results)
                    }
                },
                'results': []
            }

            # Separate collections for each type
            all_emails = []
            all_phones = []
            all_addresses = []

            for result in results:
                # Add to organized results
                organized_result = {
                    'source_url': result['url'],
                    'contacts': {
                        'emails': result['emails'],
                        'phones': result['phones'],
                        'addresses': result['addresses']
                    }
                }
                organized_data['results'].append(organized_result)

                # Collect all unique contacts with source
                for email in result['emails']:
                    all_emails.append({'email': email, 'source': result['url']})
                for phone in result['phones']:
                    all_phones.append({'phone': phone, 'source': result['url']})
                for address in result['addresses']:
                    all_addresses.append({'address': address, 'source': result['url']})

            organized_data['all_emails'] = all_emails
            organized_data['all_phones'] = all_phones
            organized_data['all_addresses'] = all_addresses

            # Save organized JSON
            organized_json_path = output_dir / f'{base_filename}_organized_{timestamp}.json'
            with open(organized_json_path, 'w', encoding='utf-8') as f:
                json.dump(organized_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Organized results saved to: {organized_json_path}")

            # Save separate CSV files for each contact type
            # Emails CSV
            emails_csv_path = output_dir / f'{base_filename}_emails_{timestamp}.csv'
            with open(emails_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Email', 'Source URL'])
                for item in all_emails:
                    writer.writerow([item['email'], item['source']])
            self.logger.info(f"Emails saved to: {emails_csv_path}")

            # Phones CSV
            phones_csv_path = output_dir / f'{base_filename}_phones_{timestamp}.csv'
            with open(phones_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Phone Number', 'Source URL'])
                for item in all_phones:
                    writer.writerow([item['phone'], item['source']])
            self.logger.info(f"Phones saved to: {phones_csv_path}")

            # Addresses CSV
            addresses_csv_path = output_dir / f'{base_filename}_addresses_{timestamp}.csv'
            with open(addresses_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Address', 'Source URL'])
                for item in all_addresses:
                    writer.writerow([item['address'], item['source']])
            self.logger.info(f"Addresses saved to: {addresses_csv_path}")

            # Summary report
            summary_path = output_dir / f'{base_filename}_summary_{timestamp}.txt'
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("CONTACT SCRAPER - SUMMARY REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total URLs Scraped: {len(results)}\n\n")
                f.write("-" * 60 + "\n")
                f.write("TOTAL CONTACTS FOUND\n")
                f.write("-" * 60 + "\n")
                f.write(f"Emails:    {len(all_emails)}\n")
                f.write(f"Phones:    {len(all_phones)}\n")
                f.write(f"Addresses: {len(all_addresses)}\n\n")
                f.write("-" * 60 + "\n")
                f.write("FILES GENERATED\n")
                f.write("-" * 60 + "\n")
                f.write(f"1. {organized_json_path.name}\n")
                f.write(f"2. {emails_csv_path.name}\n")
                f.write(f"3. {phones_csv_path.name}\n")
                f.write(f"4. {addresses_csv_path.name}\n")
                f.write(f"5. {summary_path.name}\n")
            self.logger.info(f"Summary saved to: {summary_path}")

            return {
                'organized_json': str(organized_json_path),
                'emails_csv': str(emails_csv_path),
                'phones_csv': str(phones_csv_path),
                'addresses_csv': str(addresses_csv_path),
                'summary': str(summary_path)
            }

        except Exception as e:
            self.logger.error(f"Error saving organized results: {e}", exc_info=True)
            raise


def load_urls_from_file(filepath: str) -> List[str]:
    """Load URLs from a text file (one URL per line)."""
    urls = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    if not line.startswith('http'):
                        line = 'https://' + line
                    urls.append(line)
        logger.info(f"Loaded {len(urls)} URLs from {filepath}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {filepath}: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied reading file: {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error loading URLs from {filepath}: {e}", exc_info=True)
    return urls


def main():
    parser = argparse.ArgumentParser(
        description='Scrape contact details from company websites'
    )
    parser.add_argument(
        'urls',
        nargs='*',
        help='URL(s) to scrape'
    )
    parser.add_argument(
        '-f', '--file',
        help='Text file containing URLs (one per line)'
    )
    parser.add_argument(
        '-o', '--output',
        choices=['csv', 'json', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=5,
        help='Maximum contact pages to check per site (default: 5)'
    )
    parser.add_argument(
        '--organized',
        action='store_true',
        default=True,
        help='Save results in organized structure (separate files for emails, phones, addresses)'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='results',
        help='Directory to save results (default: results)'
    )

    args = parser.parse_args()

    # Get URLs from file or command line
    urls = []
    if args.file:
        urls = load_urls_from_file(args.file)
    elif args.urls:
        urls = args.urls
    else:
        parser.error('Provide URLs as arguments or use -f/--file for a URL list file')

    if not urls:
        logger.error("No URLs provided to scrape")
        return

    # Initialize scraper
    scraper = ContactScraper(timeout=args.timeout, max_pages=args.max_pages, results_dir=args.results_dir)

    logger.info(f"Starting scrape job for {len(urls)} URLs")

    # Scrape all URLs
    results = []
    for url in urls:
        if not url.startswith('http'):
            url = 'https://' + url

        result = scraper.scrape_url(url)
        results.append(result)

        # Print summary
        logger.info(f"Completed: {result['url']} - Emails: {len(result['emails'])}, "
                   f"Phones: {len(result['phones'])}, Addresses: {len(result['addresses'])}")

        if result['emails']:
            logger.debug(f"Emails: {', '.join(result['emails'][:3])}")
        if result['phones']:
            logger.debug(f"Phones: {', '.join(result['phones'][:3])}")

    # Save results
    try:
        if args.organized:
            # Save in organized structure
            organized_files = scraper.save_organized_results(results)
            logger.info(f"Organized results saved:")
            logger.info(f"  - Emails: {organized_files['emails_csv']}")
            logger.info(f"  - Phones: {organized_files['phones_csv']}")
            logger.info(f"  - Addresses: {organized_files['addresses_csv']}")
            logger.info(f"  - Summary: {organized_files['summary']}")
        else:
            # Save in traditional format
            if args.output in ['csv', 'both']:
                scraper.save_to_csv(results)
            if args.output in ['json', 'both']:
                scraper.save_to_json(results)
        logger.info(f"Scrape job completed successfully. Processed {len(results)} URLs")
    except Exception as e:
        logger.error(f"Failed to save results: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
