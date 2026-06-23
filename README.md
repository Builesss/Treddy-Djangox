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

## 🎨 Recursos Frontend — 100% Locales (Sin CDNs)

Todos los archivos de estilos y librerías JavaScript están almacenados y servidos **localmente** desde la carpeta `static/`. Esto está configurado en `treddy_project/settings.py` con la variable `STATICFILES_DIRS`.

| Librería | Versión | Ruta Local | Propósito |
|----------|---------|------------|-----------|
| **Bootstrap** | 5.3 | `static/css/bootstrap.min.css` | Sistema de grillas y componentes UI |
| **Bootstrap JS** | 5.3 | `static/js/bootstrap.bundle.min.js` | Componentes JS (modales, collapse) |
| **SweetAlert2** | 11.x | `static/js/vendor/sweetalert2.all.min.js` | Alertas y confirmaciones interactivas |
| **NProgress** | 0.2.0 | `static/js/vendor/nprogress.min.js` | Barra de progreso de carga SPA |
| **NProgress CSS** | 0.2.0 | `static/css/nprogress.css` | Estilos de la barra NProgress |

> ✅ **Sin CDN:** No existe ninguna referencia a `cdn.jsdelivr.net`, `cdnjs.cloudflare.com` ni servicios externos de recursos estáticos en ninguna plantilla del proyecto.

---

## 🔒 4 Capas de Seguridad Implementadas

El sistema aplica un modelo de defensa en profundidad con **4 capas independientes** de validación y protección:

### Capa 1 — Validación en el Cliente (HTML5 / Frontend)
Ubicación: atributos `pattern`, `required` y `type` en los formularios HTML.

```html
<!-- Ejemplo en templates/usuarios/login.html -->
<input type="email"
       pattern="^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
       required>
```

- Valida el formato del correo electrónico con Regex HTML5
- Exige contraseña con mínimo 8 caracteres, mayúscula y número
- Nombres solo con letras (sin caracteres especiales ni SQL)
- Teléfono con formato numérico válido

### Capa 2 — Validación en el Servidor (Python / Forms)
Ubicación: `usuarios/forms.py` — métodos `clean_*()` con el módulo `re`.

```python
# usuarios/forms.py
import re

def clean_username(self):
    username = self.cleaned_data.get('username', '')
    if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', username):
        raise ValidationError("El correo contiene caracteres no permitidos.")
    return username
```

- Re-valida todos los campos con las mismas expresiones regulares
- Impide que un atacante bypass la validación manipulando el HTML
- Verifica unicidad del email antes de registrar

### Capa 3 — Validación en el Modelo (Base de Datos / ORM)
Ubicación: `usuarios/models.py` y `productos/models.py`.

```python
# usuarios/models.py
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)        # Unicidad garantizada en BD
    tipo_usuario = models.CharField(...)          # Campo con choices restringidos
    estado = models.CharField(...)
```

- Campos con restricciones `unique`, `not null` a nivel de base de datos
- El modelo `Usuario` extiende `AbstractUser` de Django con contraseñas hasheadas (bcrypt)
- `@login_required` en todas las vistas protegidas
- Control de acceso por rol: clientes no pueden acceder a rutas de admin/vendedor
- Soft Delete en `Producto` (`is_deleted`) mantiene la integridad referencial

### Capa 4 — Seguridad de Infraestructura (Middleware / Settings)
Ubicación: `treddy_project/settings.py`.

```python
# Protección contra fuerza bruta — django-axes
AXES_FAILURE_LIMIT = 5       # Bloquea IP tras 5 intentos fallidos
AXES_COOLOFF_TIME = 1        # Tiempo de bloqueo: 1 hora
AXES_LOCKOUT_TEMPLATE = 'usuarios/lockout.html'

# Variables de entorno — django-environ
SECRET_KEY = env('SECRET_KEY')   # Clave secreta fuera del código fuente
DATABASES = {'default': env.db('DATABASE_URL')}  # Credenciales en .env

# Cabeceras de seguridad HTTP (en producción)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

- **`django-axes`**: bloqueo automático de IPs con intentos de fuerza bruta
- **`django-environ`**: variables sensibles en `.env` (excluido del repositorio con `.gitignore`)
- **`CsrfViewMiddleware`**: protección contra ataques CSRF en todos los formularios POST
- **`SecurityMiddleware`**: cabeceras HTTP de seguridad activadas
- **`AUTH_PASSWORD_VALIDATORS`**: validadores de contraseña del framework Django

---

## 📐 Patrones de Diseño Aplicados

| Patrón | Descripción | Archivo |
|--------|-------------|---------|
| **Strategy** | El `dashboard_view` selecciona plantilla y contexto según el rol del usuario | `usuarios/views.py` |
| **Observer** | `HistorialProducto` registra automáticamente cada cambio en productos | `productos/models.py` |
| **SPA (Arquitectural)** | Navegación sin recarga vía `fetch()` + partials HTML inyectados en `#spa-container` | `templates/base.html` |
| **Service Layer** | La lógica de checkout está separada en `services.py` fuera de las vistas | `productos/services.py` |
| **Soft Delete** | Los productos eliminados se marcan con `is_deleted=True` para preservar integridad | `productos/models.py` |
| **DRY (Herencia de Forms)** | `AdminRegistroForm` hereda de `CustomRegistroForm` sin repetir código | `usuarios/forms.py` |

---

## 📋 Bitácoras de Desarrollo

Las bitácoras semanales del proyecto se encuentran en el directorio `bitacoras/`.

| Fecha | Contenido |
|-------|-----------|
| 05-05-2026 | Configuración inicial, CustomUser, Bootstrap local, MVT |
| 12-05-2026 | CRUD de productos, formularios, plantillas SPA |
| 19-05-2026 | Módulo e-commerce: carrito, favoritos, pedidos |
| 26-05-2026 | Dashboard vendedor, gráficos, exportar CSV |
| 02-06-2026 | HistorialProducto (Observer), UML, README, pruebas de integración |

---

## 📊 Diagramas UML (PlantUML)

Los diagramas del sistema se encuentran en `docs/uml/` en formato PlantUML (`.puml`).

| Archivo | Tipo |
|---------|------|
| `arquitectura_mvt.puml` | Diagrama de componentes (MVT + SPA + Supabase) |
| `casos_de_uso.puml` | Casos de uso por rol |
| `diagrama_clases.puml` | Clases del sistema |
| `modelo_de_datos.puml` | Entidad-Relación (tablas PostgreSQL) |
| `patrones_diseno.puml` | Patrones de diseño aplicados |
| `estados_producto.puml` | Ciclo de vida del producto |
| `secuencia_checkout.puml` | Secuencia del proceso de compra |
| `secuencia_login.puml` | Secuencia del proceso de autenticación |

