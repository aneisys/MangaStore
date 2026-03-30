from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, F
from django.utils import timezone

from .models import Manga, Cliente, Pedido, DetallePedido
from .serializers import (
    MangaSerializer, ClienteSerializer,
    PedidoSerializer, PedidoCreateSerializer,
    DetallePedidoSerializer
)


# ─── ModelViewSets (mínimo 3 requeridos) ──────────────────────────────────────

class MangaViewSet(viewsets.ModelViewSet):
    """
    ViewSet 1: CRUD completo para el catálogo de mangas.
    GET    /api/mangas/           → listar todos
    POST   /api/mangas/           → crear nuevo manga
    GET    /api/mangas/{id}/      → detalle de un manga
    PUT    /api/mangas/{id}/      → actualizar manga
    DELETE /api/mangas/{id}/      → eliminar manga
    GET    /api/mangas/por_genero/ → filtrar por género
    """
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer

    def get_queryset(self):
        queryset = Manga.objects.all()
        genero = self.request.query_params.get('genero')
        autor = self.request.query_params.get('autor')
        activo = self.request.query_params.get('activo')

        if genero:
            queryset = queryset.filter(genero=genero)
        if autor:
            queryset = queryset.filter(autor__icontains=autor)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')

        return queryset

    @action(detail=False, methods=['get'], url_path='por-genero')
    def por_genero(self, request):
        """Retorna los mangas agrupados por género."""
        generos = {}
        for manga in Manga.objects.filter(activo=True):
            g = manga.get_genero_display()
            if g not in generos:
                generos[g] = []
            generos[g].append(MangaSerializer(manga).data)
        return Response(generos)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet 2: CRUD completo para clientes.
    GET    /api/clientes/         → listar todos
    POST   /api/clientes/         → registrar nuevo cliente
    GET    /api/clientes/{id}/    → detalle de un cliente
    PUT    /api/clientes/{id}/    → actualizar cliente
    DELETE /api/clientes/{id}/    → eliminar cliente
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_queryset(self):
        queryset = Cliente.objects.all()
        nombre = self.request.query_params.get('nombre')
        ciudad = self.request.query_params.get('ciudad')

        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if ciudad:
            queryset = queryset.filter(ciudad__icontains=ciudad)

        return queryset


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet 3: CRUD completo para pedidos.
    GET    /api/pedidos/           → listar todos
    POST   /api/pedidos/           → crear nuevo pedido
    GET    /api/pedidos/{id}/      → detalle de un pedido
    PUT    /api/pedidos/{id}/      → actualizar pedido
    DELETE /api/pedidos/{id}/      → eliminar pedido
    PATCH  /api/pedidos/{id}/cambiar-estado/ → cambiar estado del pedido
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoSerializer

    def get_queryset(self):
        queryset = Pedido.objects.all()
        estado = self.request.query_params.get('estado')
        cliente_id = self.request.query_params.get('cliente')

        if estado:
            queryset = queryset.filter(estado=estado)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        return queryset

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de un pedido específico."""
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')

        estados_validos = [c[0] for c in Pedido.ESTADO_CHOICES]
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Opciones: {estados_validos}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.estado = nuevo_estado
        pedido.save()
        return Response(PedidoSerializer(pedido).data)


# ─── Custom APIs (mínimo 1 requerida) ─────────────────────────────────────────

class InventarioBajoAPIView(APIView):
    """
    Custom API 1: Reporta mangas con stock bajo (menos de 5 unidades).
    GET /api/inventario-bajo/
    GET /api/inventario-bajo/?limite=10   → cambiar el límite de stock
    """

    def get(self, request):
        limite = int(request.query_params.get('limite', 5))
        mangas_bajo_stock = Manga.objects.filter(stock__lt=limite, activo=True)

        data = {
            'total_mangas_bajo_stock': mangas_bajo_stock.count(),
            'limite_configurado': limite,
            'mangas': MangaSerializer(mangas_bajo_stock, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)


class ResumenTiendaAPIView(APIView):
    """
    Custom API 2: Resumen general del estado de la tienda.
    GET /api/resumen/
    """

    def get(self, request):
        hoy = timezone.now().date()

        total_mangas = Manga.objects.filter(activo=True).count()
        total_clientes = Cliente.objects.filter(activo=True).count()
        total_pedidos = Pedido.objects.count()
        pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()

        pedidos_por_estado = {}
        for estado, label in Pedido.ESTADO_CHOICES:
            pedidos_por_estado[label] = Pedido.objects.filter(estado=estado).count()

        mangas_sin_stock = Manga.objects.filter(stock=0, activo=True).count()
        manga_mas_pedido = (
            DetallePedido.objects
            .values('manga__titulo')
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')
            .first()
        )

        data = {
            'resumen_general': {
                'total_mangas_activos': total_mangas,
                'total_clientes_activos': total_clientes,
                'total_pedidos': total_pedidos,
                'pedidos_realizados_hoy': pedidos_hoy,
                'mangas_sin_stock': mangas_sin_stock,
            },
            'pedidos_por_estado': pedidos_por_estado,
            'manga_mas_vendido': manga_mas_pedido,
        }
        return Response(data, status=status.HTTP_200_OK)
