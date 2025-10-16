# notes/services/yahoo.py
import requests

YF_BASES = (
    "https://query1.finance.yahoo.com",
    "https://query2.finance.yahoo.com",  # fallback
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

class YahooError(RuntimeError):
    def __init__(self, status: int, msg: str = ""):
        super().__init__(msg or f"Yahoo HTTP {status}")
        self.status = status

def _get(path: str, params: dict | None = None, timeout: int = 15):
    params = params or {}
    last_exc: Exception | None = None
    for base in YF_BASES:
        try:
            r = requests.get(f"{base}{path}", headers=HEADERS, params=params, timeout=timeout)
            if r.status_code in (401, 403, 429):  # bloqueios usuais
                last_exc = YahooError(r.status_code, f"Yahoo HTTP {r.status_code}")
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_exc = e
            continue
    raise last_exc or RuntimeError("Yahoo Finance indisponível")

def search(query: str, limit: int = 10):
    data = _get("/v1/finance/search", {"q": query, "quotesCount": limit})
    quotes = (data or {}).get("quotes", []) or []
    items = []
    for q in quotes:
        symbol = q.get("symbol")
        if not symbol:
            continue
        name = q.get("shortname") or q.get("longname") or q.get("longName") or ""
        exch = q.get("exchDisp") or q.get("exchange") or ""
        items.append({"symbol": symbol, "name": name, "exchange": exch})
    return {"count": len(items), "items": items}

def quote(symbol: str):
    data = _get("/v7/finance/quote", {"symbols": symbol})
    arr = (data or {}).get("quoteResponse", {}).get("result", []) or []
    if not arr:
        return {}
    q = arr[0]
    return {
        "symbol": q.get("symbol") or symbol,
        "name": q.get("shortName") or q.get("longName") or "",
        "price": q.get("regularMarketPrice"),
        "previous_close": q.get("regularMarketPreviousClose"),
        "change": q.get("regularMarketChange"),
        "change_pct": q.get("regularMarketChangePercent"),
        "as_of": q.get("regularMarketTime"),
        "market_cap": q.get("marketCap"),
    }
