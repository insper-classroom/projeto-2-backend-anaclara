from datetime import datetime
from django.utils.dateparse import parse_date

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import WatchItem
from .serializers.watchlist import WatchItemSerializer
from .services.fmp import FMPClient


# Funcionalidade 1: company notes
@api_view(["GET"])
def company_notes_view(request, symbol: str):
    client = FMPClient()
    # repassa alguns filtros comuns, se vierem
    params = {}
    for key in ("limit", "page", "from", "to"):
        if key in request.query_params:
            params[key] = request.query_params.get(key)

    data = client.company_notes(symbol, **params)
    items = []
    if isinstance(data, dict) and "data" in data:
        # alguns endpoints da FMP retornam {"data":[...]}
        raw = data.get("data", [])
    else:
        raw = data if isinstance(data, list) else []

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

    data = client.historical_price_eod(symbol, full=full, **params)

    # Normalização para um contrato consistente
    series = []
    # FMP costuma devolver {"symbol":"AMZN","historical":[{...},...]}
    hist = data.get("historical", []) if isinstance(data, dict) else []
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
    Contrato final de 'detalhes' para o front:
    - price: último close
    - previous_close: penúltimo
    - change / change_pct
    - as_of: data do último candle
    """
    client = FMPClient()
    data = client.historical_price_eod(symbol, full=False, limit=2)

    hist = data.get("historical", []) if isinstance(data, dict) else []
    if not hist:
        return Response({"detail": "Sem dados para o símbolo."}, status=status.HTTP_404_NOT_FOUND)

    # Ordena por data descendente se necessário
    hist_sorted = sorted(hist, key=lambda x: x.get("date"), reverse=True)
    last = hist_sorted[0]
    prev = hist_sorted[1] if len(hist_sorted) > 1 else None

    price = last.get("close")
    previous = prev.get("close") if prev else None
    change = round(price - previous, 6) if (price is not None and previous is not None) else None
    change_pct = round((change / previous) * 100, 4, ) if (change is not None and previous not in (None, 0)) else None

    return Response({
        "symbol": symbol,
        "price": price,
        "previous_close": previous,
        "change": change,
        "change_pct": change_pct,
        "as_of": last.get("date"),
    }, status=status.HTTP_200_OK)


# Funcionalidade 3: Watchlist (CRUD)
class WatchlistViewSet(viewsets.ModelViewSet):
    """
    CRUD de itens de watchlist com target e direção.
    Em produção, use IsAuthenticated; por hora deixo leitura aberta.
    """
    queryset = WatchItem.objects.all().order_by("-updated_at")
    serializer_class = WatchItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user if self.request and self.request.user.is_authenticated else None
        if user:
            qs = qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request and self.request.user.is_authenticated else None
        serializer.save(user=user)
