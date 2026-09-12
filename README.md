# 🌱 PastureRestore

Mini proyecto desarrollado por el equipo como parte de la preparación para el **NASA Space Apps Challenge 2026**.

## 📌 Descripción

**PastureRestore** es una aplicación experimental orientada al análisis y monitoreo de la recuperación de pasturas degradadas.

El objetivo del mini proyecto es que el equipo pueda llevar una idea desde el concepto hasta una **aplicación funcional**, utilizando datos y tecnologías relacionadas con la observación de la Tierra.

Este proyecto forma parte de la etapa de preparación del equipo y **no constituye la entrega oficial del NASA Space Apps Challenge 2026**.

---

## 🎯 Objetivo del mini proyecto

El objetivo principal es desarrollar un prototipo funcional que permita al equipo practicar:

* 🛰️ Uso de datos de observación de la Tierra.
* 🌱 Análisis de condiciones de pasturas.
* 📊 Procesamiento y visualización de datos.
* 💻 Desarrollo de una aplicación.
* 🤝 Trabajo colaborativo mediante GitHub.
* 🔄 Organización y control de versiones del código.

---

## 🚀 La aplicación

PastureRestore busca representar, de manera sencilla, cómo los datos obtenidos mediante observación satelital pueden utilizarse para analizar la evolución de una zona de pastura.

El prototipo podrá incorporar:

* 🗺️ Visualización geográfica.
* 🌿 Indicadores de vegetación.
* 📈 Evolución temporal.
* 🛰️ Datos provenientes de fuentes abiertas.
* 🔎 Comparación de diferentes períodos.
* 🌱 Seguimiento de la recuperación.

Las funcionalidades se irán incorporando durante el desarrollo del mini proyecto.

---

## 🧩 Arquitectura

La arquitectura inicial del proyecto será definida durante el desarrollo.

```text
       🛰️ Datos satelitales
              │
              ▼
       📥 Obtención de datos
              │
              ▼
       ⚙️ Procesamiento
              │
              ▼
       📊 Indicadores
              │
              ▼
       🗺️ Visualización
              │
              ▼
        🌱 PastureRestore
```

---

## 🛠️ Tecnologías

Para este mini proyecto se optó por mantener la parte técnica lo más simple posible, ya que el foco es practicar la dinámica de trabajo en equipo y no la complejidad del código:

* HTML / CSS / JavaScript plano (sin frameworks ni build tools)
* Git / GitHub para control de versiones y trabajo colaborativo
* Contenido generado con asistencia de IA a partir de las decisiones del equipo

Si el proyecto lo requiere más adelante, se podrán sumar herramientas de análisis geoespacial o datos abiertos de NASA.

---

## 📁 Estructura del repositorio

Esta es la estructura real y actual del repositorio (se irá actualizando a medida que se agreguen archivos):

```text
PastureRestore/
│
├── README.md          → este archivo
└── index.html         → pantalla principal de la app (mobile-first)
```

A medida que el equipo sume pantallas nuevas, se van a ir agregando como archivos `.html` adicionales (o carpetas, si hace falta ordenar más) siguiendo el mismo estilo visual definido en `index.html`.

---

## 🔄 Flujo de trabajo con Git

Para practicar el trabajo colaborativo, el equipo sigue siempre el mismo circuito para subir cualquier cambio:

1. **Actualizar `main`** antes de empezar: `git pull origin main` (o "Pull" desde VS Code), para no perder cambios de otros compañeros.
2. **Crear una rama propia** para el cambio que se va a hacer, por ejemplo `feature/pantalla-mapa`. Nunca se trabaja directo sobre `main`.
3. **Hacer los cambios** (agregar o editar archivos).
4. **Commit**: guardar los cambios con un mensaje corto que explique qué se hizo (ej: `"Agregar pantalla de mapa"`).
5. **Push**: subir la rama a GitHub.
6. **Abrir un Pull Request** desde GitHub, describiendo brevemente el cambio.
7. **Esperar revisión** de otro integrante del equipo antes de aprobar (o revisarlo uno mismo si el equipo decide que alcanza con eso para este mini proyecto).
8. **Merge** del Pull Request a `main`, y borrar la rama una vez mezclada.
9. **Actualizar la copia local**: volver a `main` y hacer `git pull` para tener el último estado del proyecto.

Este es el mismo circuito para cualquier cambio, sea una pantalla nueva, una corrección, o un ajuste de estilos.

---

## 👥 Equipo

Proyecto desarrollado por el equipo de preparación para **NASA Space Apps Challenge 2026**.

* Daniel
* Emmanuel
* Marcelo
* Hernán
* Leandro
* Alfredo

---

## 📅 Estado del proyecto

**🟡 En desarrollo**

Este repositorio se utilizará para:

* Centralizar el código.
* Registrar avances.
* Trabajar de manera colaborativa.
* Practicar Git y GitHub.
* Documentar decisiones técnicas.
* Construir y probar el prototipo.

---

## 🎓 Propósito

PastureRestore es principalmente un **proyecto de aprendizaje y experimentación**.

La finalidad es que el equipo pueda experimentar el ciclo completo:

**Idea → Diseño → Desarrollo → Prueba → Mejora**

y utilizar lo aprendido como experiencia para el proyecto que posteriormente se desarrolle para el **NASA Space Apps Challenge 2026**.

---

## 🌱 PastureRestore

**Un pequeño proyecto para aprender haciendo.**
