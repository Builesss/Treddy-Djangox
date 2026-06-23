# ⚡ Treddy — Plataforma de Gestión de Inventario

Treddy es una aplicación web full-stack de gestión de inventario y e-commerce construida con **Django 6**, con arquitectura **MVT (Model-View-Template)**, base de datos en la nube con **Supabase (PostgreSQL)** y una interfaz SPA (Single Page Application) dinámica.

---

## 🚀 Características Principales

### 🛡️ Administrador
- Dashboard con estadísticas en tiempo real (usuarios, productos, estados)
- Gestión completa de productos (CRUD)
- Historial de auditoría de productos (creación, actualización, eliminación)
- Gestión de usuarios: visualización y eliminación con confirmación
- Exportación de inventario a CSV
- Registro de nuevos usuarios con asignación de roles

### 🛒 Cliente
- Catálogo de productos con búsqueda y filtros
- Lista de favoritos (toggle con corazón interactivo)
- Carrito de compras con sesión
- Proceso de checkout y generación de pedidos
- Historial de pedidos con detalle expandible
- Edición de perfil

### 🏪 Vendedor
- Gestión de productos (CRUD completo)
- Historial de auditoría propio
- Exportación a CSV

---

## 🏗️ Arquitectura

```
treddy-django/
├── treddy_project/       # Configuración principal del proyecto
│   ├── settings.py       # Settings con Supabase (dj-database-url)
│   └── urls.py
├── usuarios/             # App de usuarios y autenticación
│   ├── models.py         # Modelo Usuario personalizado
│   ├── views.py          # Login, Dashboard (patrón Strategy), perfil
│   └── forms.py          # Formularios de login, registro, perfil
├── productos/            # App de inventario y e-commerce
│   ├── models.py         # Producto, HistorialProducto, Favorito, Pedido
│   ├── views.py          # CRUD productos + carrito, favoritos, pedidos
│   └── urls.py
├── templates/            # Plantillas HTML (Django Template Language)
│   ├── base.html         # Layout SPA principal con sidebar y particles
│   ├── usuarios/         # Login, Registro, Dashboards por rol
│   └── productos/        # Catálogo, formularios, carrito, pedidos
├── static/               # CSS, JS y librerías de terceros
│   ├── css/custom.css    # Sistema de diseño Treddy
│   └── js/
├── bitacoras/            # Bitácoras de desarrollo del proyecto
└── docs/uml/             # Diagramas UML del sistema
```

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 6.0.6 |
| Base de Datos | Supabase (PostgreSQL 17) |
| ORM Connector | psycopg2-binary + dj-database-url |
| Frontend | Bootstrap 5 + CSS Variables + JS Vanilla |
| Alertas UI | SweetAlert2 |
| Barra de Progreso | NProgress |
| Autenticación | Django Auth (modelo personalizado) |

---

## ⚙️ Instalación y Configuración Local

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd Treddy-Django
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Edita `treddy_project/settings.py` y asegúrate de que el `DATABASE_URL` apunte a tu instancia de Supabase.

### 5. Aplicar migraciones
```bash
python manage.py migrate
```

### 6. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

---

## 👤 Roles de Usuario

| Rol | Acceso |
|-----|--------|
| `Administrador` | Control total: usuarios, productos, historial, reportes |
| `Vendedor` | Gestión de productos, historial propio, exportar CSV |
| `Cliente` | Catálogo, favoritos, carrito, pedidos, perfil |

---

## 📐 Patrones de Diseño Aplicados

- **Strategy Pattern** — Delegación de dashboard según el rol del usuario
- **Observer Pattern** — Registro automático de auditoría en `HistorialProducto`
- **SPA (Single Page Application)** — Navegación sin recargas via AJAX + partials
- **MVT (Model-View-Template)** — Arquitectura base de Django

---

## 📋 Bitácoras de Desarrollo

Las bitácoras semanales del proyecto se encuentran en el directorio `bitacoras/`.

---

## 📊 Diagramas UML

Los diagramas del sistema (arquitectura, casos de uso, clases, modelo de datos) se encuentran en `docs/uml/` en formato PlantUML (`.puml`).
