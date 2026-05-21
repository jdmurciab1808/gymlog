# 🏋️ GymLog — Planificador de Rutinas y Progreso Personal

Aplicación web desarrollada con **Django 5** como proyecto parcial final.

## Funcionalidades
- Registro de usuario con login/logout
- CRUD completo de **Ejercicios** (con categoría y grupo muscular)
- CRUD completo de **Rutinas** (agrupaciones de ejercicios)
- **Sesiones de entrenamiento** con registro de series, peso y repeticiones
- **Récords personales** (PR) por ejercicio
- **Gráfica de progreso** de peso levantado por ejercicio (Chart.js)
- Panel de **Admin Django** con todos los modelos
- **18 tests** cubriendo modelos, vistas y formularios

## Tecnologías
- Django 5 + SQLite
- Whitenoise (archivos estáticos)
- Gunicorn (servidor WSGI)
- Chart.js (gráficas de progreso)

## Instalación local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tests

```bash
python manage.py test workouts --verbosity=2
```

## Despliegue
Desplegado en Railway. Ver URL en la entrega.
