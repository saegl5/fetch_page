# Fetch Pages

Python script for fetching page content to ingest in an AI assistant

## Dependencies

Set up and activate virtual environment:<br>
`python3 -m venv .venv`<br>
`source .venv/bin/activate`

Install `playwright` package:<br> 
`pip install playwright`

Download `chromium`:<br>
`playwright install chromium`

## Run

Fetch page content:<br>
`python3 fetch_page.py [URL]`

The script will fetch text and images from the URL and output them in markdown.
