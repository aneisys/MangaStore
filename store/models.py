from django.db import models
from django.core.exceptions import ValidationError
import re


# ─── Validaciones personalizadas ───────────────────────────────────────────────

def validar_precio_positivo(valor):
    """Validación 1: El precio debe ser mayor que cero."""
    if valor <= 0:
        raise ValidationError(
            f'El precio debe ser mayor que cero. Valor ingresado: {valor}'
        )

def validar_telefono(valor):
    """Validación 2: El teléfono solo debe contener números y tener entre 7 y 15 dígitos."""
    if not re.match(r'^\d{7,15}$', valor):
        raise ValidationError(
            'El teléfono debe contener solo números y tener entre 7 y 15 dígitos.'
        )

def validar_stock_no_negativo(valor):
    """Validación 3: El stock no puede ser negativo."""
    if valor < 0:
        raise ValidationError('El stock no puede ser un valor negativo.')


# ─── Modelos ───────────────────────────────────────────────────────────────────

class Manga(models.Model):
    """Model 1: Catálogo de mangas disponibles en la tienda."""

    GENERO_CHOICES = [
        ('shonen', 'Shōnen'),
        ('shojo', 'Shōjo'),
        ('seinen', 'Seinen'),
        ('josei', 'Josei'),
        ('isekai', 'Isekai'),
        ('mecha', 'Mecha'),
        ('deportes', 'Deportes'),
        ('terror', 'Terror'),
        ('comedia', 'Comedia'),
        ('otro', 'Otro'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Título')
    autor = models.CharField(max_length=100, verbose_name='Autor')
    editorial = models.CharField(max_length=100, verbose_name='Editorial', default='Desconocida')
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, default='otro', verbose_name='Género')
    volumen = models.PositiveIntegerField(default=1, verbose_name='Número de volumen')
    precio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[validar_precio_positivo],
        verbose_name='Precio (Bs)'
    )
    stock = models.IntegerField(
        default=0,
        validators=[validar_stock_no_negativo],
        verbose_name='Stock disponible'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    fecha_agregado = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de agregado')
    activo = models.BooleanField(default=True, verbose_name='Activo en tienda')

    class Meta:
        verbose_name = 'Manga'
        verbose_name_plural = 'Mangas'
        ordering = ['titulo', 'volumen']

    def __str__(self):
        return f'{self.titulo} - Vol. {self.volumen} ({self.autor})'

    @property
    def stock_bajo(self):
        return self.stock < 5


class Cliente(models.Model):
    """Model 2: Clientes registrados en la tienda."""

    nombre = models.CharField(max_length=100, verbose_name='Nombre completo')
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    telefono = models.CharField(
        max_length=15,
        validators=[validar_telefono],
        verbose_name='Teléfono'
    )
    direccion = models.TextField(verbose_name='Dirección de envío')
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad', default='Santa Cruz')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    activo = models.BooleanField(default=True, verbose_name='Cliente activo')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.email})'


class Pedido(models.Model):
    """Model 3: Pedidos realizados por los clientes."""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name='Cliente'
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del pedido')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado del pedido'
    )
    direccion_envio = models.TextField(verbose_name='Dirección de envío', blank=True)
    notas = models.TextField(blank=True, null=True, verbose_name='Notas adicionales')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente.nombre} [{self.estado}]'

    @property
    def total(self):
        return sum(detalle.subtotal for detalle in self.detalles.all())

    def save(self, *args, **kwargs):
        # Auto-completar dirección de envío con la del cliente si está vacía
        if not self.direccion_envio and self.cliente_id:
            self.direccion_envio = self.cliente.direccion
        super().save(*args, **kwargs)


class DetallePedido(models.Model):
    """Model 4: Ítems individuales dentro de cada pedido."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Pedido'
    )
    manga = models.ForeignKey(
        Manga,
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        verbose_name='Manga'
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    precio_unitario = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Precio unitario (al momento del pedido)'
    )

    class Meta:
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalles de pedido'

    def __str__(self):
        return f'{self.cantidad}x {self.manga.titulo} (Pedido #{self.pedido.pk})'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        # Guardar el precio del manga al momento del pedido
        if not self.precio_unitario:
            self.precio_unitario = self.manga.precio
        super().save(*args, **kwargs)

    def clean(self):
        # Validar que la cantidad pedida no supere el stock disponible
        if self.manga and self.cantidad > self.manga.stock:
            raise ValidationError(
                f'No hay suficiente stock. Disponible: {self.manga.stock}, solicitado: {self.cantidad}'
            )
