from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MangaViewSet, ClienteViewSet, PedidoViewSet,
    InventarioBajoAPIView, ResumenTiendaAPIView
)

router = DefaultRouter()
router.register(r'mangas', MangaViewSet, basename='manga')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('', include(router.urls)),

    # Custom APIs
    path('inventario-bajo/', InventarioBajoAPIView.as_view(), name='inventario-bajo'),
    path('resumen/', ResumenTiendaAPIView.as_view(), name='resumen-tienda'),
]
