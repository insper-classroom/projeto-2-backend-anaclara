from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    company_notes_view, history_eod_view, details_view,
    WatchlistViewSet, search_view
)

router = DefaultRouter()
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    path('stocks/search', search_view),                   # <— NOVA
    path('stocks/<str:symbol>/notes', company_notes_view),
    path('stocks/<str:symbol>/history/eod', history_eod_view),
    path('stocks/<str:symbol>/details', details_view),
    path('', include(router.urls)),
]

