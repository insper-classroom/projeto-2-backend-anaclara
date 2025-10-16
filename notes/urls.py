from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import search_view, details_view, WatchlistViewSet

router = DefaultRouter()
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    path('stocks/search', search_view),
    path('stocks/<str:symbol>/details', details_view),
    path('', include(router.urls)),
]
