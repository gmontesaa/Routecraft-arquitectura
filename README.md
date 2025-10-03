# 🧭 RouteCraft

**RouteCraft** es una aplicación web construida con **Django** que permite a los usuarios descubrir, organizar y optimizar rutas turísticas en ciudades como Medellín, Bogotá y Barranquilla.  
El sistema integra **IA (OpenAI Embeddings)** para recomendaciones personalizadas de lugares según el interés del usuario, presupuesto y contexto, además de **Google Maps API** para cálculo de rutas.

---

## 🚀 Funcionalidades principales

- 📍 **Gestión de lugares (CRUD)**: añadir, editar y eliminar sitios turísticos con descripción, categoría, dirección, costos, coordenadas y foto.  
- ⭐ **Sistema de reseñas**: cada lugar puede recibir reseñas de usuarios con calificación (1 a 5 estrellas).  
- 🧮 **Recomendaciones con IA**:
  - Embeddings de descripciones de lugares generados con OpenAI.  
  - Recomendación de lugares relevantes a partir de la descripción ingresada por el usuario (ej. "quiero hacer deporte").  
  - Filtrado por **presupuesto**: bajo, medio o alto.  
- 🗺️ **Generación de rutas**:
  - Uso de **Google Maps Directions API** para obtener polilíneas y tiempos estimados.  
  - Servicio desacoplado mediante inversión de dependencias (DIP).  
- ⚙️ **Patrones de diseño aplicados**:
  - **DIP (Dependency Inversion)** para separar vistas de implementaciones externas (Google/OpenAI).  
  - **Strategy + Factory** para ordenar resultados (por distancia, rating, presupuesto o híbrido).  
  - **CBV + Mixins** en controladores CRUD.  
  - **Signals + normalización** en modelos para mantener `avg_rating` y `reviews_count`.

---

## 📂 Estructura del proyecto

routecraft/
├── manage.py
├── routecraft/ # Configuración principal
├── places/ # App principal: lugares, reseñas, IA, rutas
│ ├── adapters/ # Adaptadores OpenAI + Google Maps (DIP)
│ ├── strategies/ # Estrategias de ranking (Strategy + Factory)
│ ├── forms.py # Formularios para CRUD
│ ├── models.py # Modelos Place y Review
│ ├── views.py # Vistas FBV (IA, rutas)
│ ├── views_cbv.py # Vistas CBV (CRUD)
│ ├── signals.py # Signals para recalcular ratings
│ └── urls.py # URLs de la app
├── events/ # App de eventos
├── accounts/ # App de usuarios
├── docs/ # Documentación de actividades
│ ├── actividad2_revision_calidad.md
│ ├── actividad4_patron_python.md
│ └── actividad5_patrones_django.md
└── generate_embeddings.py # Script standalone para embeddings


---

## 🛠️ Tecnologías usadas

- **Backend**: Django 4.2  
- **Base de datos**: SQLite (desarrollo)  
- **Frontend**: Templates Django + Bootstrap  
- **IA**: OpenAI Embeddings API  
- **Mapas**: Google Maps Directions API  
- **Otros**: Pillow, pandas, matplotlib, numpy  

---

## 📑 Documentación académica

- **Actividad 2**: Revisión autocrítica (Usabilidad, Compatibilidad, Rendimiento, Seguridad).  
- **Actividad 3**: Inversión de Dependencias (DIP con adaptadores OpenAI/Google).  
- **Actividad 4**: Patrón Strategy + Factory aplicado en ranking de lugares.  
- **Actividad 5**: CBV + Mixins (controladores) y Signals + normalización (modelos).  

---

## ✨ Uso

1. Ingresar a `/places/` para listar lugares con soporte de ordenamiento:
   - `?order=distance`
   - `?order=rating`
   - `?order=budget`
   - `?order=hybrid` (por defecto)

2. Crear/editar lugares en `/places/create/` (requiere autenticación).  

3. Acceder a `/ruta-ai/`:
   - GET: devuelve formulario HTML.
   - POST: recibe JSON con:
     ```json
     {
       "ciudad": "medellin",
       "presupuesto": "medio",
       "prompt": "quiero hacer deporte"
     }
     ```
     y devuelve lugares recomendados con embeddings.

4. Acceder a `/obtener_ruta_google_maps/`:
   - POST: recibe JSON con ids de lugares
     ```json
     { "lugares_ids": [1, 2, 3] }
     ```
   - Devuelve la polilínea de la ruta y duración total en minutos.

---

## 👨‍💻 Autor

Proyecto desarrollado por **Gerónimo Montes Acebedo Y Luis Estiven Moreno**  
Curso: **Arquitectura de Software (ST0251)**  
Universidad EAFIT – 2025
