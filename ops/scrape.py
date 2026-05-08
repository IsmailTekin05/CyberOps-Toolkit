import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ops.utils import ensure_dir


class WebScraper:
    #url = url to scrape, selectors = a list of css targets for soup
    def __init__(self, url, selectors=None, log_file="../reports/scrape_logs.json"):
        self.url = url
        self.selectors = selectors if selectors else ["title", "h1", "p"]
        self.log_file = log_file

        ensure_dir(log_file)

        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def _log_data(self, emails, extracted_content):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": self.url,
            "emails_found": emails,
            "extracted_data": extracted_content
        }

        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    pass

        logs.append(log_entry)

        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

    #makes the request and returns the response
    def fetch_page(self):
        #we use this so the website will think we are a normal user and let us in
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        #we make the http request
        response = requests.get(self.url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text

    def scrape(self):
        try:
            html_content = self.fetch_page()
            soup = BeautifulSoup(html_content, "html.parser")

            #check for email matches on the http response
            raw_emails = self.email_pattern.findall(html_content)
            unique_emails = list(set(raw_emails))

            extracted_data = {}
            for selector in self.selectors:
                elements = soup.select(selector)
                extracted_data[selector] = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]

            self._log_data(unique_emails, extracted_data)

            #return emails and css components
            return {
                "emails": unique_emails,
                "data": extracted_data
            }

        except requests.exceptions.RequestException as e:
            print(f"[-] Network error occurred: {e}")
        except Exception as e:
            print(f"[-] Parsing error occurred: {e}")