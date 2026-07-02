# Fetch Pages

Python script for fetching page content to ingest in an AI assistant

## ⚠️ Legal Disclaimer & Ethical Use

This tool is provided for **legitimate and lawful purposes only**, such as ingesting content from websites you own or have explicit permission to access.

**By using this script, you agree that:**

- You are solely responsible for ensuring your use complies with all applicable laws, including but not limited to the Computer Fraud and Abuse Act (CFAA), GDPR, and relevant local regulations.
- You have read and will respect the target website's `robots.txt` file and Terms of Service before fetching any content.
- Unauthorized scraping, circumventing access controls, harvesting personal data without consent, or any use that violates a site's ToS is done entirely **at your own risk**.

**The author of this project accepts no liability** for any misuse, legal consequences, damages, or harm arising from use of this software. This project is released as-is under the MIT License, with no warranty of any kind.

## Dependencies

Set up and activate virtual environment:<br>
`python3 -m venv .venv`<br>
`source .venv/bin/activate`

Install `playwright` package into the virtual environment:<br> 
`pip install playwright`

Download `chromium` for `playwright`:<br>
`playwright install chromium`

## Run

Fetch page content:<br>
`python3 fetch_page.py [URL]`

The script will fetch text and images from the URL and output them in markdown.
