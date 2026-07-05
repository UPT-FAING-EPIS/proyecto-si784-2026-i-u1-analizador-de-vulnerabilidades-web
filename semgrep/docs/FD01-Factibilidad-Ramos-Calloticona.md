<center>

![Logo UPT](media/logo-upt.png)

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERÍA**

**Escuela Profesional de Ingeniería de Sistemas**

**Proyecto: Analizador de Vulnerabilidades Web — VulnScan Pro**

Curso: *Calidad y Pruebas de Software*

Docente: *Ing. Patrick Jose Cuadros Quiroga*

Integrantes:

**Ramos Loza, Mariela Estefany (2023077478)**

**Calloticona Chambilla, Marymar D. (2023076791)**

**Tacna – Perú**

**2026**

</center>

<div style="page-break-after: always;"></div>

---

**Sistema: Analizador de Vulnerabilidades Web — VulnScan Pro**

**Informe de Factibilidad**

Versión 1.1

| CONTROL DE VERSIONES | | | | | |
|:---:|:---|:---|:---|:---|:---|
| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
| 1.0 | M. Calloticona | M. Ramos | | 28/03/2026 | Versión Original |
| 1.1 | M. Ramos | M. Calloticona | | 04/04/2026 | Actualización stack y análisis financiero |

<div style="page-break-after: always;"></div>

---

## ÍNDICE GENERAL

