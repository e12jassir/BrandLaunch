# BrandLaunch — Contexto del Proyecto

## Idea principal

**BrandLaunch** es una aplicación web para que negocios, emprendedores y profesionales puedan lanzar una presencia online profesional mediante una landing page moderna con panel administrativo.

No es solo una página bonita. La idea es construir una solución completa:

> “Una landing page profesional con panel de gestión para captar clientes, administrar contenido básico y organizar contactos.”

---

## Problema que resuelve

Muchos negocios pequeños tienen estos problemas:

- no tienen página web
- dependen solo de Instagram o WhatsApp
- tienen una web vieja o poco profesional
- no pueden editar servicios o textos sin llamar a alguien
- reciben contactos desordenados por WhatsApp
- pierden leads porque no tienen formulario ni seguimiento
- no muestran sus servicios de forma clara
- no tienen una presencia digital confiable

BrandLaunch resuelve eso ofreciendo una landing profesional con gestión básica.

---

## Usuario objetivo

BrandLaunch está pensado para:

- negocios locales
- emprendedores
- profesionales independientes
- pequeñas marcas
- restaurantes
- barberías
- clínicas
- consultores
- agencias pequeñas
- gimnasios
- inmobiliarias
- técnicos independientes

Ejemplos:
- odontólogo que necesita captar pacientes
- barbería que quiere recibir reservas
- agencia que quiere mostrar servicios
- consultor que necesita una página profesional
- negocio local que quiere contacto por WhatsApp
- restaurante que quiere mostrar menú y ubicación

---

## Propuesta de valor

BrandLaunch permite:

- tener una landing page profesional
- mostrar servicios y beneficios
- recibir leads por formulario
- contactar por WhatsApp
- administrar servicios desde un panel
- editar testimonios/demo social proof
- revisar contactos recibidos
- exportar leads a CSV
- mejorar la confianza del negocio online

La promesa:

> “Lanza una presencia online profesional para tu negocio, capta clientes y administra tu contenido desde un panel simple.”

---

## MVP recomendado

Primero construimos una versión fuerte pero realista.

### Módulo 1: Landing pública

Debe incluir:

- header moderno
- hero section con propuesta clara
- botón principal de WhatsApp/contacto
- sección de servicios
- sección de beneficios
- sección “cómo funciona” o “por qué elegirnos”
- testimonios demo
- formulario de contacto
- footer con datos del negocio
- diseño responsive
- SEO básico

Contenido demo recomendado:

Negocio ficticio:
**Nova Studio Digital**
o
**Clínica Sonrisa Caribe**
o
**Barbería Distrito 21**

Podemos escoger uno según lo que más venda visualmente. Para Workana yo elegiría:

> **Nova Studio Digital**

Porque permite mostrar un negocio moderno y flexible.

---

### Módulo 2: Panel administrativo

Debe incluir:

- login simple
- dashboard con métricas
- listado de leads/contactos recibidos
- detalle de lead
- gestión de servicios
- gestión de testimonios
- edición de textos principales
- exportación de leads a CSV

Métricas del dashboard:

- total de leads
- leads nuevos
- servicios activos
- testimonios publicados
- última solicitud recibida

---

### Módulo 3: Leads

Funciones:

- formulario público guarda leads
- ver leads desde admin
- marcar lead como nuevo/contactado/cerrado
- buscar leads
- exportar leads a CSV

Campos:

- nombre
- email
- teléfono
- servicio de interés
- mensaje
- estado
- fecha

Estados:

- nuevo
- contactado
- cerrado

---

### Módulo 4: Servicios

Funciones:

- listar servicios
- crear servicio
- editar servicio
- activar/desactivar servicio

Campos:

- título
- descripción
- precio desde opcional
- icono o categoría
- estado activo/inactivo

---

### Módulo 5: Testimonios

Funciones:

- listar testimonios
- crear testimonio demo
- editar testimonio
- activar/desactivar testimonio

Campos:

- nombre
- cargo/empresa
- comentario
- rating
- estado activo/inactivo

---

## Stack recomendado

Para mantener coherencia con tu perfil:

### Backend
**Python + Flask**

Por qué:
- fácil de desarrollar rápido
- ideal para formularios, paneles y CRUD
- demuestra backend real
- combina bien con SQLite

### Base de datos
**SQLite**

Por qué:
- simple
- perfecto para demo
- no requiere servidor externo
- ideal para portfolio

### Frontend
**HTML + CSS + JavaScript**

Por qué:
- demuestra fundamentos
- sirve para landing visual
- se puede hacer muy premium sin framework
- más fácil de explicar en Workana

### Export CSV
Python nativo con `csv`.

---

## Baseline técnico obligatorio

Para que esto NO termine siendo una demo frágil, arrancar con esta base:

### Testing
- `pytest`
- carpeta `/tests`
- cubrir como mínimo formularios, leads, servicios, testimonios y export CSV

