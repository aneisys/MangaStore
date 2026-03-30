from rest_framework import serializers
from .models import Manga, Cliente, Pedido, DetallePedido


class MangaSerializer(serializers.ModelSerializer):
    stock_bajo = serializers.ReadOnlyField()
    genero_display = serializers.CharField(source='get_genero_display', read_only=True)

    class Meta:
        model = Manga
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    total_pedidos = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_total_pedidos(self, obj):
        return obj.pedidos.count()


class DetallePedidoSerializer(serializers.ModelSerializer):
    manga_titulo = serializers.CharField(source='manga.titulo', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetallePedido
        fields = ['id', 'manga', 'manga_titulo', 'cantidad', 'precio_unitario', 'subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'


class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer especial para crear pedidos con sus detalles."""

    detalles = DetallePedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ['cliente', 'notas', 'detalles']

    def validate_detalles(self, detalles):
        if not detalles:
            raise serializers.ValidationError('El pedido debe tener al menos un ítem.')
        return detalles

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        pedido = Pedido.objects.create(**validated_data)

        for detalle_data in detalles_data:
            manga = detalle_data['manga']
            cantidad = detalle_data['cantidad']

            # Verificar stock
            if manga.stock < cantidad:
                pedido.delete()
                raise serializers.ValidationError(
                    f'Stock insuficiente para "{manga.titulo}". Disponible: {manga.stock}'
                )

            # Crear detalle con precio actual del manga
            DetallePedido.objects.create(
                pedido=pedido,
                manga=manga,
                cantidad=cantidad,
                precio_unitario=manga.precio
            )

            # Descontar stock
            manga.stock -= cantidad
            manga.save()

        return pedido
