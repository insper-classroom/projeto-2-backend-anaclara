from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    company_notes_view, history_eod_view, details_view,
    WatchlistViewSet
)

router = DefaultRouter()
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    # Funcionalidade 1
    path('stocks/<str:symbol>/notes', company_notes_view),

    # Funcionalidade 2
    path('stocks/<str:symbol>/history/eod', history_eod_view),
    path('stocks/<str:symbol>/details', details_view),

    # Funcionalidade 3
    path('', include(router.urls)),
]
