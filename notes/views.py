from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from .models import WatchItem
from .serializers.watchlist import WatchItemSerializer
from .services import yahoo, brapi, stooq

def _is_b3(symbol: str) -> bool:
    return symbol.upper().endswith(".SA")

@api_view(["GET"])
def search_view(request):
    q = request.query_params.get("q") or request.query_params.get("query")
    if not q:
        return Response({"detail": "Parâmetro 'q' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    limit = int(request.query_params.get("limit", 10))

    # Yahoo primeiro; se nada, tenta brapi (bom p/ B3)
    try:
        data = yahoo.search(q, limit=limit)
        if data.get("count"):
            return Response(data, status=status.HTTP_200_OK)
    except Exception:
        pass
    try:
        data = brapi.search(q, limit=limit)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e2:
        return Response({"detail": "Busca indisponível no momento."}, status=status.HTTP_502_BAD_GATEWAY)

def _is_b3(symbol: str) -> bool:
    return symbol.upper().endswith(".SA")

@api_view(["GET"])
def details_view(request, symbol: str):
    symbol_up = symbol.upper()

    if _is_b3(symbol_up):
        # B3: brapi primeiro, depois Yahoo
        try:
            d = brapi.quote(symbol_up)
            if d:
                return Response(d, status=status.HTTP_200_OK)
        except Exception:
            pass
        try:
            d = yahoo.quote(symbol_up)
            if d:
                return Response(d, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Cotações indisponíveis no momento."}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({}, status=status.HTTP_200_OK)

    # EUA/outros: Yahoo -> Stooq
    try:
        d = yahoo.quote(symbol_up)
        if d:
            return Response(d, status=status.HTTP_200_OK)
    except Exception:
        pass
    try:
        d = stooq.quote(symbol_up)
        if d:
            return Response(d, status=status.HTTP_200_OK)
    except Exception:
        return Response({"detail": "Cotações indisponíveis no momento."}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({}, status=status.HTTP_200_OK)


class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = WatchItem.objects.all().order_by("-updated_at")
    serializer_class = WatchItemSerializer
    permission_classes = [AllowAny]
