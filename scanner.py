import requests, re, os, glob
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd

TICKERS = ["AMD","AMZN","APP","BKNG","INTU","KKR","MA","META","MSFT","NFLX","NKE","SHOP","SOFI","SPGI","UBER","ROBO","BX"]
SOURCES = ["MarketBeat"]
LOOKBACK_DAYS = 7
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_marketbeat(ticker, cutoff):
    results = []
    for exch in ["NASDAQ","NYSE"]:
        url = f"https://www.marketbeat.com/stocks/{exch}-{ticker}/price-target/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            # Try to find price target table rows
            rows = soup.find_all("tr")
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) >= 5:
                    date_str = cols[0]
                    try:
                        dt = datetime.strptime(date_str, "%m/%d/%Y")
                        if dt.date() >= cutoff:
                            results.append({
                                "Ticker": ticker,
                                "Date": date_str,
                                "Firm": cols[1],
                                "Action": cols[2],
                                "Rating": cols[3],
                                "PT": cols[4],
                                "Source": "MarketBeat"
                            })
                    except:
                        continue
            if results:
                break
        except:
            continue
    return results

cutoff_date = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).date()
all_data = []

for t in TICKERS:
    try:
        data = fetch_marketbeat(t, cutoff_date)
        all_data.extend(data)
    except Exception as e:
        print(f"{t} error {e}")

if not all_data:
    for t in TICKERS:
        all_data.append({
            "Ticker": t,
            "Date": "-",
            "Firm": "-",
            "Action": "No change in last 7 days",
            "Rating": "Same",
            "PT": "Same",
            "Source": "-"
        })

df = pd.DataFrame(all_data)
# Save latest and dated version
df.to_csv("analyst_targets_weekly_latest.csv", index=False)
df.to_csv(f"analyst_targets_weekly_{datetime.now().strftime('%Y-%m-%d')}.csv", index=False)
print(f"Saved {len(df)} rows")
print(df.head())
