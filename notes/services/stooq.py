# notes/services/stooq.py
import csv
import io
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/csv,application/json;q=0.9,*/*;q=0.8",
}

def _us_symbol(symbol: str) -> str:
    """
    Converte 'AAPL' ou 'AAPL.US' para o formato do Stooq: 'aapl.us'
    (só vamos usar Stooq como fallback para EUA).
    """
    s = symbol.upper()
    if "." in s:
        base, suf = s.split(".", 1)
        if suf != "US":
            # se não é .US, deixamos como base + .us mesmo assim (stooq só tem .us, .uk etc.)
            pass
        return f"{base.lower()}.us"
    return f"{s.lower()}.us"

def quote(symbol: str) -> dict:
    """
    Lê histórico diário em CSV do Stooq, pega os 2 últimos candles para
    calcular price, previous_close, change e change_pct.
    """
    sym = _us_symbol(symbol)
    url = f"https://stooq.com/q/d/l/?s={sym}&i=d"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    rows = list(csv.DictReader(io.StringIO(r.text)))
    if not rows:
        return {}

    last = rows[-1]
    price = _to_float(last.get("Close"))
    prev = _to_float(rows[-2].get("Close")) if len(rows) > 1 else None

    change = (price - prev) if (price is not None and prev is not None) else None
    change_pct = ((change / prev) * 100.0) if (change is not None and prev not in (None, 0)) else None

    return {
        "symbol": symbol,
        "name": "",  # Stooq não traz nome curto aqui; mantemos vazio
        "price": price,
        "previous_close": prev,
        "change": change,
        "change_pct": change_pct,
        "as_of": last.get("Date"),
        "market_cap": None,  # Stooq não expõe market cap
    }

def _to_float(v):
    try:
        if v is None or v == "-" or v == "":
            return None
        return float(v)
    except Exception:
        return None