### Calidad de código
- `ruff`
- código formateado y chequeado desde el inicio

### Configuración
- `.env.example`
- `config.py`
- separar configuración de desarrollo y secretos del código

### Plantillas
- Jinja2 usando el sistema de templates de Flask

### Estructura mínima sana
No dejar crecer todo en un único `app.py` gigante. Separar temprano:

```txt
BrandLaunch/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── /routes
├── /services
├── /database
├── /templates
├── /static
└── /tests
```

### Riesgos funcionales que hay que diseñar bien
- validación de formulario público
- manejo de estados de leads (`nuevo`, `contactado`, `cerrado`)
- búsqueda y detalle de leads
- exportación CSV consistente
- CRUD admin sin romper contenido público

---

## Skills recomendadas para OpenCode

### Instaladas en este repo
- `frontend-design`
- `web-design-guidelines`
- `copywriting`
- `page-cro`
- `seo-audit`
- `webapp-testing`
- `systematic-debugging`
- `test-driven-development`
- `verification-before-completion`

### Estado
Para este stack y esta etapa, el set instalado ya está bien balanceado. Combina diseño, marketing, testing y disciplina de backend sin meter skills que no aplican al stack.

---

## Estructura sugerida

```txt
BrandLaunch/
├── app.py
├── requirements.txt
├── README.md
├── AGENT.md
├── .gitignore
├── database.db
├── /templates
│   ├── base.html
│   ├── landing.html
│   ├── admin_base.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── leads.html
│   ├── lead_detail.html
│   ├── services.html
│   ├── service_form.html
│   ├── testimonials.html
│   └── testimonial_form.html
├── /static
│   ├── css
│   │   └── styles.css
│   ├── js
│   │   └── app.js
│   └── img
├── /database
│   └── schema.sql
└── /docs
    └── screenshots
```

---

## Diseño visual

Este proyecto debe ser más visual que QuoteFlow.

Debe sentirse:
- premium
- moderno
- confiable
- comercial
- orientado a conversión

Paleta sugerida:
- fondo claro
- azul profundo o negro suave
- acento verde/azul eléctrico
- blanco
- gris elegante

Estilo:
- hero grande
- cards modernas
- botones claros
- sombras suaves
- buena tipografía
- espacios amplios
- mobile-first

Inspiración:
- landing SaaS
- agencia digital premium
- páginas tipo Webflow/Framer
- NO parecer Bootstrap básico

---

## Modelo de datos básico

### leads
```txt
id
name
email
phone
service_interest
message
status
created_at
```

### services
```txt
id
title
description
starting_price
icon
is_active
created_at
```

### testimonials
```txt
id
name
role
comment
rating
is_active
created_at
```

### site_settings
```txt
id
key
value
```

Para MVP, `site_settings` puede manejar:
- hero_title
- hero_subtitle
- whatsapp_number
- business_email
- business_name

---

## Datos demo

Negocio demo sugerido:

### Nova Studio Digital

Servicios:
- Diseño de landing pages
- Automatización para negocios
- Gestión de presencia digital
- Soporte técnico remoto

Testimonios demo:
- “Me ayudaron a ordenar mis contactos y recibir más solicitudes desde la web.”
- “La landing se ve profesional y ahora puedo mostrar mis servicios de forma clara.”
- “El panel me permite revisar contactos sin perder mensajes importantes.”

Leads demo:
- Laura Gómez — landing page
- Andrés Pérez — automatización
- Camila Torres — soporte técnico

Importante:
Los testimonios deben marcarse como **demo content** en el README para no mentir.

---

## README debe vender

Debe incluir:

1. Qué es BrandLaunch
2. Problema que resuelve
3. Features
4. Stack
5. Screenshots
6. Demo flow
7. Cómo correrlo
8. Próximas mejoras
9. Nota de contenido demo

Frase de venta:

> BrandLaunch is a business-focused landing page and admin panel that helps small businesses launch a professional online presence, capture leads, manage services, and organize contact requests.

---

## Qué debe demostrar en Workana

Este proyecto debe demostrar que sabés:

- diseñar una landing profesional
- pensar en conversión
- crear formularios funcionales
- conectar frontend con backend
- guardar datos en base de datos
- crear panel administrativo
- implementar CRUD básico
- exportar información
- construir soluciones útiles para negocios

---

## Resultado esperado

Al final deberíamos tener:

- landing page visualmente premium
- panel admin funcional
- formulario conectado a base de datos
- gestión de leads
- gestión de servicios
- gestión de testimonios
- exportación CSV
- repo GitHub limpio
- README profesional
- screenshots
- presentación corta para Workana

Descripción para portafolio:

> BrandLaunch es una landing page profesional con panel administrativo para negocios que necesitan captar clientes, mostrar servicios y gestionar contactos. Incluye formulario funcional, gestión de leads, servicios editables, testimonios, dashboard y exportación a CSV.

