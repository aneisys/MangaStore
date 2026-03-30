"""
Script para cargar datos de ejemplo.
Ejecutar con: python manage.py shell < seed_data.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manga_store.settings')
django.setup()

from store.models import Manga, Cliente, Pedido, DetallePedido

print("🗑  Limpiando datos anteriores...")
DetallePedido.objects.all().delete()
Pedido.objects.all().delete()
Cliente.objects.all().delete()
Manga.objects.all().delete()

print("📚 Creando mangas...")
mangas = [
    Manga(titulo='One Piece', autor='Eiichiro Oda', editorial='Shueisha', genero='shonen', volumen=1, precio=45.00, stock=20, descripcion='La gran aventura de Monkey D. Luffy para convertirse en el Rey de los Piratas.'),
    Manga(titulo='One Piece', autor='Eiichiro Oda', editorial='Shueisha', genero='shonen', volumen=2, precio=45.00, stock=15),
    Manga(titulo='Naruto', autor='Masashi Kishimoto', editorial='Shueisha', genero='shonen', volumen=1, precio=42.00, stock=10),
    Manga(titulo='Attack on Titan', autor='Hajime Isayama', editorial='Kodansha', genero='seinen', volumen=1, precio=50.00, stock=8),
    Manga(titulo='Demon Slayer', autor='Koyoharu Gotouge', editorial='Shueisha', genero='shonen', volumen=1, precio=48.00, stock=3, descripcion='Tanjiro busca la cura para su hermana convertida en demonio.'),
    Manga(titulo='Berserk', autor='Kentaro Miura', editorial='Hakusensha', genero='seinen', volumen=1, precio=55.00, stock=2),
    Manga(titulo='Sailor Moon', autor='Naoko Takeuchi', editorial='Kodansha', genero='shojo', volumen=1, precio=40.00, stock=0, activo=True),
    Manga(titulo='My Hero Academia', autor='Kohei Horikoshi', editorial='Shueisha', genero='shonen', volumen=1, precio=44.00, stock=12),
    Manga(titulo='Re:Zero', autor='Tappei Nagatsuki', editorial='MF Bunko J', genero='isekai', volumen=1, precio=52.00, stock=6),
    Manga(titulo='Vinland Saga', autor='Makoto Yukimura', editorial='Kodansha', genero='seinen', volumen=1, precio=58.00, stock=4),
]
Manga.objects.bulk_create(mangas)
print(f"  ✅ {len(mangas)} mangas creados")

print("👤 Creando clientes...")
clientes = [
    Cliente(nombre='Juan Pérez', email='juan@example.com', telefono='77712345', direccion='Av. Monseñor Rivero 123', ciudad='Santa Cruz'),
    Cliente(nombre='María García', email='maria@example.com', telefono='71198765', direccion='Calle Sucre 456', ciudad='La Paz'),
    Cliente(nombre='Carlos López', email='carlos@example.com', telefono='69087654', direccion='Av. América 789', ciudad='Cochabamba'),
    Cliente(nombre='Ana Rodríguez', email='ana@example.com', telefono='76543210', direccion='Calle Bolívar 321', ciudad='Santa Cruz'),
]
Cliente.objects.bulk_create(clientes)
print(f"  ✅ {len(clientes)} clientes creados")

print("🛒 Creando pedidos...")
manga_op1 = Manga.objects.get(titulo='One Piece', volumen=1)
manga_naruto = Manga.objects.get(titulo='Naruto', volumen=1)
manga_aot = Manga.objects.get(titulo='Attack on Titan', volumen=1)
manga_mha = Manga.objects.get(titulo='My Hero Academia', volumen=1)

cliente1 = Cliente.objects.get(email='juan@example.com')
cliente2 = Cliente.objects.get(email='maria@example.com')

pedido1 = Pedido.objects.create(cliente=cliente1, estado='entregado', notas='Primera compra')
DetallePedido.objects.create(pedido=pedido1, manga=manga_op1, cantidad=2, precio_unitario=manga_op1.precio)
DetallePedido.objects.create(pedido=pedido1, manga=manga_naruto, cantidad=1, precio_unitario=manga_naruto.precio)
manga_op1.stock -= 2
manga_op1.save()
manga_naruto.stock -= 1
manga_naruto.save()

pedido2 = Pedido.objects.create(cliente=cliente2, estado='enviado', notas='Envío urgente')
DetallePedido.objects.create(pedido=pedido2, manga=manga_aot, cantidad=1, precio_unitario=manga_aot.precio)
DetallePedido.objects.create(pedido=pedido2, manga=manga_mha, cantidad=3, precio_unitario=manga_mha.precio)
manga_aot.stock -= 1
manga_aot.save()
manga_mha.stock -= 3
manga_mha.save()

pedido3 = Pedido.objects.create(cliente=cliente1, estado='pendiente')
DetallePedido.objects.create(pedido=pedido3, manga=manga_mha, cantidad=1, precio_unitario=manga_mha.precio)

print("  ✅ 3 pedidos creados")
print("\n🎉 ¡Datos de ejemplo cargados exitosamente!")
print("   Ejecuta: python manage.py runserver")
print("   Admin:   http://127.0.0.1:8000/admin/")
print("   API:     http://127.0.0.1:8000/api/")
