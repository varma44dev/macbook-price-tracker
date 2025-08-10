import requests
import re
import smtplib
from bs4 import BeautifulSoup
import os

# Target product URL
URL = "https://www.vijaysales.com/p/P238593/238591/apple-macbook-air-m4-chip-13-inch-34-46-cm-13-6-16gb-256gb-silver-mw0w3hn-a"

# Credentials from GitHub Secrets (match names in YAML)
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
APP_PASSWORD = os.environ["APP_PASSWORD"]

def fetch_price_vijaysales(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # Skip if exchange/buyback mentioned
    page_text = soup.get_text(separator=" ").lower()
    if "exchange" in page_text or "buyback" in page_text:
        return None, "Skipped: exchange/buyback offer"

    # Try to get price from known tag
    price_tag = soup.find("span", {"id": "spnFinalPrice"})
    if price_tag:
        return price_tag.text.strip(), None

    # Fallback regex search
    m = re.search(r'₹\s*[\d,]{3,}', soup.get_text())
    if m:
        return m.group().strip(), None

    return None, "Price not found"

def send_email(subject, body):
    msg = f"Subject: {subject}\n\n{body}"
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_FROM, APP_PASSWORD)
        smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg)

if __name__ == "__main__":
    price, info = fetch_price_vijaysales(URL)
    if price:
        send_email("MacBook Air M4 Price Update", f"Price: {price}\nLink: {URL}")
        print(f"Email sent! Price: {price}")
    else:
        print(f"No price fetched. Info: {info}")