---

## Diferencia con QuoteFlow

QuoteFlow vende:

> “Puedo crear sistemas internos y documentos comerciales.”

BrandLaunch vende:

> “Puedo crear presencia online profesional y herramientas para captar clientes.”

Juntos demuestran:
- frontend visual
- backend funcional
- base de datos
- lógica de negocio
- orientación comercial
- capacidad de entregar productos reales

---

Este proyecto tiene que ser el más visual. Si QuoteFlow demuestra lógica, **BrandLaunch demuestra impacto comercial inmediato**.

---

## Orden de implementación obligatorio

Construir en este orden. BrandLaunch debe vender visualmente, pero no se debe sacrificar funcionalidad básica.

1. **Estructura base del proyecto**
   - `app.py`
   - `requirements.txt`
   - carpetas `templates/`, `static/`, `database/`, `docs/`
   - layout base para landing
   - layout base para admin

2. **Base de datos**
   - crear `schema.sql`
   - tablas `leads`, `services`, `testimonials`, `site_settings`
   - función de inicialización de DB
   - seed con datos demo de Nova Studio Digital

3. **Landing pública premium**
   - hero
   - servicios
   - beneficios
   - cómo funciona / por qué elegirnos
   - testimonios demo
   - formulario de contacto
   - footer
   - responsive desde el inicio

4. **Captura de leads**
   - formulario funcional
   - guardar lead en SQLite
   - feedback visual al enviar
   - estado inicial `nuevo`

5. **Login simple de admin**
   - login demo suficiente para proteger panel
   - no sobreingenierizar autenticación

6. **Dashboard admin**
   - total de leads
   - leads nuevos
   - servicios activos
   - testimonios activos
   - últimos leads

7. **Gestión de leads**
   - listar leads
   - ver detalle
   - cambiar estado: nuevo/contactado/cerrado
   - exportar CSV

8. **Gestión de servicios y testimonios**
   - listar
   - crear
   - editar
   - activar/desactivar

9. **Edición básica de textos**
   - hero title
   - hero subtitle
   - WhatsApp
   - email
   - nombre del negocio

10. **Pulido final**
   - responsive fino
   - copywriting comercial
   - microinteracciones simples
   - README profesional
   - screenshots

---

## Reglas de implementación

- Construir primero una landing visualmente fuerte y funcional.
- Usar **Flask + SQLite + HTML/CSS/JS** salvo instrucción explícita en contra.
- Mantener arquitectura simple y fácil de explicar.
- Separar responsabilidades:
  - rutas/controladores en `app.py` o módulos claros si el proyecto crece
  - landing/admin templates en `templates/`
  - estilos en `static/css/`
  - JavaScript en `static/js/`
  - schema en `database/schema.sql`
- Usar datos demo únicamente y marcarlo como demo en README.
- Todo texto visible debe sonar como una marca real, no como placeholder técnico.
- Priorizar conversión: CTA claro, beneficios claros, formulario visible.
- No usar Bootstrap genérico si hace que parezca plantilla barata.
- No sobreingenierizar autenticación, roles, multiusuario, pagos o CMS avanzado en MVP.
- Actualizar `README.md` cuando cambie setup, features o flujo de uso.
- Mantener el proyecto fácil de correr localmente.
- Evitar código confuso: nombres claros para rutas, funciones y variables.

---

## Definition of Done

Una feature se considera terminada solo si cumple:

- funciona de punta a punta
- guarda o muestra datos correctamente si aplica
- tiene validaciones mínimas
- se ve bien en desktop y mobile
- mantiene estética premium
- usa copy orientado a cliente
- no rompe otros flujos
- refuerza el objetivo Workana del proyecto
- está documentada en README si cambia el flujo principal

El proyecto completo se considera listo para portafolio cuando tenga:

- landing pública premium
- formulario funcional conectado a DB
- panel admin funcional
- gestión de leads
- gestión de servicios
- gestión de testimonios
- exportación CSV
- datos demo realistas
- README orientado a cliente
- screenshots en `docs/screenshots/`
- repo limpio sin archivos temporales ni secretos

---

## No hacer

- No hacer una landing genérica que parezca plantilla gratuita.
- No usar colores, textos o layouts infantiles.
- No hacer solo frontend sin backend funcional.
- No usar testimonios demo como si fueran reales.
- No afirmar que el proyecto fue contratado por una empresa real si es demo.
- No agregar pagos, roles complejos, CMS avanzado o integraciones externas antes del MVP.
- No sacrificar claridad por “efectos bonitos”.

---

## Criterio principal

Cada decisión debe responder:

> “¿Esto hace que BrandLaunch parezca una solución profesional que ayuda a un negocio a captar clientes?”

Si la respuesta es no, simplificar o eliminar.