[1. Descripción del Proyecto](#1-descripción-del-proyecto)

[2. Riesgos](#2-riesgos)

[3. Análisis de la Situación Actual](#3-análisis-de-la-situación-actual)

[4. Estudio de Factibilidad](#4-estudio-de-factibilidad)

&nbsp;&nbsp;&nbsp;&nbsp;[4.1. Factibilidad Técnica](#41-factibilidad-técnica)

&nbsp;&nbsp;&nbsp;&nbsp;[4.2. Factibilidad Económica](#42-factibilidad-económica)

&nbsp;&nbsp;&nbsp;&nbsp;[4.3. Factibilidad Operativa](#43-factibilidad-operativa)

&nbsp;&nbsp;&nbsp;&nbsp;[4.4. Factibilidad Legal](#44-factibilidad-legal)

&nbsp;&nbsp;&nbsp;&nbsp;[4.5. Factibilidad Social](#45-factibilidad-social)

&nbsp;&nbsp;&nbsp;&nbsp;[4.6. Factibilidad Ambiental](#46-factibilidad-ambiental)

[5. Análisis Financiero](#5-análisis-financiero)

[6. Conclusiones](#6-conclusiones)

<div style="page-break-after: always;"></div>

---

## Informe de Factibilidad

---

## 1. Descripción del Proyecto

### 1.1. Nombre del Proyecto

**Analizador de Vulnerabilidades Web — VulnScan Pro**

### 1.2. Duración del Proyecto

- **Tiempo total:** 4 semanas (1 mes) — Marzo a Abril 2026

| **Fase** | **Duración** | **Actividades Clave** |
|:---------|:------------|:----------------------|
| Fase 1: Arquitectura y Setup | Semana 1 | Definición de arquitectura, configuración VPS (149.34.48.176), MySQL, FastAPI, Next.js, estructura de carpetas y control de versiones. |
| Fase 2: Backend y Motor de Escaneo | Semana 2 | Implementación de los 13 módulos OWASP Top 10: XSS, SQLi, CSRF, SSRF, LFI, Command Injection, Open Redirect, Headers, SSL, Archivos Sensibles, HTTP Methods, Error Disclosure, Crawling. API REST con JWT. |
| Fase 3: Frontend y Dashboard SOC | Semana 3 | Dashboard con gráficos Chart.js, escáner interactivo con polling en tiempo real, panel de administración, autenticación con roles. |
| Fase 4: IA, Reportes y Despliegue | Semana 4 | Integración DeepSeek AI, generación PDF/HTML/JSON, script deploy.sh, Nginx, systemd, PM2, UFW. Pruebas finales. |

### 1.3. Descripción

**VulnScan Pro** es una plataforma web profesional de análisis dinámico de seguridad (DAST) desarrollada en el curso de Calidad y Pruebas de Software de la Escuela Profesional de Ingeniería de Sistemas de la Universidad Privada de Tacna.

El sistema permite a ingenieros de QA, desarrolladores y auditores identificar vulnerabilidades web de forma automatizada antes del despliegue a producción. Integra inteligencia artificial (DeepSeek AI) para analizar cada vulnerabilidad detectada, generar escenarios de ataque realistas, proporcionar código de remediación específico por stack tecnológico y producir reportes ejecutivos con puntuación de riesgo.

La importancia del proyecto radica en que las aplicaciones web desarrolladas en entornos académicos y PYMES de la región Tacna se despliegan frecuentemente sin ninguna verificación de seguridad, exponiéndose a ataques automatizados. VulnScan Pro actúa como esa capa de verificación, ofreciendo capacidades equivalentes a herramientas comerciales (Burp Suite, Nessus) de forma gratuita y accesible.

**Stack tecnológico:** Backend FastAPI + Python + MySQL 8.0 + SQLAlchemy. Frontend Next.js 16 + TypeScript + TailwindCSS. IA: DeepSeek API. Infraestructura: VPS Linux 149.34.48.176, Nginx + systemd + PM2 + UFW.

### 1.4. Objetivos

#### 1.4.1. Objetivo General

Desarrollar una plataforma web integral de análisis de vulnerabilidades de seguridad que permita a equipos de desarrollo e ingeniería de calidad identificar, priorizar y remediar brechas de seguridad en aplicaciones web mediante un motor de escaneo OWASP Top 10 potenciado por inteligencia artificial, desplegado en infraestructura VPS Linux de producción.

#### 1.4.2. Objetivos Específicos

1. **Implementar un motor de escaneo multimódulo** capaz de detectar las 13 categorías de vulnerabilidades más críticas del OWASP Top 10: SQL Injection (error-based y blind), XSS reflejado, CSRF, SSRF, LFI/Path Traversal, Command Injection, Open Redirect, cabeceras HTTP inseguras, SSL/TLS deficiente, archivos sensibles expuestos, métodos HTTP peligrosos y divulgación de errores.

2. **Desarrollar un sistema de autenticación robusto** con roles Admin/Analista/Usuario, protección anti-fuerza bruta (bloqueo automático tras 5 intentos fallidos por 15 minutos), sesiones JWT con JTI único, registro de auditoría completo y gestión de usuarios desde panel administrativo.

3. **Integrar DeepSeek AI** para análisis automático por vulnerabilidad: puntuación CVSS (0-10), identificador CWE, escenario de ataque, código de remediación adaptado al stack tecnológico del objetivo y reporte ejecutivo de riesgo global con risk score (0-100).

4. **Construir un dashboard SOC** (Security Operations Center) en Next.js 16 con estadísticas en tiempo real, gráficos interactivos (Chart.js), escáner con configuración avanzada (profundidad, timeout, stack, IA), polling automático del estado del escaneo y panel de administración.

5. **Desplegar el sistema en producción** sobre VPS Linux (149.34.48.176) con Nginx como proxy reverso, systemd para el backend (Gunicorn 4 workers), PM2 para el frontend, UFW firewall y MySQL 8.0 nativo, mediante un script `deploy.sh` que automatiza toda la instalación en un solo comando.

<div style="page-break-after: always;"></div>

---

## 2. Riesgos

Los siguientes riesgos podrían afectar el éxito del proyecto:

| **#** | **Riesgo** | **Probabilidad** | **Impacto** | **Plan de Mitigación** |
|:------|:-----------|:----------------:|:-----------:|:-----------------------|
| R-01 | Bloqueo de IPs por servidores objetivo durante el escaneo | Media | Alto | Timeouts configurables por módulo (5-60 s), límite de peticiones simultáneas, User-Agent estándar. |
| R-02 | Falsos positivos en detección de vulnerabilidades | Alta | Medio | Validación con múltiples payloads por módulo; análisis IA como segunda capa de verificación con indicador de probabilidad de falso positivo (0-100%). |
| R-03 | Uso indebido sobre sistemas sin autorización | Baja | Crítico | Aviso legal obligatorio en la interfaz; disclaimer de responsabilidad en los términos de uso; documentación ética en el repositorio. |
| R-04 | Fallo o indisponibilidad de la API DeepSeek | Media | Medio | Fallback local para SQLi (CWE-89), XSS (CWE-79) y CSRF (CWE-352) implementado. Sistema funcional sin IA. |
| R-05 | Caída del VPS durante escaneos activos | Baja | Alto | systemd con `Restart=always` y `RestartSec=5`; MySQL con `pool_pre_ping=True`; health check en `/health`. |
| R-06 | Consumo excesivo de recursos durante escaneos paralelos | Media | Medio | Límite de 4 workers Gunicorn; timeout por módulo; un escaneo a la vez por usuario desde el frontend. |
| R-07 | Exposición de credenciales en el repositorio | Baja | Crítico | Variables en `.env` con `.gitignore`; `SECRET_KEY` generada con `openssl rand -hex 32` en deploy.sh. |
| R-08 | Incompatibilidad de versiones en el VPS de producción | Media | Medio | Script `deploy.sh` instala versiones específicas (Python 3.11, Node.js 20, MySQL 8.0, Nginx 1.24). |
| R-09 | Curva de aprendizaje del equipo con el stack tecnológico | Media | Bajo | Stack basado en Python y TypeScript, lenguajes conocidos. FastAPI y Next.js tienen documentación extensa. |

<div style="page-break-after: always;"></div>

---

## 3. Análisis de la Situación Actual

### 3.1. Planteamiento del Problema

En la actualidad, las aplicaciones web desarrolladas en entornos académicos y por PYMES de la región Tacna suelen desplegarse con configuraciones de seguridad deficientes: cabeceras HTTP ausentes, certificados SSL vencidos, formularios vulnerables a inyección SQL, cookies sin flags de protección y archivos de configuración sensibles expuestos públicamente (`.env`, `.git`, `phpinfo.php`).

La causa principal es la falta de herramientas de auditoría de seguridad accesibles. Las soluciones profesionales existentes (Burp Suite Professional: USD 449/año; Nessus: USD 3,590/año; Acunetix: USD 4,500/año) tienen costos que las hacen inaccesibles para estudiantes, desarrolladores independientes y pequeñas empresas locales.

Esta situación expone los datos de ciudadanos, estudiantes y organizaciones a ataques automatizados crecientes. Según el OWASP Top 10:2021, más del 94% de las aplicaciones web presentan al menos una vulnerabilidad de la lista, siendo SQL Injection, XSS y cabeceras inseguras las más prevalentes.

**VulnScan Pro** resuelve este problema ofreciendo capacidades DAST equivalentes a herramientas comerciales de forma gratuita, con resultados en español, análisis de IA contextualizado y reportes exportables para auditoría formal.

### 3.2. Consideraciones de Hardware y Software

#### Hardware disponible y requerido

| **Componente** | **Especificación** | **Propósito** | **Estado** |
|:---------------|:-------------------|:-------------|:-----------|
| Laptop de desarrollo (×2) | Intel i5/i7 11ª gen, 16 GB RAM, SSD 512 GB | Desarrollo, pruebas locales | Disponible |
| VPS de producción | IP: 149.34.48.176, 2 vCPU, 4 GB RAM, 50 GB SSD, Ubuntu 22.04 LTS | Despliegue en producción | Activo y contratado |
| Monitor externo (×2) | 24" Full HD | Productividad del equipo | Disponible |

#### Stack tecnológico completo

| **Tecnología** | **Versión** | **Propósito** | **Licencia** | **Costo** |
|:---------------|:------------|:-------------|:------------|:---------:|
| Python | 3.11+ | Lenguaje principal del backend | PSF | S/. 0.00 |
| FastAPI | 0.110+ | Framework REST asíncrono con validación Pydantic | MIT | S/. 0.00 |
| SQLAlchemy | 2.0 | ORM para MySQL con QueuePool | MIT | S/. 0.00 |
| PyMySQL | 1.1+ | Driver MySQL para Python | MIT | S/. 0.00 |
| Gunicorn + Uvicorn | Latest | Servidor ASGI para producción | MIT | S/. 0.00 |
| python-jose | 3.x | Generación y validación JWT (HS256) | MIT | S/. 0.00 |
| bcrypt / passlib | Latest | Hash seguro de contraseñas (cost=10) | Apache 2.0 | S/. 0.00 |
| slowapi | Latest | Rate limiting para FastAPI | MIT | S/. 0.00 |
| requests | 2.31+ | Cliente HTTP para el motor de escaneo | Apache 2.0 | S/. 0.00 |
| BeautifulSoup4 | 4.12 | Parser HTML para web crawling | MIT | S/. 0.00 |
| WeasyPrint | Latest | Generación de reportes PDF | BSD | S/. 0.00 |
| python-dotenv | Latest | Gestión de variables de entorno | BSD | S/. 0.00 |
| MySQL | 8.0 | Base de datos relacional de producción | GPL v2 | S/. 0.00 |
| Next.js | 16 (App Router) | Framework React con SSR y routing | MIT | S/. 0.00 |
| TypeScript | 5.x | Tipado estático para JavaScript | Apache 2.0 | S/. 0.00 |
| TailwindCSS | 3.x | Framework CSS utilitario | MIT | S/. 0.00 |
| Chart.js + react-chartjs-2 | 4.x | Gráficos interactivos (dona, línea) | MIT | S/. 0.00 |
| lucide-react | Latest | Iconos SVG para la interfaz | ISC | S/. 0.00 |
| DeepSeek AI API | deepseek-chat | Análisis IA de vulnerabilidades | Comercial (free tier) | S/. 0.00* |
| Nginx | 1.24 | Proxy reverso, rate limiting, SSL | BSD | S/. 0.00 |
| PM2 | Latest | Process manager Node.js | AGPL | S/. 0.00 |
| UFW | Latest | Firewall Linux (Ubuntu) | GPL | S/. 0.00 |
| Git / GitHub | 2.x / Free | Control de versiones | MIT / Free | S/. 0.00 |
| VS Code + extensiones | Latest | IDE principal del equipo | Gratuito | S/. 0.00 |

*DeepSeek AI otorga créditos iniciales gratuitos para uso académico.

<div style="page-break-after: always;"></div>

---

## 4. Estudio de Factibilidad

Los resultados indican que el proyecto es viable en todas sus dimensiones. La evaluación fue realizada por el equipo de desarrollo durante la Fase 1 del proyecto.

### 4.1. Factibilidad Técnica

El proyecto es **técnicamente factible**. El equipo cuenta con los conocimientos requeridos en desarrollo web fullstack (Python, TypeScript, SQL) y el stack seleccionado está completamente basado en tecnologías maduras, open source y con amplia documentación.

| **Criterio de evaluación** | **Puntuación (1-5)** | **Justificación** |
|:---------------------------|:--------------------:|:------------------|
| Disponibilidad de tecnologías | 5 | Python, FastAPI, Next.js, MySQL son tecnologías estables, gratuitas y con miles de proyectos en producción. |
| Conocimiento del equipo | 4 | Dominio intermedio-avanzado en Python y JavaScript/TypeScript. Experiencia en bases de datos relacionales. |
| Escalabilidad de la arquitectura | 5 | Arquitectura desacoplada: nuevos módulos de escaneo = una función nueva en `scanner.py`. Sin refactorización mayor. |
| Infraestructura disponible | 5 | VPS Linux ya contratado y activo (149.34.48.176). Acceso root. Conectividad permanente. |
| Compatibilidad tecnológica | 5 | Todo el stack es compatible entre sí y con Ubuntu 22.04 LTS del VPS. |
| Seguridad del sistema | 5 | JWT + bcrypt + rate limiting + headers de seguridad + audit logs + variables de entorno. |
| **Promedio** | **4.83/5** | **Alta factibilidad técnica** |

**Medidas de seguridad implementadas en el sistema:**
- Validación de entradas con Pydantic en todos los endpoints.
- Timeouts configurables (5, 10, 30, 60 s) para evitar DoS accidental sobre objetivos.
- Rate limiting en Nginx (3 zonas) y en la API (slowapi).
- Autenticación JWT con JTI único, expiración 24h, tabla de sesiones activas para revocación remota.
- Variables sensibles en `.env` excluidas del repositorio con `.gitignore`.
- Headers de seguridad HTTP aplicados globalmente por middleware FastAPI.
- Servicio systemd con `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict`.

### 4.2. Factibilidad Económica

El proyecto es **económicamente factible**. El modelo de desarrollo es open source con costo de licenciamiento cero. Los únicos costos reales son operativos del equipo durante las 4 semanas de ejecución.

#### 4.2.1. Costos Generales

| **Ítem** | **Cant.** | **Costo Unit. (S/.)** | **Total (S/.)** |
|:---------|:---------:|:---------------------:|:---------------:|
| Papel e impresión de documentación académica | 1 resma | S/. 15.00 | S/. 15.00 |
| Útiles de escritorio (lapiceros, folder, etc.) | Global | S/. 10.00 | S/. 10.00 |
| Cuota de acceso internet adicional (datos móviles pruebas) | 1 mes | S/. 20.00 | S/. 20.00 |
| **Total Costos Generales** | | | **S/. 45.00** |

#### 4.2.2. Costos Operativos durante el Desarrollo

| **Ítem** | **Cant. (mes)** | **Costo Unit. (S/.)** | **Total (S/.)** |
|:---------|:---------------:|:---------------------:|:---------------:|
| Energía eléctrica (2 laptops + monitores, ~4 h/día) | 1 | S/. 38.00 | S/. 38.00 |
| Servicio de internet (fibra óptica 200 Mbps) | 1 | S/. 40.00 | S/. 40.00 |
| Alquiler de VPS (Ubuntu 22.04, 2 vCPU, 4 GB RAM) | 1 | S/. 18.00 | S/. 18.00 |
| **Total Costos Operativos** | | | **S/. 96.00** |

#### 4.2.3. Costos del Ambiente (Software y Licencias)

| **Software / Servicio** | **Proveedor** | **Tipo de Licencia** | **Costo (S/.)** |
|:------------------------|:-------------|:---------------------|:---------------:|
| Python 3.11 + FastAPI + todas las librerías | Comunidad open source | MIT / Apache 2.0 / PSF | S/. 0.00 |
| Next.js 16 + TypeScript + TailwindCSS | Vercel / Microsoft / Tailwind Labs | MIT | S/. 0.00 |
| MySQL 8.0 | Oracle | GPL v2 (uso libre) | S/. 0.00 |
| DeepSeek AI API (créditos académicos) | DeepSeek | Free tier | S/. 0.00 |
| VS Code + extensiones Python/TypeScript | Microsoft | Gratuita | S/. 0.00 |
| GitHub (repositorio privado/público) | GitHub | Plan Free | S/. 0.00 |
| Nginx + PM2 + UFW | Open source | BSD / AGPL / GPL | S/. 0.00 |
| **Total Costos de Ambiente** | | | **S/. 0.00** |

#### 4.2.4. Costos de Personal

| **Rol** | **Integrante** | **Horas totales** | **Valor hora (S/.)** | **Total referencial (S/.)** |
|:--------|:--------------|:-----------------:|:--------------------:|:---------------------------:|
| Backend Developer / Scrum Master | Calloticona Chambilla, Marymar D. | 80 h | S/. 15.00 | S/. 1,200.00 |
| Frontend Developer / QA Engineer | Ramos Loza, Mariela Estefany | 80 h | S/. 15.00 | S/. 1,200.00 |
| **Total Personal (referencial — no erogado)** | | **160 h** | | **S/. 2,400.00** |

*Como proyecto académico, el costo de personal no representa una erogación monetaria real.*

#### 4.2.5. Costos Totales del Desarrollo del Sistema

| **Categoría** | **Monto Efectivo (S/.)** | **Monto Referencial (S/.)** |
|:--------------|:------------------------:|:---------------------------:|
| Costos Generales | S/. 45.00 | S/. 45.00 |
| Costos Operativos (1 mes) | S/. 96.00 | S/. 96.00 |
| Costos de Software y Licencias | S/. 0.00 | S/. 0.00 |
| Personal (referencial — no erogado) | S/. 0.00 | S/. 2,400.00 |
| Imprevistos (5%) | S/. 7.05 | S/. 127.05 |
| **INVERSIÓN TOTAL** | **S/. 148.05** | **S/. 2,668.05** |

### 4.3. Factibilidad Operativa

El sistema es **operativamente factible**. Los beneficios directos por stakeholder son:

| **Stakeholder** | **Beneficio operativo** |
|:----------------|:------------------------|
| Docente del curso | Herramienta de evaluación práctica para que los estudiantes demuestren comprensión de seguridad web OWASP. |
| Estudiantes EPIS (UPT) | Herramienta gratuita para auditar sus propios proyectos antes de entregarlos o desplegarlos. |
| Ingenieros de QA | Automatización de pruebas de seguridad antes de cada ciclo de despliegue. |
| PYMES de Tacna | Diagnóstico de seguridad web sin costo de licenciamiento ni instalación local. |
| Auditores de TI | Reportes PDF/HTML/JSON exportables para procesos de auditoría formal. |

**Capacidad operativa del sistema:** El sistema está diseñado para operar de forma autónoma con reinicio automático ante fallos (systemd). No requiere administración diaria una vez desplegado. La adición de nuevos módulos de escaneo no requiere interrumpir el servicio.

**Interesados del proyecto:**

| **Interesado** | **Rol** | **Nivel de involucramiento** |
|:---------------|:--------|:---------------------------:|
| Ing. Patrick Jose Cuadros Quiroga | Docente supervisor | Alto |
| Calloticona Chambilla, Marymar D. | Desarrolladora backend | Alto |
| Ramos Loza, Mariela Estefany | Desarrolladora frontend / QA | Alto |
| Estudiantes EPIS (UPT) | Usuarios finales académicos | Medio |
| PYMES y desarrolladores de Tacna | Beneficiarios externos | Bajo |

### 4.4. Factibilidad Legal

El desarrollo y distribución de VulnScan Pro se rige bajo un marco de estricta legalidad:

- **Ley N° 30096 — Ley de Delitos Informáticos (Perú):** La plataforma incluye un aviso legal obligatorio que el usuario acepta antes de iniciar cualquier escaneo, declarando poseer autorización expresa sobre la aplicación objetivo. El sistema no ejecuta ataques destructivos. Evita la figura de "Acceso Ilícito" del Art. 2.
- **Ley N° 29733 — Ley de Protección de Datos Personales (Perú):** El sistema no recolecta datos personales de terceros. Los resultados de escaneos están vinculados al usuario autenticado que los generó. No se comparte información con terceros.
- **Licenciamiento MIT:** El código fuente es transparente y auditable. No contiene funciones ocultas de espionaje, robo de datos ni ataques encubiertos.
- **Disclaimer legal:** Los términos de uso especifican que los autores no se responsabilizan por el uso indebido del software sobre sistemas sin autorización expresa del propietario.
- **OWASP Legal Notice:** El sistema implementa pruebas no intrusivas alineadas con las guías éticas de OWASP para herramientas de seguridad.

### 4.5. Factibilidad Social

VulnScan Pro genera impacto social positivo en la región Tacna:

- **Democratización de la ciberseguridad:** Permite a estudiantes, desarrolladores independientes y PYMES acceder a diagnósticos de seguridad equivalentes a herramientas de nivel empresarial (USD 449-4,500/año) de forma gratuita.
- **Formación en cultura de hacking ético:** Desarrollado en el entorno académico de la UPT, promueve el uso responsable y preventivo de herramientas de seguridad, educando a la próxima generación de ingenieros en prácticas de desarrollo seguro (Security by Design).
- **Protección del ciudadano digital:** Al elevar la seguridad de aplicaciones locales, se protege indirectamente la información personal (nombres, correos, datos de transacciones) de ciudadanos de Tacna que consumen servicios digitales de pequeñas empresas.
- **Reducción de la brecha digital en seguridad:** Contribuye a cerrar la brecha entre la capacidad de defensa digital de grandes corporaciones y la de organizaciones locales.

### 4.6. Factibilidad Ambiental

El proyecto se alinea con los principios de **Green IT (Tecnologías Verdes)**:

- **Eficiencia computacional:** FastAPI es uno de los frameworks Python más eficientes en CPU/memoria por petición (comparable con Node.js Express), reduciendo el consumo energético del servidor.
- **Optimización del frontend:** Next.js aplica code splitting automático, lazy loading y compresión de assets, reduciendo el tráfico de datos y el consumo en el dispositivo del usuario final.
- **Cero residuos físicos:** Distribución 100% digital mediante GitHub. No se requieren medios físicos, impresiones masivas ni infraestructura adicional.
- **Infraestructura compartida:** El VPS aloja múltiples proyectos, optimizando el uso de recursos físicos. Los centros de datos modernos operan con energías renovables en porcentajes crecientes.
- **Sin dependencias de hardware especializado:** No requiere servidores dedicados, HSMs ni dispositivos de seguridad adicionales. Funciona en un VPS estándar de S/. 18.00/mes.

<div style="page-break-after: always;"></div>

---

## 5. Análisis Financiero

El plan financiero evalúa los ingresos y gastos asociados al proyecto desde el punto de vista temporal, con el objetivo de validar la viabilidad financiera de la inversión.

### 5.1. Justificación de la Inversión

La inversión efectiva de **S/. 148.05** se justifica ampliamente por los beneficios generados.

#### 5.1.1. Beneficios del Proyecto

**Beneficios tangibles (cuantificables):**

| **Beneficio** | **Valor estimado anual (S/.)** |
|:--------------|:------------------------------:|
| Ahorro en licencias de herramientas equivalentes (Burp Suite: USD 449 ≈ S/. 1,706/año) | S/. 1,706.00 |
| Reducción de tiempo en detección de vulnerabilidades (de 2 días a 5 minutos → 4 h/semana × S/. 15/h × 50 semanas) | S/. 3,000.00 |
| Prevención de incidentes de seguridad en proyectos académicos (costo estimado de un incidente: S/. 500) | S/. 500.00 |
| **Total beneficios tangibles anuales** | **S/. 5,206.00** |

**Beneficios intangibles (no cuantificables directamente):**
- Elevación del estándar de calidad de software en la EPIS — UPT.
- Formación práctica en ciberseguridad del equipo de desarrollo.
- Mejora en la reputación del proyecto ante el mercado laboral.
- Contribución al ecosistema de seguridad digital de la región Tacna.
- Disponibilidad de una herramienta open source replicable por otros grupos de la universidad.

#### 5.1.2. Criterios de Inversión

**5.1.2.1. Relación Beneficio/Costo (B/C)**

```
B/C = Beneficios Totales Anuales / Inversión Total Efectiva
B/C = S/. 5,206.00 / S/. 148.05
B/C = 35.2
```

> B/C = 35.2 > 1 → **Se acepta el proyecto.** Por cada sol invertido, se generan S/. 35.20 en beneficios.

**5.1.2.2. Valor Actual Neto (VAN)**

Considerando: vida útil = 3 años, tasa de descuento (COK) = 12% anual, beneficio neto anual = S/. 5,206.00.

```
VAN = -148.05 + (5,206 / 1.12¹) + (5,206 / 1.12²) + (5,206 / 1.12³)
VAN = -148.05 + 4,648.21 + 4,150.19 + 3,705.53
VAN = S/. 12,355.88
```

> VAN = S/. 12,355.88 > 0 → **Se acepta el proyecto.**

**5.1.2.3. Tasa Interna de Retorno (TIR)**

Dado el bajo costo de inversión (S/. 148.05) y los beneficios anuales de S/. 5,206.00, la TIR supera el **3,400%**, muy superior al COK del 12%.

> TIR >> COK (12%) → **Se acepta el proyecto.** La inversión es altamente rentable.

<div style="page-break-after: always;"></div>

---

## 6. Conclusiones

1. El proyecto **VulnScan Pro — Analizador de Vulnerabilidades Web** es **altamente factible** desde todas las dimensiones analizadas: técnica (4.83/5), económica (costo cero en licencias), operativa (beneficios directos para todos los stakeholders), legal (cumplimiento Ley 30096 y 29733), social (democratización de la ciberseguridad) y ambiental (Green IT).

2. El stack tecnológico elegido (FastAPI + MySQL + Next.js + DeepSeek AI) ofrece el mejor equilibrio entre rendimiento, facilidad de mantenimiento, costo cero en licencias y alineación con las tendencias actuales del mercado de desarrollo web seguro.

3. Los indicadores financieros son excepcionales: **B/C = 35.2**, **VAN = S/. 12,355.88** (positivo), **TIR >> 3,400%**. La inversión efectiva de S/. 148.05 genera retornos que justifican ampliamente el desarrollo del sistema.

4. La integración de DeepSeek AI diferencia a VulnScan Pro de herramientas académicas convencionales, proporcionando análisis contextualizado con código de remediación específico por stack tecnológico, lo que incrementa significativamente la utilidad práctica del sistema.

5. El proyecto cumple estrictamente con el marco legal peruano, adopta un enfoque ético de hacking defensivo y cuenta con mecanismos que previenen activamente el uso indebido de la plataforma.

---

*Documento elaborado por: Calloticona Chambilla, Marymar D. y Ramos Loza, Mariela Estefany*
*Curso: Calidad y Pruebas de Software — Docente: Ing. Patrick Jose Cuadros Quiroga — UPT — 2026*
