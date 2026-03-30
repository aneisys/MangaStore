from django.contrib import admin
from .models import Manga, Cliente, Pedido, DetallePedido


# ─── Inline para ver detalles dentro del pedido ────────────────────────────────

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ['precio_unitario', 'subtotal']

    def subtotal(self, obj):
        return f'Bs. {obj.subtotal}' if obj.pk else '-'
    subtotal.short_description = 'Subtotal'


# ─── Admin Model 1: Manga ──────────────────────────────────────────────────────

@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'volumen', 'genero', 'precio', 'stock', 'activo', 'stock_estado']
    list_filter = ['genero', 'activo', 'editorial']
    search_fields = ['titulo', 'autor', 'editorial']
    list_editable = ['precio', 'stock', 'activo']
    ordering = ['titulo', 'volumen']
    readonly_fields = ['fecha_agregado']

    fieldsets = (
        ('Información del Manga', {
            'fields': ('titulo', 'autor', 'editorial', 'volumen', 'genero', 'descripcion')
        }),
        ('Precio e Inventario', {
            'fields': ('precio', 'stock', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_agregado',),
            'classes': ('collapse',)
        }),
    )

    def stock_estado(self, obj):
        if obj.stock == 0:
            return '🔴 Sin stock'
        elif obj.stock < 5:
            return '🟡 Stock bajo'
        return '🟢 OK'
    stock_estado.short_description = 'Estado stock'


# ─── Admin Model 2: Pedido ─────────────────────────────────────────────────────

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'estado', 'fecha_pedido', 'total_pedido']
    list_filter = ['estado', 'fecha_pedido']
    search_fields = ['cliente__nombre', 'cliente__email']
    readonly_fields = ['fecha_pedido', 'fecha_actualizacion']
    inlines = [DetallePedidoInline]

    def total_pedido(self, obj):
        return f'Bs. {obj.total}'
    total_pedido.short_description = 'Total'


# ─── Admin Model 3: Cliente ────────────────────────────────────────────────────

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'telefono', 'ciudad', 'activo', 'fecha_registro']
    list_filter = ['activo', 'ciudad']
    search_fields = ['nombre', 'email', 'telefono']
    readonly_fields = ['fecha_registro']


# ─── Admin Model 4: DetallePedido ──────────────────────────────────────────────

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'manga', 'cantidad', 'precio_unitario', 'subtotal_display']
    search_fields = ['pedido__id', 'manga__titulo']

    def subtotal_display(self, obj):
        return f'Bs. {obj.subtotal}'
    subtotal_display.short_description = 'Subtotal'
