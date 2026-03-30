# 🐉 Manga Store API — Proyecto Django Módulo V

Sistema de administración para una tienda de mangas con inventario, clientes y pedidos.

---

## 🚀 Instalación y ejecución

### 1. Clonar / descomprimir el proyecto

```bash
cd manga_store
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario (para el Admin)

```bash
python manage.py createsuperuser
```

### 6. (Opcional) Cargar datos de ejemplo

```bash
python manage.py shell < seed_data.py
```

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

---

## 🔗 URLs disponibles

| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:8000/admin/` | Panel de administración Django |
| `http://127.0.0.1:8000/api/` | Raíz de la API (DRF browsable) |
| `http://127.0.0.1:8000/api/mangas/` | CRUD de mangas |
| `http://127.0.0.1:8000/api/clientes/` | CRUD de clientes |
| `http://127.0.0.1:8000/api/pedidos/` | CRUD de pedidos |
| `http://127.0.0.1:8000/api/inventario-bajo/` | Custom API: stock bajo |
| `http://127.0.0.1:8000/api/resumen/` | Custom API: resumen tienda |

---

## 📋 Endpoints detallados

### Mangas
```
GET    /api/mangas/                     → Lista todos los mangas
POST   /api/mangas/                     → Crea un manga
GET    /api/mangas/{id}/                → Detalle de un manga
PUT    /api/mangas/{id}/                → Actualiza un manga
DELETE /api/mangas/{id}/                → Elimina un manga
GET    /api/mangas/por-genero/          → Mangas agrupados por género

Filtros: ?genero=shonen  ?autor=Oda  ?activo=true
```

### Clientes
```
GET    /api/clientes/                   → Lista todos los clientes
POST   /api/clientes/                   → Registra un cliente
GET    /api/clientes/{id}/              → Detalle de un cliente
PUT    /api/clientes/{id}/              → Actualiza un cliente
DELETE /api/clientes/{id}/              → Elimina un cliente

Filtros: ?nombre=Juan  ?ciudad=Santa+Cruz
```

### Pedidos
```
GET    /api/pedidos/                    → Lista todos los pedidos
POST   /api/pedidos/                    → Crea un pedido (descuenta stock automáticamente)
GET    /api/pedidos/{id}/               → Detalle de un pedido con ítems
PUT    /api/pedidos/{id}/               → Actualiza un pedido
DELETE /api/pedidos/{id}/               → Elimina un pedido
PATCH  /api/pedidos/{id}/cambiar-estado/ → Cambia el estado del pedido

Filtros: ?estado=pendiente  ?cliente=1
```

### Custom APIs
```
GET /api/inventario-bajo/              → Mangas con menos de 5 unidades
GET /api/inventario-bajo/?limite=10    → Cambiar el límite
GET /api/resumen/                      → Resumen general de la tienda
```

---

## 📦 Ejemplo: Crear un pedido (POST /api/pedidos/)

```json
{
  "cliente": 1,
  "notas": "Entregar por la tarde",
  "detalles": [
    {
      "manga": 1,
      "cantidad": 2,
      "precio_unitario": 45.00
    },
    {
      "manga": 3,
      "cantidad": 1,
      "precio_unitario": 38.50
    }
  ]
}
```

---

## ✅ Cumplimiento de requisitos

| Requisito | Implementado |
|-----------|--------------|
| 1 Aplicación Django | ✅ `store` |
| 4 Models | ✅ Manga, Cliente, Pedido, DetallePedido |
| 2+ validaciones personalizadas | ✅ precio positivo, teléfono numérico, stock no negativo, cantidad vs stock |
| 2+ Models en Admin | ✅ Manga, Pedido, Cliente, DetallePedido |
| 3 ModelViewSet | ✅ MangaViewSet, ClienteViewSet, PedidoViewSet |
| 1 Custom API | ✅ InventarioBajoAPIView + ResumenTiendaAPIView |
| requirements.txt | ✅ En la raíz |

---

## 🛠 Tecnologías usadas

- Python 3.10+
- Django 4.2
- Django REST Framework 3.14
- SQLite (base de datos por defecto)
