from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import WatchItem
from .serializers.watchlist import WatchItemSerializer
from .services.fmp import FMPClient
from rest_framework.permissions import AllowAny


#  helpers 
def _normalize_eod_payload(data):
    """
    FMP pode devolver:
      1) {"symbol": "XXX", "historical": [ {...}, ... ]}
      2) [ {...}, ... ]
    Esta função sempre retorna uma LISTA de candles.
    """
    if isinstance(data, dict) and "historical" in data:
        return data.get("historical") or []
    if isinstance(data, list):
        return data
    return []


def _json_error(detail: str, http_status=status.HTTP_502_BAD_GATEWAY):
    return Response({"detail": detail}, status=http_status)

@api_view(["GET"])
def search_view(request):
    q = request.query_params.get("q") or request.query_params.get("query")
    if not q:
        return Response({"detail": "Parâmetro 'q' é obrigatório."},
                        status=status.HTTP_400_BAD_REQUEST)
    limit = int(request.query_params.get("limit", 10))
    client = FMPClient()
    try:
        data = client.search(q, limit=limit)
    except RuntimeError as e:
        return _json_error(str(e), http_status=status.HTTP_502_BAD_GATEWAY)

    items = []
    for it in data or []:
        items.append({
            "symbol": it.get("symbol") or it.get("ticker"),
            "name": it.get("name") or it.get("companyName") or "",
            "exchange": it.get("exchangeShortName") or it.get("exchange") or "",
        })
    return Response({"count": len(items), "items": items}, status=status.HTTP_200_OK)

# Funcionalidade 1: company notes
@api_view(["GET"])
def company_notes_view(request, symbol: str):
    client = FMPClient()
    params = {}
    for key in ("limit", "page", "from", "to"):
        if key in request.query_params:
            params[key] = request.query_params.get(key)
    try:
        data = client.company_notes(symbol, **params)
    except RuntimeError as e:
        return _json_error(str(e), http_status=status.HTTP_502_BAD_GATEWAY)

    items = []
    raw = []
    # FMP pode vir como {"data": [...]} ou lista direta
    if isinstance(data, dict) and "data" in data:
        raw = data.get("data") or []
    elif isinstance(data, list):
        raw = data

    for it in raw:
        items.append({
            "title": it.get("title") or it.get("headline") or "",
            "note": it.get("text") or it.get("summary") or "",
            "source": "FMP",
            "published_at": it.get("date") or it.get("publishedDate"),
            "url": it.get("url"),
        })

    return Response({"symbol": symbol, "count": len(items), "items": items}, status=status.HTTP_200_OK)


# Funcionalidade 2: histórico EOD e “detalhes”
@api_view(["GET"])
def history_eod_view(request, symbol: str):
    client = FMPClient()
    full = request.query_params.get("full", "true").lower() in ("1", "true", "yes")
    params = {}
    for key in ("from", "to", "limit"):
        if key in request.query_params:
            params[key] = request.query_params.get(key)

    try:
        data = client.historical_price_eod(symbol, full=full, **params)
    except RuntimeError as e:
        return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    series = []
    hist = _normalize_eod_payload(data)

    # se veio vazio e usuário pediu curto, refaz com /full
    if not hist and not full:
        try:
            data_full = client.historical_price_eod(symbol, full=True, **params)
            hist = _normalize_eod_payload(data_full)
        except RuntimeError as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    for row in hist:
        series.append({
            "date": row.get("date"),
            "close": row.get("close"),
            "open": row.get("open"),
            "high": row.get("high"),
            "low": row.get("low"),
            "volume": row.get("volume"),
        })

    return Response({"symbol": symbol, "series": series}, status=status.HTTP_200_OK)

@api_view(["GET"])
def details_view(request, symbol: str):
    """
    Detalhes atuais da ação via /stable/quote:
      - price, change, changesPercentage, timestamp (convertido se vier em unix)
    """
    from datetime import datetime, timezone

    client = FMPClient()
    try:
        raw = client.quote(symbol)  # FMP retorna lista
        if isinstance(raw, list) and raw:
            quote = raw[0]
        elif isinstance(raw, dict):
            quote = raw
        else:
            return Response({"detail": "Sem dados para o símbolo."},
                            status=status.HTTP_404_NOT_FOUND)

        # normalização
        ts = quote.get("timestamp") or quote.get("lastUpdated") or quote.get("date")
        as_of = None
        # se vier unix (int/str), converte
        try:
            if isinstance(ts, (int, float)) or (isinstance(ts, str) and ts.isdigit()):
                as_of = datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
            elif isinstance(ts, str):
                as_of = ts  # já é string ISO/data fornecida pela FMP
        except Exception:
            as_of = None

        payload = {
            "symbol": quote.get("symbol") or symbol,
            "name": quote.get("name"),
            "price": quote.get("price"),
            "change": quote.get("change"),
            "change_pct": quote.get("changesPercentage"),
            "as_of": as_of,
            # campos extras úteis (não obrigatórios)
            "day_high": quote.get("dayHigh"),
            "day_low": quote.get("dayLow"),
            "year_high": quote.get("yearHigh"),
            "year_low": quote.get("yearLow"),
            "market_cap": quote.get("marketCap"),
            "volume": quote.get("volume"),
        }
        return Response(payload, status=status.HTTP_200_OK)

    except RuntimeError as e:
        # Erros vindos do client FMP (_get/quote)
        return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        # Qualquer outro NameError/KeyError/etc => sempre JSON
        return Response({"detail": f"Internal error: {e.__class__.__name__}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Funcionalidade 3: Watchlist (CRUD)

@api_view(["GET"])
def search_view(request):
    q = request.query_params.get("q") or request.query_params.get("query")
    if not q:
        return Response({"detail": "Parâmetro 'q' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    limit = int(request.query_params.get("limit", 10))
    client = FMPClient()
    try:
        data = client.search(q, limit=limit)
    except RuntimeError as e:
        return _json_error(str(e), http_status=status.HTTP_502_BAD_GATEWAY)

    items = []
    for it in data or []:
        items.append({
            "symbol": it.get("symbol") or it.get("ticker"),
            "name": it.get("name") or it.get("companyName") or "",
            "exchange": it.get("exchangeShortName") or it.get("exchange") or "",
        })
    return Response({"count": len(items), "items": items}, status=status.HTTP_200_OK)

class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = WatchItem.objects.all().order_by("-updated_at")
    serializer_class = WatchItemSerializer
    permission_classes = [AllowAny]