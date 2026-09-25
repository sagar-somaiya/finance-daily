"""
Finance Daily — data fetcher

Run on a schedule (see .github/workflows/update-data.yml). Fetches indices,
watchlist stocks, crypto, FX and news, then writes everything into one
data.json file that the static HTML page reads directly — no API keys or
CORS issues in the browser, because none of these calls happen there.

Run locally to test:
    pip install -r requirements.txt
    python fetch_data.py
"""

import json
import re
from datetime import datetime, timezone

import feedparser
import requests
import yfinance as yf

INDICES = [
    {"name": "NIFTY 50", "symbol": "^NSEI"},
    {"name": "SENSEX", "symbol": "^BSESN"},
    {"name": "BANK NIFTY", "symbol": "^NSEBANK"},
]

WATCHLIST = [
    {"name": "Reliance Industries", "symbol": "RELIANCE.NS"},
    {"name": "HDFC Bank", "symbol": "HDFCBANK.NS"},
    {"name": "Tata Consultancy Svcs", "symbol": "TCS.NS"},
    {"name": "Infosys", "symbol": "INFY.NS"},
    {"name": "DMart (Avenue Supermarts)", "symbol": "DMART.NS"},
    {"name": "Nestle India", "symbol": "NESTLEIND.NS"},
    {"name": "Vedanta", "symbol": "VEDL.NS"},
    {"name": "Bata India", "symbol": "BATAINDIA.NS"},
    {"name": "ACC", "symbol": "ACC.NS"},
    {"name": "PVR Inox", "symbol": "PVRINOX.NS"},
]

RSS_FEEDS = {
    "corp": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.moneycontrol.com/rss/business.xml",
    ],
    "acct": [
        "https://news.google.com/rss/search?q=ICAI+OR+%22Ind+AS%22+OR+IFRS+OR+%22chartered+accountant%22&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=GST+OR+%22income+tax%22+OR+RBI+OR+SEBI+India&hl=en-IN&gl=IN&ceid=IN:en",
    ],
}


def fetch_quote(symbol):
    """Fetch one symbol's latest price + % change via yfinance."""
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        price = info.get("last_price")
        prev_close = info.get("previous_close") or info.get("regular_market_previous_close")
        if price is None or prev_close in (None, 0):
            return {"ok": False}
        chg_pct = ((price - prev_close) / prev_close) * 100
        return {"ok": True, "price": round(float(price), 2), "chgPct": round(float(chg_pct), 2)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def fetch_indices():
    out = []
    for idx in INDICES:
        q = fetch_quote(idx["symbol"])
        out.append({**idx, **q})
    return out


def fetch_watchlist():
    out = []
    for w in WATCHLIST:
        q = fetch_quote(w["symbol"])
        out.append({**w, **q})
    return out


def fetch_crypto():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin,ethereum",
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=10,
        )
        r.raise_for_status()
        d = r.json()
        return {
            "ok": True,
            "btc": {"price": d["bitcoin"]["usd"], "chg": round(d["bitcoin"]["usd_24h_change"], 2)},
            "eth": {"price": d["ethereum"]["usd"], "chg": round(d["ethereum"]["usd_24h_change"], 2)},
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def fetch_fx():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        r.raise_for_status()
        rates = r.json()["rates"]
        return {
            "ok": True,
            "usdinr": round(rates["INR"], 2),
            "eurinr": round(rates["INR"] / rates["EUR"], 2),
            "gbpinr": round(rates["INR"] / rates["GBP"], 2),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def clean_title(title):
    return re.sub(r"\s+", " ", title or "").strip()


def fetch_feed(url, limit=10):
    try:
        parsed = feedparser.parse(url)
        source = parsed.feed.get("title", "source") if parsed.feed else "source"
        items = []
        for entry in parsed.entries[:limit]:
            items.append(
                {
                    "title": clean_title(entry.get("title")),
                    "link": entry.get("link", ""),
                    "source": source,
                    "pubDate": entry.get("published", ""),
                }
            )
        return items
    except Exception:
        return []


def fetch_news():
    corp = []
    for url in RSS_FEEDS["corp"]:
        corp.extend(fetch_feed(url))
    acct = []
    for url in RSS_FEEDS["acct"]:
        acct.extend(fetch_feed(url))
    return {"corp": corp[:10], "acct": acct[:10]}


def main():
    data = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "indices": fetch_indices(),
        "watchlist": fetch_watchlist(),
        "crypto": fetch_crypto(),
        "fx": fetch_fx(),
        "news": fetch_news(),
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote data.json at {data['generatedAt']}")


if __name__ == "__main__":
    main()
