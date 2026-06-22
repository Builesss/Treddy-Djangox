# Treddy - Proyecto Final SENA

Treddy es una plataforma web desarrollada en Django, orientada a la gestión de inventario y comercio con diferentes roles de usuario (Administrador, Vendedor, Cliente). El proyecto se desarrolló cumpliendo estrictamente con los lineamientos del SENA y aplicando principios SOLID, DRY y arquitectura por capas (MVT).

## 🚀 Módulos Implementados

1. **Gestión de Usuarios y Roles:** Autenticación personalizada (`CustomUser`) con roles definidos y tableros (Dashboards) dinámicos según los permisos.
2. **Single Page Application (SPA):** Navegación sin recargas utilizando `Fetch API`, `NProgress` y el API `History` de HTML5.
3. **CRUD de Productos:** Sistema completo de gestión de inventarios (Crear, Leer, Actualizar, Eliminar).
4. **Historial y Auditoría:** Registro automático de las acciones realizadas sobre los productos por parte de administradores y vendedores.
5. **Seguridad Avanzada (4 Capas):**
   - **Base de Datos:** Validadores `Regex`, `MinLength` y `MinValue` directamente en los Modelos.
   - **Servidor:** Métodos `clean()` en Django Forms para sanitización de datos.
   - **HTML5:** Atributos `pattern`, `min`, `maxlength` requeridos por el navegador.
   - **JavaScript:** Intercepción dinámica en el Frontend con SweetAlert2 antes del envío de peticiones.

## 📐 Patrones de Diseño Aplicados

Para garantizar escalabilidad, mantenibilidad y un código limpio profesional, se han documentado y aplicado los siguientes patrones de diseño de software:

1. **MVT (Model-View-Template):**
   - Es una variante arquitectónica del MVC utilizada por Django. Separa la lógica de acceso a datos (Models), la presentación (Templates) y la lógica de negocio (Views).

2. **Observer (Observador):**
   - Se utiliza para la creación del **Historial de Productos**. Cada vez que ocurre un evento en el CRUD (ej. una actualización o eliminación), se "notifica" a la capa de registro (o usando Signals en implementaciones más grandes) para insertar un registro en la tabla de auditoría (`HistorialProducto`) de manera automática.

3. **Decorator (Decorador):**
   - Implementado extensamente para proteger las rutas. Envolviendo las funciones de las vistas con `@login_required`, modificamos el comportamiento de acceso a la vista dinámicamente sin alterar el código de negocio interno.

4. **Singleton (Instancia Única):**
   - Se aplica mediante el uso del ORM de Django (Connection Handler), asegurando que las conexiones a la base de datos se mantengan bajo un mismo pool o instancia controlada durante el ciclo de vida de cada petición.

5. **Factory Method (Método Fábrica):**
   - Se evidencia en el uso de los formularios y serializadores en las vistas, delegando en las clases genéricas de Django (`UserCreationForm` modificado) la responsabilidad de "crear" los diferentes tipos de objetos Usuario.

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3, Django 6
- **Frontend:** HTML5, CSS3 Nativo, JavaScript Vanilla
- **Estilos:** Bootstrap 5 (Local, sin CDNs)
- **Librerías UX:** SweetAlert2, NProgress (Ambas instaladas localmente para uso offline)
- **Base de datos:** SQLite3

## 📦 Instalación Local

1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual e instalar los requerimientos: `pip install -r requirements.txt` (si existe) o las dependencias de Django.
4. Aplicar las migraciones: `python manage.py migrate`
5. Ejecutar el servidor de pruebas: `python manage.py runserver`

*Nota: La aplicación contiene todas las librerías estáticas (Bootstrap, NProgress, SweetAlert2) empaquetadas localmente, garantizando su funcionamiento sin conexión a internet según lineamientos de evaluación.*
