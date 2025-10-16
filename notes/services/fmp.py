import requests
from django.conf import settings

BASE = getattr(settings, "FMP_BASE", "https://financialmodelingprep.com/stable")
API_KEY = getattr(settings, "FMP_API_KEY", None)

class FMPClient:
    """Cliente simples para a FinancialModelingPrep (FMP)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise RuntimeError("FMP_API_KEY não definido em settings/env.")

    def _get(self, path: str, params: dict | None = None):
        params = dict(params or {})
        params["apikey"] = self.api_key
        url = f"{BASE}{path}"
        try:
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            # Algumas respostas da FMP podem vir como lista ou dict
            return r.json()
        except requests.exceptions.HTTPError as e:
            # Propaga erro com informação de status (a view converte para JSON)
            raise RuntimeError(f"FMP HTTP {r.status_code}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"FMP request error: {e}") from e

    def company_notes(self, symbol: str, **params):
        return self._get("/company-notes", {"symbol": symbol, **params})

    def historical_price_eod(self, symbol: str, full: bool = True, **params):
        """
        FMP “stable” é mais confiável em /full. Fazemos fallback automático:
        - se pedir curto e der 404, repetimos em /full.
        """
        def _call(path):
            return self._get(path, {"symbol": symbol, **params})

        try:
            if full:
                return _call("/historical-price-eod/full")
            # tenta curto primeiro
            return _call("/historical-price-eod")
        except RuntimeError as e:
            # Se a curta falhar (muito comum 404), tenta /full
            msg = str(e).lower()
            if (not full) and ("404" in msg or "not found" in msg):
                return _call("/historical-price-eod/full")
            raise

    def search(self, query: str, limit: int = 10, exchange: str | None = None):
        params = {"query": query, "limit": limit}
        if exchange:
            params["exchange"] = exchange
        return self._get("/search", params)

    def quote(self, symbol: str, **params):
        """
        Busca cotação atual (último preço, variação, etc.)
        Exemplo de URL:
        https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey=...
        """
        return self._get("/quote", {"symbol": symbol, **params})
