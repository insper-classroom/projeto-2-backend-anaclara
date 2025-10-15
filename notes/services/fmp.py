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
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    # Funcionalidade 1: company notes
    def company_notes(self, symbol: str, **params):
        return self._get("/company-notes", {"symbol": symbol, **params})

    # =============================
    # Funcionalidade 2: histórico EOD
    # =============================
    def historical_price_eod(self, symbol: str, full: bool = True, **params):
        path = "/historical-price-eod/full" if full else "/historical-price-eod"
        return self._get(path, {"symbol": symbol, **params})
