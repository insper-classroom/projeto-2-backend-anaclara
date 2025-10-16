import os
import requests

BRAPI_BASE = "https://brapi.dev/api"
HEADERS = {
    "User-Agent": "FinScope/1.0 (+https://example.local)",
    "Accept": "application/json",
}

BRAPI_TOKEN = os.getenv("BRAPI_TOKEN")  # lido do ambiente/.env

def _with_token(params: dict | None) -> dict:
    params = dict(params or {})
    if BRAPI_TOKEN:
        params["token"] = BRAPI_TOKEN
    return params

def _get(path: str, params: dict | None = None, timeout: int = 15):
    try:
        r = requests.get(
            f"{BRAPI_BASE}{path}",
            headers=HEADERS,
            params=_with_token(params),
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        # mensagens sem URL (não vaza token)
        if status == 401:
            msg = "Brapi: acesso negado (token inválido/ausente)."
        elif status == 429:
            msg = "Brapi: limite de requests atingido."
        else:
            msg = f"Brapi erro HTTP {status or 'desconhecido'}."
        raise RuntimeError(msg) from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError("Brapi: falha de rede/timeout.") from e

def _to_b3(symbol: str) -> str:
    # Yahoo usa PETR4.SA; brapi usa PETR4
    return symbol[:-3] if symbol.upper().endswith(".SA") else symbol

def search(query: str, limit: int = 10):
    data = _get("/search", {"query": query})
    stocks = (data or {}).get("stocks", []) or []
    items = []
    for s in stocks[:limit]:
        items.append({
            "symbol": s.get("stock"),
            "name": s.get("name") or "",
            "exchange": "B3",
        })
    return {"count": len(items), "items": items}

def quote(symbol: str):
    sym = _to_b3(symbol)
    data = _get(f"/quote/{sym}", {"range": "1d", "interval": "1d", "fundamental": "true"})
    arr = (data or {}).get("results", []) or []
    if not arr:
        return {}
    q = arr[0]
    return {
        "symbol": symbol,  # mantém como veio do front
        "name": q.get("shortName") or q.get("longName") or "",
        "price": q.get("regularMarketPrice"),
        "previous_close": q.get("regularMarketPreviousClose"),
        "change": q.get("regularMarketChange"),
        "change_pct": q.get("regularMarketChangePercent"),
        "as_of": q.get("regularMarketTime"),
        "market_cap": q.get("marketCap"),
    }
