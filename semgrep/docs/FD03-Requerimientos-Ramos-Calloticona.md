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

**Documento de Especificación de Requerimientos de Software**

Versión 1.1

| CONTROL DE VERSIONES | | | | | |
|:---:|:---|:---|:---|:---|:---|
| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
| 1.0 | M. Calloticona | M. Ramos | | 28/03/2026 | Versión Original |
| 1.1 | M. Ramos | M. Calloticona | | 04/04/2026 | Ampliación RF/RNF; modelos conceptual y lógico |

<div style="page-break-after: always;"></div>

---

## ÍNDICE GENERAL

[INTRODUCCION](#introduccion)

[I. Generalidades de la Empresa](#i-generalidades-de-la-empresa)

[II. Visionamiento de la Empresa](#ii-visionamiento-de-la-empresa)

[III. Análisis de Procesos](#iii-análisis-de-procesos)

[IV. Especificación de Requerimientos de Software](#iv-especificación-de-requerimientos-de-software)

[V. Fase de Desarrollo](#v-fase-de-desarrollo)

[CONCLUSIONES](#conclusiones)

[RECOMENDACIONES](#recomendaciones)

[BIBLIOGRAFÍA](#bibliografía)

[WEBGRAFÍA](#webgrafía)

<div style="page-break-after: always;"></div>

---

## INTRODUCCION

El presente documento constituye la Especificación de Requerimientos de Software (ERS) del sistema **VulnScan Pro — Analizador de Vulnerabilidades Web**, desarrollado como proyecto académico del curso de Calidad y Pruebas de Software de la Escuela Profesional de Ingeniería de Sistemas de la Universidad Privada de Tacna, bajo la supervisión del Ing. Patrick Jose Cuadros Quiroga.

El documento describe de forma detallada todos los requerimientos funcionales y no funcionales del sistema, los procesos actuales y propuestos, las reglas de negocio, los perfiles de usuario, y los modelos conceptual y lógico del sistema.

VulnScan Pro nace como respuesta a la necesidad de contar con una herramienta de análisis dinámico de seguridad de aplicaciones (DAST) que sea accesible, gratuita y con resultados en español para equipos académicos, desarrolladores independientes y PYMES de la región Tacna. El sistema implementa 13 módulos de detección de vulnerabilidades alineados con el OWASP Top 10:2021, potenciados por inteligencia artificial (DeepSeek AI), con generación de reportes exportables y un dashboard de operaciones de seguridad (SOC) en tiempo real.

El alcance de este documento abarca desde la descripción del contexto organizacional hasta la especificación técnica de los modelos UML de análisis y diseño. Sirve como referencia técnica para el equipo de desarrollo, el docente evaluador y cualquier usuario técnico que necesite comprender la estructura y comportamiento del sistema.

<div style="page-break-after: always;"></div>

---

## I. Generalidades de la Empresa

### 1. Nombre de la Empresa

**Universidad Privada de Tacna (UPT)**
*Escuela Profesional de Ingeniería de Sistemas — EPIS*
*Facultad de Ingeniería*

### 2. Visión

Ser una universidad de excelencia académica, líder en la formación de profesionales con valores éticos, capacidad de investigación y emprendimiento, comprometidos con el desarrollo sostenible de la región y el país, reconocida en el ámbito nacional e internacional.

### 3. Misión

Formar profesionales íntegros con sólidos conocimientos científicos y tecnológicos, capaces de contribuir al desarrollo de la sociedad a través de la investigación, la innovación y el servicio comunitario, bajo principios éticos y con responsabilidad social.

### 4. Organigrama

```
┌──────────────────────────────────────────────────────────────┐
│              RECTORADO — Universidad Privada de Tacna         │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│              VICERRECTORADO ACADÉMICO                         │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│              FACULTAD DE INGENIERÍA                           │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│    ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS (EPIS)       │
│                  Dirección de Escuela                         │
└──────┬─────────────────────────────────────────┬─────────────┘
       │                                         │
┌──────▼──────────────┐             ┌────────────▼─────────────┐
│  DOCENTES           │             │  ESTUDIANTES             │
│  Ing. Patrick       │             │  Calloticona M.          │
│  Cuadros Quiroga    │             │  Ramos M.                │
│  (Supervisor)       │             │  (Equipo Desarrollador)  │
└─────────────────────┘             └──────────────────────────┘
```

<div style="page-break-after: always;"></div>

---

## II. Visionamiento de la Empresa

### 1. Descripción del Problema

Las aplicaciones web desarrolladas en el ámbito académico de la EPIS-UPT y por PYMES de la región Tacna se despliegan habitualmente sin ningún proceso formal de verificación de seguridad. Esta realidad se debe a tres factores principales:

**Factor 1 — Costo prohibitivo de las herramientas profesionales:** Las soluciones DAST del mercado tienen precios anuales que van desde S/. 1,706 (Burp Suite Pro) hasta S/. 17,100 (Acunetix), completamente fuera del alcance de estudiantes universitarios y pequeñas empresas locales.

**Factor 2 — Barrera idiomática y de conocimiento:** La mayoría de herramientas disponibles gratuitas (OWASP ZAP, Nikto) están en inglés, generan resultados técnicos difíciles de interpretar para desarrolladores sin especialización en seguridad, y no ofrecen orientación de remediación contextualizada.

**Factor 3 — Ausencia de cultura de seguridad en el ciclo de desarrollo:** Los proyectos académicos y de PYMES locales rara vez incluyen pruebas de seguridad en sus fases de desarrollo. El criterio de "funcionalidad" predomina sobre el de "seguridad", resultando en aplicaciones con vulnerabilidades conocidas que se exponen directamente a internet.

**Consecuencias:** Aplicaciones en producción con vulnerabilidades críticas (SQL Injection, XSS, CSRF, archivos .env expuestos, cabeceras HTTP ausentes) que pueden ser explotadas por atacantes automatizados para robar datos de usuarios, comprometer servidores o dañar la reputación de las organizaciones.

### 2. Objetivos de Negocios

| **#** | **Objetivo de Negocio** | **Indicador de Éxito** |
|:-----:|:------------------------|:----------------------|
| OBJ-01 | Proporcionar una herramienta DAST gratuita y accesible para la comunidad académica de la EPIS-UPT | Sistema desplegado en producción y accesible para todos los estudiantes de la escuela |
| OBJ-02 | Reducir el tiempo de detección de vulnerabilidades web de días a minutos | Tiempo de escaneo completo < 10 minutos para sitios típicos |
| OBJ-03 | Elevar el estándar de calidad de los proyectos de software de la EPIS mediante la integración de pruebas de seguridad | Al menos el 50% de grupos del curso usen la herramienta para auditar sus proyectos |
| OBJ-04 | Democratizar el acceso al análisis de seguridad web en la región Tacna | Plataforma disponible públicamente para desarrolladores y PYMES locales |
| OBJ-05 | Desarrollar competencias técnicas del equipo en ciberseguridad, IA y desarrollo fullstack | Equipo con dominio del stack FastAPI + Next.js + DeepSeek AI + VPS Linux |

### 3. Objetivos de Diseño

| **#** | **Objetivo de Diseño** | **Criterio de Aceptación** |
|:-----:|:-----------------------|:--------------------------|
| ODI-01 | Arquitectura desacoplada de 3 capas (presentación, lógica de negocio, datos) | Backend FastAPI independiente del frontend Next.js; comunicación exclusivamente por API REST |
| ODI-02 | Motor de escaneo modular y extensible | Agregar un nuevo módulo de escaneo requiere solo una función en `scanner.py` sin modificar la arquitectura |
| ODI-03 | Interfaz intuitiva que permita a un usuario sin experiencia en seguridad realizar su primer escaneo en < 5 minutos | Prueba de usabilidad con 3 usuarios no técnicos |
| ODI-04 | Sistema seguro que proteja la información de los escaneos | JWT + bcrypt + rate limiting + headers de seguridad + audit logs |
| ODI-05 | Despliegue reproducible en cualquier VPS Ubuntu 22.04 mediante un solo comando | `bash deploy.sh` en VPS limpio instala y configura todo el sistema |

### 4. Alcance del Proyecto

**Incluido en el alcance:**
- Motor DAST con 13 módulos de detección de vulnerabilidades OWASP Top 10:2021
- Sistema de autenticación y autorización con 3 roles (Admin/Analista/Usuario)
- Dashboard SOC con estadísticas y gráficos en tiempo real
- Integración con DeepSeek AI para análisis contextualizado de vulnerabilidades
- Generación de reportes exportables en PDF, HTML y JSON
- Panel de administración para gestión de usuarios y audit logs
- Despliegue en VPS Linux (149.34.48.176) con Nginx, systemd, PM2 y UFW

**Excluido del alcance:**
- Análisis estático de código fuente (SAST)
- Pruebas de penetración de infraestructura de red (VAPT)
- Análisis de aplicaciones móviles (iOS/Android)
- Pruebas de APIs GraphQL
- Integración con pipelines CI/CD (GitHub Actions, Jenkins)
- Soporte multi-tenant para múltiples organizaciones

### 5. Viabilidad del Sistema

El sistema es viable en todas sus dimensiones. A continuación se resume la evaluación (detallada en el FD01 — Informe de Factibilidad):

| **Dimensión** | **Resultado** | **Indicador clave** |
|:-------------|:-------------:|:--------------------|
| Técnica | VIABLE | Stack maduro y open source; equipo con experiencia Python+TypeScript; VPS activo |
| Económica | VIABLE | Inversión efectiva S/. 148.05; software 100% gratuito; B/C = 35.2 |
| Operativa | VIABLE | Sistema autónomo con systemd Restart=always; sin administración diaria requerida |
| Legal | VIABLE | Cumple Ley 30096 y 29733; aviso legal en interfaz; sin ataques destructivos |
| Social | VIABLE | Beneficia a estudiantes, QA, PYMES de Tacna; democratiza la ciberseguridad |
| Ambiental | VIABLE | Green IT: stack eficiente; distribución digital; infraestructura compartida |

### 6. Información Obtenida del Levantamiento de Información

El levantamiento de información se realizó mediante:

**Análisis de herramientas existentes:**
- Revisión de OWASP ZAP (open source, complejo, sin IA), Nikto (CLI, sin interfaz), Burp Suite Community (limitado, en inglés) y herramientas comerciales.
- Conclusión: ninguna herramienta gratuita ofrece interfaz web intuitiva en español + análisis IA + reportes PDF + gestión de usuarios.

**Entrevistas informales con estudiantes EPIS:**
- 8 de 10 estudiantes consultados nunca realizaron pruebas de seguridad a sus proyectos académicos.
- Los motivos principales: desconocimiento de herramientas, herramientas muy complejas de usar, resultados difíciles de interpretar.

**Análisis de vulnerabilidades reales:**
- Revisión de 5 sitios web de PYMES de Tacna (con autorización de sus propietarios).
- Resultado: 4 de 5 presentaban cabeceras de seguridad ausentes; 3 de 5 tenían archivos sensibles expuestos (.env o phpinfo.php); 2 de 5 eran vulnerables a XSS reflejado.

**Referencia técnica:**
- OWASP Top 10:2021 como marco de referencia para los módulos de detección.
- OWASP Testing Guide v4.2 como metodología de prueba por módulo.
- CWE/SANS Top 25 para la clasificación estándar de debilidades.

<div style="page-break-after: always;"></div>

---

## III. Análisis de Procesos

### a) Diagrama del Proceso Actual — Diagrama de Actividades

El proceso actual de verificación de seguridad en proyectos web académicos y de PYMES de Tacna es manual, fragmentado e inconsistente:

```
┌─────────────────────────────────────────────────────────────────────┐
│           PROCESO ACTUAL DE VERIFICACIÓN DE SEGURIDAD WEB           │
└─────────────────────────────────────────────────────────────────────┘

[INICIO]
   │
   ▼
[Desarrollador termina aplicación web]
   │
   ▼
[Decide si hacer pruebas de seguridad]
   │
   ├──── NO (80% de los casos) ────────────────────────────────────────┐
   │                                                                    │
   ▼                                                                    │
[SÍ: Busca herramienta manualmente en internet]                       │
   │                                                                    │
   ▼                                                                    │
[Descarga e instala herramienta (OWASP ZAP, Nikto, etc.)]             │
   │     ~30-60 minutos de instalación y configuración                 │
   ▼                                                                    │
[Ejecuta herramienta contra la aplicación]                            │
   │                                                                    │
   ▼                                                                    │
[Recibe reporte en inglés con cientos de resultados técnicos]         │
   │                                                                    │
   ▼                                                                    │
[Intenta interpretar manualmente cada resultado]                       │
   │     ~2-8 horas para entender y priorizar resultados               │
   ▼                                                                    │
[Busca soluciones en Google por cada vulnerabilidad]                  │
   │     ~1-2 días adicionales de investigación                        │
   ▼                                                                    │
[Implementa correcciones (algunas, no todas)]                         │
   │                                                                    │
   ▼                                                                    │
[No tiene reporte formal exportable]  ◄──────────────────────────────-┘
   │
   ▼
[Despliega aplicación a producción SIN auditoría de seguridad]
   │
   ▼
[FIN — Aplicación potencialmente vulnerable en producción]
```

**Problemas identificados en el proceso actual:**
- **Tiempo:** El proceso manual consume 2-10 días si se realiza; la mayoría no lo realiza.
- **Costo:** Las herramientas profesionales son inaccesibles (USD 449-4,500/año).
- **Barrera idiomática:** Resultados en inglés, difíciles de interpretar sin conocimiento en seguridad.
- **Sin priorización:** No hay orientación sobre qué vulnerabilidades corregir primero.
- **Sin reportes formales:** Imposible generar documentación de auditoría para entregar.
- **Sin seguimiento:** No hay comparación entre versiones para verificar que las correcciones funcionaron.

### b) Diagrama del Proceso Propuesto — Diagrama de Actividades Inicial

Con VulnScan Pro, el proceso de verificación de seguridad se simplifica radicalmente:

```
┌─────────────────────────────────────────────────────────────────────┐
│         PROCESO PROPUESTO CON VULNSCAN PRO                          │
└─────────────────────────────────────────────────────────────────────┘

[INICIO]
   │
   ▼
[Desarrollador termina versión de la aplicación web]
   │
   ▼
[Abre navegador → accede a http://149.34.48.176]
   │     < 30 segundos
   ▼
[Se autentica (login) con sus credenciales JWT]
   │     < 10 segundos
   ▼
[Ingresa URL objetivo + selecciona profundidad + stack tecnológico]
   │     < 2 minutos de configuración
   ▼
[Inicia escaneo → sistema ejecuta 13 módulos OWASP en paralelo]
   │     < 10 minutos (escaneo completo típico)
   ▼
[Dashboard muestra progreso en tiempo real (polling 3s)]
   │
   ▼
[Escaneo completo → resultados con severidad codificada por color]
   │
   ├── ¿Vulnerabilidades críticas/altas? ─── SÍ ─────────────────────┐
   │                                                                    │
   │                                                                    ▼
   │                                                          [Revisa detalle de cada vuln]
   │                                                          [Lee análisis IA: escenario
   │                                                           de ataque + código de remediación
   │                                                           para su stack tecnológico]
   │                                                          [Implementa correcciones]
   │                                                          [Exporta reporte PDF/HTML/JSON]
   │                                                          [Re-escanea para verificar]
   │                                                                    │
   ▼                                                                    │
[Exporta reporte formal PDF en español] ◄──────────────────────────────┘
   │
   ▼
[Despliega aplicación a producción CON auditoría de seguridad documentada]
   │
   ▼
[FIN — Aplicación auditada, con reporte formal y vulnerabilidades remediadas]
```

**Beneficios del proceso propuesto:**
- **Tiempo:** De 2-10 días a < 15 minutos (configuración + escaneo + revisión).
- **Costo:** S/. 0.00 en licencias; solo requiere navegador web.
- **Idioma:** Resultados en español con análisis contextualizado.
- **Priorización:** Severidad CVSS + risk score global orienta qué corregir primero.
- **Reportes formales:** PDF/HTML/JSON listos para entregar en auditorías o presentaciones académicas.
- **Seguimiento:** Historial de escaneos para comparar versiones y verificar remediaciones.

<div style="page-break-after: always;"></div>

---

## IV. Especificación de Requerimientos de Software

### a) Cuadro de Requerimientos Funcionales Inicial

Los requerimientos funcionales iniciales se obtuvieron del levantamiento de información y representan las capacidades básicas identificadas antes del análisis detallado:

| **ID** | **Descripción** | **Prioridad** |
|:------:|:----------------|:-------------:|
| RFI-01 | El sistema debe permitir registrar y autenticar usuarios | Alta |
| RFI-02 | El sistema debe permitir ingresar una URL objetivo para escanear | Alta |
| RFI-03 | El sistema debe detectar vulnerabilidades web comunes | Alta |
| RFI-04 | El sistema debe mostrar los resultados de las vulnerabilidades detectadas | Alta |
| RFI-05 | El sistema debe generar reportes exportables de los resultados | Alta |
| RFI-06 | El sistema debe tener un panel de administración de usuarios | Media |
| RFI-07 | El sistema debe mostrar estadísticas de los escaneos realizados | Media |
| RFI-08 | El sistema debe integrar inteligencia artificial para analizar vulnerabilidades | Media |
| RFI-09 | El sistema debe mantener un historial de escaneos | Media |
| RFI-10 | El sistema debe controlar el acceso según el rol del usuario | Alta |

### b) Cuadro de Requerimientos No Funcionales

| **ID** | **Descripción** | **Categoría ISO 25010** | **Prioridad** |
|:------:|:----------------|:-----------------------:|:-------------:|
| RNF-01 | El sistema debe cifrar las contraseñas usando bcrypt con factor de costo mínimo 10 | Seguridad | Alta |
| RNF-02 | El tiempo de respuesta para iniciar un escaneo no debe superar 2 segundos desde el clic | Rendimiento | Alta |
| RNF-03 | El sistema debe soportar mínimo 10 escaneos simultáneos sin degradación del rendimiento | Rendimiento | Alta |
| RNF-04 | La interfaz de usuario debe ser intuitiva: un usuario sin experiencia completa su primer escaneo en < 5 min | Usabilidad | Alta |
| RNF-05 | El sistema debe tener uptime mínimo del 99.5% mensual | Confiabilidad | Alta |
| RNF-06 | El sistema debe recuperarse automáticamente ante fallos en < 5 segundos (systemd Restart=always) | Confiabilidad | Alta |
| RNF-07 | Todos los tokens JWT deben expirar en máximo 24 horas y tener JTI único | Seguridad | Alta |
| RNF-08 | El sistema debe aplicar rate limiting en al menos 3 capas: Nginx, API global y endpoint de login | Seguridad | Alta |
| RNF-09 | El sistema debe registrar en audit log el 100% de las acciones de autenticación y gestión de escaneos | Seguridad | Alta |
| RNF-10 | Los módulos de escaneo deben ser independientes entre sí para permitir mantenimiento sin afectar otros | Mantenibilidad | Media |
| RNF-11 | El sistema debe ser desplegable en cualquier VPS Ubuntu 22.04 LTS mediante un único script (deploy.sh) | Portabilidad | Media |
| RNF-12 | La tasa de falsos positivos por módulo de escaneo no debe superar el 15% | Confiabilidad | Media |
| RNF-13 | Todas las comunicaciones en producción deben usar HTTPS (TLS 1.2+) | Seguridad | Alta |
| RNF-14 | Los reportes PDF deben generarse en menos de 10 segundos para escaneos con hasta 50 vulnerabilidades | Rendimiento | Media |
| RNF-15 | Toda consulta a la base de datos debe usar SQL parametrizado (ORM SQLAlchemy) — sin concatenación de strings SQL | Seguridad | Alta |
| RNF-16 | La interfaz debe ser compatible con Chrome 120+, Firefox 120+ y Edge 120+ | Usabilidad | Alta |
| RNF-17 | El sistema debe aplicar headers de seguridad HTTP en todas las respuestas: CSP, HSTS, X-Frame-Options, X-Content-Type-Options | Seguridad | Alta |
| RNF-18 | El código fuente del backend debe cumplir con PEP 8 (estilo Python) para facilitar el mantenimiento | Mantenibilidad | Baja |
| RNF-19 | La base de datos debe soportar 20 conexiones simultáneas (pool_size=10, max_overflow=20) | Rendimiento | Media |
| RNF-20 | El sistema no debe almacenar credenciales, tokens API ni información sensible en texto plano en el repositorio de código | Seguridad | Alta |
| RNF-21 | La página de dashboard debe cargar en < 3 segundos en una conexión de 10 Mbps | Rendimiento | Media |
| RNF-22 | Los módulos de escaneo deben respetar timeouts configurables (5-60 s) para no bloquear el sistema | Rendimiento | Alta |
| RNF-23 | El sistema debe funcionar sin JavaScript en la capa de datos (Next.js App Router con componentes del servidor) | Usabilidad | Baja |
| RNF-24 | La documentación del sistema debe seguir las plantillas EPIS-UPT: FD01, FD02, FD03, FD04 | Mantenibilidad | Media |
| RNF-25 | El sistema debe ser modular para permitir agregar nuevos módulos de escaneo sin modificar la arquitectura base | Mantenibilidad | Media |
| RNF-26 | El servicio del backend debe ejecutarse con privilegios mínimos: NoNewPrivileges=yes, PrivateTmp=yes (systemd) | Seguridad | Alta |
| RNF-27 | El firewall UFW debe bloquear todos los puertos excepto 22 (SSH), 80 (HTTP), 443 (HTTPS) desde internet | Seguridad | Alta |
| RNF-28 | MySQL debe estar accesible únicamente desde localhost (puerto 3306 no expuesto a internet) | Seguridad | Alta |
| RNF-29 | La API REST debe documentarse automáticamente con OpenAPI/Swagger (disponible en /docs en desarrollo) | Mantenibilidad | Baja |
| RNF-30 | El sistema debe implementar validación de entrada con Pydantic en todos los endpoints de la API | Seguridad | Alta |

### c) Cuadro de Requerimientos Funcionales Final

Los requerimientos funcionales finales incorporan el análisis completo del sistema y las capacidades identificadas durante el diseño detallado:

#### RF — Módulo de Autenticación y Gestión de Usuarios

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-01 | El sistema debe permitir registrar nuevos usuarios con nombre, email, contraseña (mín. 8 caracteres, 1 número, 1 mayúscula) y rol. La contraseña se hashea con bcrypt (cost ≥ 10) antes de almacenarse. | Administrador / Nuevo Usuario | Alta |
| RF-02 | El sistema debe autenticar usuarios con email y contraseña, generando un JWT (HS256, 24h expiry, JTI único) y una entrada en la tabla UserSession. | Usuario / Analista / Admin | Alta |
| RF-03 | El sistema debe bloquear automáticamente la cuenta de un usuario por 15 minutos tras 5 intentos de login fallidos consecutivos, registrando cada intento en AuditLog. | Sistema (automático) | Alta |
| RF-04 | El sistema debe desbloquear automáticamente la cuenta bloqueada al transcurrir 15 minutos desde el último intento fallido. | Sistema (automático) | Alta |
| RF-05 | El sistema debe permitir al usuario cerrar su sesión actual (logout), invalidando el JWT en la tabla UserSession (campo `is_active = False`). | Todos los usuarios | Alta |
| RF-06 | El sistema debe permitir al administrador crear usuarios con roles: Admin, Analista o Usuario. | Administrador | Alta |
| RF-07 | El sistema debe permitir al administrador editar el nombre, email, rol y estado (activo/bloqueado) de cualquier usuario. | Administrador | Alta |
| RF-08 | El sistema debe permitir al administrador bloquear o desbloquear manualmente cualquier cuenta de usuario. | Administrador | Alta |
| RF-09 | El sistema debe permitir al administrador eliminar usuarios, con confirmación previa. Los escaneos del usuario eliminado se conservan en la base de datos con `user_id = NULL`. | Administrador | Media |
| RF-10 | El sistema debe permitir al usuario solicitar recuperación de contraseña ingresando su email. El sistema genera un token único con expiración de 1 hora. | Todos los usuarios | Media |
| RF-11 | El sistema debe permitir al usuario cambiar su contraseña usando el token de recuperación, verificando que el token sea válido y no haya expirado. | Todos los usuarios | Media |
| RF-12 | El sistema debe permitir al usuario autenticado cambiar su contraseña actual ingresando la contraseña actual y la nueva contraseña. | Todos los usuarios | Media |
| RF-13 | El sistema debe permitir al usuario ver y editar su nombre, email y organización desde su perfil. | Todos los usuarios | Media |
| RF-14 | El sistema debe mostrar al usuario la lista de sus sesiones activas (dispositivo, IP, fecha de inicio) y permitirle cerrar todas las sesiones simultáneamente. | Todos los usuarios | Media |
| RF-15 | El sistema debe rechazar con HTTP 403 cualquier solicitud a endpoints protegidos que no incluya un JWT válido y no expirado. | Sistema (automático) | Alta |
| RF-16 | El sistema debe rechazar con HTTP 403 cualquier solicitud de un usuario a endpoints fuera de su rol (Admin-only, Analista+). | Sistema (automático) | Alta |

#### RF — Módulo de Escaneo de Vulnerabilidades

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-17 | El sistema debe permitir al usuario autenticado iniciar un nuevo escaneo ingresando la URL objetivo (formato: http:// o https://). | Todos los usuarios | Alta |
| RF-18 | El sistema debe validar que la URL objetivo tenga un formato válido (protocolo HTTP/HTTPS, dominio o IP pública) antes de aceptar el escaneo. | Sistema (automático) | Alta |
| RF-19 | El sistema debe rechazar el inicio de un escaneo si el usuario ya tiene un escaneo en estado "en progreso" (máximo 1 activo por usuario). | Sistema (automático) | Alta |
| RF-20 | El sistema debe permitir seleccionar el nivel de profundidad del escaneo: Básico (Headers + SSL + Sensitive Files), Estándar (+ XSS + SQLi + CSRF + HTTP Methods + Error Disclosure), Completo (los 13 módulos). | Todos los usuarios | Alta |
| RF-21 | El sistema debe permitir seleccionar el stack tecnológico del objetivo para personalizar los payloads y el análisis IA: PHP, Python/Django, Node.js/Express, Java/Spring, Ruby on Rails, ASP.NET Core, Genérico. | Analista / Admin | Media |
| RF-22 | El sistema debe permitir configurar el timeout por módulo de escaneo: 5, 10, 30 o 60 segundos. | Analista / Admin | Media |
| RF-23 | El sistema debe permitir habilitar o deshabilitar el análisis por IA (DeepSeek) para cada escaneo. | Todos los usuarios | Media |
| RF-24 | El sistema debe ejecutar el escaneo en segundo plano (BackgroundTasks) para no bloquear la interfaz de usuario durante el proceso. | Sistema (automático) | Alta |
| RF-25 | El módulo de SQL Injection debe probar payloads de inyección SQL error-based (`'`, `' OR 1=1--`), boolean-based (`' AND 1=1`, `' AND 1=2`) y UNION-based en todos los parámetros GET y campos de formulario encontrados. | Sistema (automático) | Alta |
| RF-26 | El módulo de XSS debe probar payloads de script inyectado (`<script>alert(1)</script>`, `"><img src=x onerror=alert(1)>`) en parámetros GET y campos de formulario, verificando si el payload aparece sin escapar en la respuesta. | Sistema (automático) | Alta |
| RF-27 | El módulo de CSRF debe verificar la presencia de tokens CSRF en formularios POST y el atributo SameSite=Strict/Lax en cookies de sesión. | Sistema (automático) | Alta |
| RF-28 | El módulo de SSRF debe probar redirecciones hacia recursos internos (`http://127.0.0.1`, `http://169.254.169.254`, `http://localhost`) en parámetros de URL. | Sistema (automático) | Alta |
| RF-29 | El módulo de LFI debe probar secuencias de path traversal (`../../../../etc/passwd`, `..%2F..%2Fetc%2Fshadow`) en parámetros de archivo. | Sistema (automático) | Alta |
| RF-30 | El módulo de Command Injection debe probar inyecciones de comandos OS (`;ls`, `|id`, `&&whoami`) en parámetros de entrada. | Sistema (automático) | Alta |
| RF-31 | El módulo de Open Redirect debe detectar parámetros de redirección (redirect, url, next, return) y probar si permiten redirigir a dominios externos arbitrarios. | Sistema (automático) | Media |
| RF-32 | El módulo de Security Headers debe verificar la presencia y configuración correcta de: Content-Security-Policy, Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy. | Sistema (automático) | Alta |
| RF-33 | El módulo de SSL/TLS debe verificar: soporte de TLS 1.0/1.1 (deprecados), fechas de validez del certificado, uso de algoritmos de cifrado débiles (RC4, DES, 3DES, MD5). | Sistema (automático) | Alta |
| RF-34 | El módulo de Sensitive Files debe verificar la accesibilidad de al menos 20 rutas comunes: `.env`, `.git/config`, `phpinfo.php`, `wp-config.php`, `.htpasswd`, `web.config`, `backup.sql`, `db_backup.zip`, `admin/`, `phpmyadmin/`, etc. | Sistema (automático) | Alta |
| RF-35 | El módulo de HTTP Methods debe verificar si métodos peligrosos están habilitados: PUT, DELETE, TRACE, CONNECT, PATCH (cuando no es esperado). | Sistema (automático) | Media |
| RF-36 | El módulo de Error Disclosure debe verificar si respuestas de error (404, 500) revelan información interna: stack traces, versiones de framework, paths absolutos del servidor, cadenas de conexión. | Sistema (automático) | Media |
| RF-37 | El módulo de Web Crawling debe descubrir URLs internas de la aplicación rastreando los links HTML de la página principal hasta 2 niveles de profundidad. | Sistema (automático) | Media |
| RF-38 | El sistema debe calcular un risk score global (0-100) para cada escaneo basado en el número y severidad de las vulnerabilidades detectadas: Crítica=10pts, Alta=7pts, Media=3pts, Baja=1pt. | Sistema (automático) | Alta |
| RF-39 | El sistema debe clasificar cada vulnerabilidad detectada con nivel de severidad: Crítica, Alta, Media, Baja o Informativa, según los criterios CVSS. | Sistema (automático) | Alta |
| RF-40 | El sistema debe actualizar el estado del escaneo en tiempo real: Pendiente → En Progreso → Completado (o Fallido), almacenado en la base de datos para polling del frontend. | Sistema (automático) | Alta |
| RF-41 | El sistema debe registrar el tiempo de inicio y fin de cada escaneo, calculando la duración total. | Sistema (automático) | Media |
| RF-42 | El sistema debe registrar el número total de URLs encontradas durante el crawling y el número de URLs probadas por cada módulo. | Sistema (automático) | Baja |

#### RF — Módulo de Inteligencia Artificial (DeepSeek AI)

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-43 | El sistema debe enviar cada vulnerabilidad detectada a la API DeepSeek AI para obtener: puntuación CVSS v3.1, vector CVSS, identificador CWE, escenario de ataque detallado y código de remediación específico para el stack seleccionado. | Sistema (automático) | Alta |
| RF-44 | El sistema debe generar un reporte ejecutivo global del escaneo usando DeepSeek AI: risk score (0-100), nivel de riesgo (Crítico/Alto/Medio/Bajo/Seguro), resumen ejecutivo, top 3 vulnerabilidades más críticas y plan de acción priorizado. | Sistema (automático) | Alta |
| RF-45 | El sistema debe incluir una estimación de probabilidad de falso positivo (0-100%) por cada vulnerabilidad en el análisis IA. | Sistema (automático) | Media |
| RF-46 | El sistema debe implementar un fallback local cuando la API DeepSeek no esté disponible, proporcionando análisis predefinidos para: SQL Injection (CWE-89), XSS (CWE-79) y CSRF (CWE-352). | Sistema (automático) | Alta |
| RF-47 | El sistema debe indicar claramente en la interfaz si el análisis IA proviene de DeepSeek (análisis personalizado) o del fallback local (análisis genérico). | Sistema (automático) | Media |

#### RF — Módulo de Reportes

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-48 | El sistema debe generar reportes en formato PDF usando WeasyPrint, incluyendo: portada con logo, metadatos del escaneo (URL, fecha, duración, módulos ejecutados), tabla de vulnerabilidades por severidad, descripción técnica completa, análisis IA y risk score visual. | Todos los usuarios | Alta |
| RF-49 | El sistema debe generar reportes en formato HTML navegable con los mismos datos que el PDF, pero con tabla de contenidos clickeable y diseño responsivo. | Todos los usuarios | Media |
| RF-50 | El sistema debe generar reportes en formato JSON estructurado con todos los datos del escaneo y vulnerabilidades, para integración en sistemas externos o pipelines CI/CD. | Analista / Admin | Media |
| RF-51 | El sistema debe almacenar los reportes generados en la base de datos con metadatos: tipo (PDF/HTML/JSON), tamaño, fecha de generación y usuario que lo generó. | Sistema (automático) | Media |
| RF-52 | El sistema debe permitir descargar un reporte directamente desde la vista de detalle del escaneo o desde el historial de escaneos. | Todos los usuarios | Alta |

#### RF — Módulo de Dashboard y Visualización

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-53 | El dashboard debe mostrar contadores animados: total de escaneos realizados, total de vulnerabilidades críticas detectadas, total de sitios distintos analizados y risk score promedio del mes. | Todos los usuarios | Alta |
| RF-54 | El dashboard debe mostrar un gráfico de dona (Chart.js) con la distribución de vulnerabilidades por severidad (Crítica/Alta/Media/Baja/Informativa) de los últimos 30 días. | Todos los usuarios | Alta |
| RF-55 | El dashboard debe mostrar un gráfico de línea temporal (Chart.js) con la cantidad de vulnerabilidades detectadas por día en los últimos 7 días. | Todos los usuarios | Media |
| RF-56 | El dashboard debe mostrar una tabla de los últimos 10 escaneos realizados con: URL objetivo, estado, fecha, número de vulnerabilidades y link al detalle. | Todos los usuarios | Alta |
| RF-57 | El sistema debe actualizar automáticamente las estadísticas del dashboard cada 60 segundos sin recargar la página. | Sistema (automático) | Media |
| RF-58 | El sistema debe mostrar el estado de un escaneo en progreso con barra de progreso y nombre del módulo actual (polling cada 3 segundos). | Todos los usuarios | Alta |

#### RF — Módulo de Administración

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-59 | El panel de administración debe mostrar la lista de todos los usuarios registrados con: nombre, email, rol, estado (activo/bloqueado), número de escaneos y última actividad. | Administrador | Alta |
| RF-60 | El panel de administración debe mostrar todos los escaneos de todos los usuarios con filtros por: estado, usuario, rango de fechas y URL objetivo. | Administrador | Alta |
| RF-61 | El panel de administración debe mostrar el audit log completo con paginación (20 registros/página) y filtros por: usuario, acción, fecha y nivel de resultado. | Administrador | Alta |
| RF-62 | El sistema debe registrar en audit log toda acción del sistema: login, logout, inicio de escaneo, exportación de reporte, creación/edición/eliminación de usuario, cambio de rol, bloqueo/desbloqueo de cuenta. | Sistema (automático) | Alta |
| RF-63 | El panel de administración debe mostrar estadísticas globales: total de usuarios activos, total de escaneos del sistema, total de vulnerabilidades detectadas acumuladas, distribución por tipo y severidad. | Administrador | Media |

#### RF — Módulo de Historial de Escaneos

| **ID** | **Descripción** | **Actor** | **Prioridad** |
|:------:|:----------------|:---------:|:-------------:|
| RF-64 | El sistema debe mostrar al usuario autenticado su historial paginado de escaneos (20/página) con: URL objetivo, fecha/hora, duración, vulnerabilidades por severidad, estado y risk score. | Todos los usuarios | Alta |
| RF-65 | El sistema debe permitir filtrar el historial por: estado del escaneo (todos/completado/en progreso/fallido), URL objetivo (búsqueda parcial) y rango de fechas. | Todos los usuarios | Media |
| RF-66 | El sistema debe permitir al usuario eliminar un escaneo de su historial (con confirmación previa), eliminando en cascada sus vulnerabilidades y reportes asociados. | Todos los usuarios | Media |
| RF-67 | El sistema debe permitir al usuario acceder al reporte detallado de cualquier escaneo pasado de su historial. | Todos los usuarios | Alta |

### d) Reglas de Negocio

| **ID** | **Regla de Negocio** | **Descripción** | **Módulo afectado** |
|:------:|:--------------------|:----------------|:--------------------|
| RN-01 | Uso solo con autorización | El usuario debe declarar explícitamente poseer autorización sobre la aplicación objetivo antes de iniciar cualquier escaneo. Aceptar los términos es obligatorio en el registro y en cada escaneo. | Escaneo |
| RN-02 | Un escaneo activo por usuario | Un usuario solo puede tener 1 escaneo en estado "en progreso" simultáneamente. Intentar iniciar un segundo escaneo devuelve error HTTP 409 (Conflict). | Escaneo |
| RN-03 | Contraseñas con requisitos mínimos | Las contraseñas deben tener mínimo 8 caracteres, al menos 1 letra mayúscula y al menos 1 dígito numérico. Contraseñas que no cumplen son rechazadas con HTTP 422. | Autenticación |
| RN-04 | Bloqueo por fuerza bruta | Tras 5 intentos de login fallidos consecutivos para la misma cuenta, la cuenta se bloquea automáticamente por 15 minutos. El contador se resetea al iniciar sesión exitosamente. | Autenticación |
| RN-05 | JWT con expiración fija | Los tokens JWT tienen vida máxima de 24 horas. Tokens expirados son rechazados con HTTP 401 independientemente del estado de la sesión en base de datos. | Autenticación |
| RN-06 | Sin escaneos de redes privadas | El sistema rechaza URLs con rangos de IP privados: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16 (link-local). Solo se permiten direcciones IP públicas y dominios resolvibles. | Escaneo |
| RN-07 | Sin modificaciones al objetivo | Los módulos de escaneo solo realizan operaciones GET (lectura) o POST de prueba con payloads inofensivos. Ningún módulo elimina, modifica ni crea datos en el objetivo. | Escaneo |
| RN-08 | Timeout obligatorio | Cada módulo de escaneo debe completarse dentro del timeout configurado (5-60 s). Si el módulo supera el timeout, se registra como "timeout" en los resultados y el sistema continúa con el siguiente módulo. | Escaneo |
| RN-09 | Severidad por CVSS | La severidad de cada vulnerabilidad se clasifica según los rangos CVSS v3.1: Crítica (9.0-10.0), Alta (7.0-8.9), Media (4.0-6.9), Baja (0.1-3.9), Informativa (0.0). | Resultados |
| RN-10 | Audit log inmutable | Los registros del audit log no pueden ser editados, eliminados ni modificados por ningún usuario, incluido el administrador. Son de solo lectura. | Auditoría |
| RN-11 | Retención de audit logs | Los registros del audit log se retienen por un mínimo de 90 días desde su creación. Registros más antiguos pueden archivarse automáticamente. | Auditoría |
| RN-12 | Reportes asociados a escaneos | Un reporte solo puede generarse cuando el escaneo asociado tiene estado "completado". No se pueden generar reportes de escaneos en progreso o fallidos. | Reportes |
| RN-13 | Contraseñas no visibles | Las contraseñas no se almacenan en ningún log, auditoría, respuesta de API ni variable de entorno en texto plano. Solo el hash bcrypt se almacena. | Seguridad |
| RN-14 | Variables sensibles en .env | DATABASE_URL, SECRET_KEY y DEEPSEEK_API_KEY solo pueden estar en el archivo `.env`. El archivo `.env` está excluido del repositorio de código mediante `.gitignore`. | Seguridad |
| RN-15 | Validación de entrada obligatoria | Todos los endpoints de la API deben validar sus parámetros de entrada con esquemas Pydantic antes de procesarlos. Datos inválidos retornan HTTP 422 con descripción del error de validación. | API |
| RN-16 | Risk score compuesto | El risk score global de un escaneo se calcula como: `min(100, Σ(Críticas×10 + Altas×7 + Medias×3 + Bajas×1))`. Un sitio sin vulnerabilidades tiene risk score 0. | Resultados |
| RN-17 | Fallback AI obligatorio | Si la API DeepSeek falla, el sistema no debe mostrar error al usuario; debe proporcionar análisis predefinido para los tipos de vulnerabilidades conocidos y marcarlo como "análisis local". | IA |
| RN-18 | Roles escalables | El sistema permite asignar a cada usuario exactamente un rol. Un administrador no puede quitarse el rol Admin a sí mismo (previene quedarse sin administradores en el sistema). | Usuarios |

<div style="page-break-after: always;"></div>

---

## V. Fase de Desarrollo

### 1. Perfiles de Usuario

#### Perfil 1: Administrador del Sistema

| **Atributo** | **Descripción** |
|:------------|:----------------|
| **Rol en el sistema** | Administrador |
| **Descripción** | Usuario con control total sobre la plataforma VulnScan Pro. Gestiona usuarios, accede a todos los escaneos, revisa audit logs y configura el sistema. Típicamente el desarrollador o el encargado de TI de la organización que usa la plataforma. |
| **Conocimiento técnico** | Alto — ingeniería de sistemas, ciberseguridad, administración de sistemas |
| **Frecuencia de uso** | Semanal (revisión de audit logs, gestión de usuarios) |
| **Permisos** | CRUD completo de usuarios, lectura de todos los escaneos, acceso al audit log, estadísticas globales, configuración del sistema |
| **Restricciones** | No puede editarse el rol Admin a sí mismo; no puede eliminar el último administrador del sistema |

#### Perfil 2: Analista de Seguridad

| **Atributo** | **Descripción** |
|:------------|:----------------|
| **Rol en el sistema** | Analista |
| **Descripción** | Usuario con experiencia técnica en seguridad o desarrollo. Ejecuta escaneos configurados con parámetros avanzados (stack, timeout, profundidad), interpreta resultados detallados y genera reportes formales para auditorías o presentaciones. |
| **Conocimiento técnico** | Intermedio-Alto — desarrollo web, fundamentos de seguridad, familiaridad con OWASP |
| **Frecuencia de uso** | Diaria/Semanal (auditorías de proyectos en desarrollo) |
| **Permisos** | Crear y gestionar sus propios escaneos, configuración avanzada, acceso a análisis IA, exportar reportes PDF/HTML/JSON, ver historial propio |
| **Restricciones** | Solo ve sus propios escaneos (no los de otros usuarios); máximo 1 escaneo simultáneo |

#### Perfil 3: Usuario Regular

| **Atributo** | **Descripción** |
|:------------|:----------------|
| **Rol en el sistema** | Usuario |
| **Descripción** | Desarrollador o estudiante sin especialización en seguridad. Usa la plataforma para obtener un diagnóstico rápido de sus proyectos antes de entregarlos o desplegarlos. Necesita una interfaz sencilla y resultados claros en español. |
| **Conocimiento técnico** | Básico-Intermedio — desarrollo web, sin especialización en seguridad |
| **Frecuencia de uso** | Ocasional (antes de entregas o despliegues) |
| **Permisos** | Crear escaneos básicos (sin configuración avanzada de stack/timeout), ver resultados, exportar reporte PDF básico, ver historial propio |
| **Restricciones** | Solo ve sus propios escaneos; máximo 1 escaneo simultáneo; sin acceso a configuración avanzada |

---

### 2. Modelo Conceptual

#### a) Diagrama de Paquetes

```
┌──────────────────────────────────────────────────────────────┐
│                    VulnScan Pro — Sistema                     │
│                                                              │
│  ┌─────────────────┐    ┌──────────────────────────────────┐ │
│  │   «package»     │    │         «package»                │ │
│  │   Frontend      │    │         Backend API              │ │
│  │   (Next.js 16)  │◄──►│         (FastAPI)                │ │
│  │                 │    │                                  │ │
│  │ + Dashboard     │    │ + auth_routes.py                 │ │
│  │ + Scanner       │    │ + scan_routes.py                 │ │
│  │ + Admin         │    │ + admin_routes.py                │ │
│  │ + Reports       │    │ + report_routes.py               │ │
│  │ + Profile       │    │ + solutions_routes.py            │ │
│  └─────────────────┘    └──────────────┬─────────────────┘ │
│                                         │                    │
│           ┌─────────────────────────────▼──────────────────┐ │
│           │              «package»                         │ │
│           │         Servicios del Sistema                  │ │
│           │                                                │ │
│           │  ┌──────────────┐  ┌──────────────────────┐   │ │
│           │  │ «component» │  │    «component»        │   │ │
│           │  │  scanner.py  │  │  ai_service.py        │   │ │
│           │  │ (13 módulos) │  │  (DeepSeek API)       │   │ │
│           │  └──────────────┘  └──────────────────────┘   │ │
│           │                                                │ │
│           │  ┌──────────────┐  ┌──────────────────────┐   │ │
│           │  │ «component» │  │    «component»        │   │ │
│           │  │    auth.py   │  │    models.py          │   │ │
│           │  │  (JWT+bcrypt)│  │  (SQLAlchemy ORM)     │   │ │
│           │  └──────────────┘  └──────────────────────┘   │ │
│           └────────────────────────────────────────────────┘ │
│                                         │                    │
│           ┌─────────────────────────────▼──────────────────┐ │
│           │              «package»                         │ │
│           │           Base de Datos                        │ │
│           │         MySQL 8.0 — 7 tablas                   │ │
│           └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### b) Diagrama de Casos de Uso

**Actores del sistema:**
- **Usuario** (hereda de: Sistema)
- **Analista** (extiende Usuario — con permisos adicionales de configuración avanzada)
- **Administrador** (extiende Analista — con permisos completos)
- **Sistema** (actor interno — ejecuta escaneos en background y audita acciones)
- **DeepSeek AI** (actor externo — servicio de IA para análisis de vulnerabilidades)

**Casos de uso principales:**

```
                    ┌──────────────────────────────────────────────────┐
                    │              Sistema VulnScan Pro                 │
                    │                                                    │
  ┌──────────┐     │  ┌──────────────────┐  ┌───────────────────────┐ │
  │          │     │  │ UC-01: Registrarse│  │ UC-02: Iniciar Sesión │ │
  │  Usuario │─────┼─►│                  │  │                       │ │
  │          │     │  └──────────────────┘  └───────────────────────┘ │
  └──────────┘     │                                                    │
       │           │  ┌──────────────────┐  ┌───────────────────────┐ │
       │           │  │ UC-03: Iniciar   │  │ UC-04: Ver Resultado  │ │
       └───────────┼─►│ Escaneo          │  │ de Escaneo            │ │
                   │  └──────────────────┘  └───────────────────────┘ │
  ┌──────────┐     │                                                    │
  │          │     │  ┌──────────────────┐  ┌───────────────────────┐ │
  │ Analista │─────┼─►│ UC-05: Configurar│  │ UC-06: Exportar       │ │
  │          │     │  │ Escaneo Avanzado │  │ Reporte PDF/HTML/JSON │ │
  └──────────┘     │  └──────────────────┘  └───────────────────────┘ │
       │           │                                                    │
       │           │  ┌──────────────────┐  ┌───────────────────────┐ │
       │           │  │ UC-07: Ver       │  │ UC-08: Gestionar      │ │
       │           │  │ Historial Escan. │  │ Mi Perfil             │ │
       │           │  └──────────────────┘  └───────────────────────┘ │
  ┌──────────┐     │                                                    │
  │          │     │  ┌──────────────────┐  ┌───────────────────────┐ │
  │  Admin   │─────┼─►│ UC-09: Gestionar │  │ UC-10: Ver Audit Log  │ │
  │          │     │  │ Usuarios         │  │                       │ │
  └──────────┘     │  └──────────────────┘  └───────────────────────┘ │
                   │                                                    │
  ┌──────────┐     │  ┌──────────────────┐  ┌───────────────────────┐ │
  │ Sistema  │─────┼─►│ UC-11: Ejecutar  │  │ UC-12: Analizar con  │ │
  │(interno) │     │  │ Módulos OWASP    │  │ DeepSeek AI           │ │
  └──────────┘     │  └──────────────────┘  └───────────────────────┘ │
                   │                                                    │
  ┌──────────┐     │  ┌──────────────────┐                            │
  │DeepSeek  │─────┼─►│ UC-13: Generar   │                            │
  │   AI     │     │  │ Análisis IA      │                            │
  └──────────┘     │  └──────────────────┘                            │
                   └──────────────────────────────────────────────────┘
```

#### c) Escenarios de Caso de Uso (Narrativa)

---

**Caso de Uso: UC-01 — Registrarse en el Sistema**

| **Campo** | **Descripción** |
|:---------|:----------------|
| **Nombre** | Registrarse en el Sistema |
| **ID** | UC-01 |
| **Actor principal** | Usuario no autenticado |
| **Precondición** | El usuario no posee una cuenta en el sistema |
| **Postcondición** | El usuario tiene una cuenta activa con rol "usuario" y puede iniciar sesión |
| **Flujo Principal** | 1. El usuario navega a la página de registro. 2. Ingresa nombre completo, email y contraseña (mín. 8 chars, 1 número, 1 mayúscula). 3. Lee y acepta los términos de uso (incluye aviso legal de uso autorizado). 4. El sistema valida el formato de email y los requisitos de contraseña. 5. El sistema verifica que el email no esté registrado previamente. 6. El sistema hashea la contraseña con bcrypt (cost=10). 7. El sistema crea el usuario en la base de datos con rol "usuario" y estado "activo". 8. El sistema redirige al usuario a la pantalla de login. |
| **Flujo Alternativo A** | 4a. El email ya está registrado: el sistema muestra "Email ya registrado". 4b. La contraseña no cumple los requisitos: muestra los requisitos específicos incumplidos. |
| **Flujo de Excepción** | Error de base de datos: el sistema muestra "Error de registro, intente de nuevo". |
| **Reglas de negocio** | RN-03 (contraseñas), RN-01 (términos de uso), RN-13 (contraseñas no visibles) |

---

**Caso de Uso: UC-02 — Iniciar Sesión**

| **Campo** | **Descripción** |
|:---------|:----------------|
| **Nombre** | Iniciar Sesión |
| **ID** | UC-02 |
| **Actor principal** | Usuario registrado |
| **Precondición** | El usuario posee cuenta activa y no bloqueada |
| **Postcondición** | El usuario está autenticado con un JWT válido y sesión activa en la base de datos |
| **Flujo Principal** | 1. El usuario ingresa email y contraseña en el formulario de login. 2. El sistema verifica si la cuenta existe y no está bloqueada. 3. El sistema verifica la contraseña contra el hash bcrypt. 4. El sistema genera un JWT (HS256, 24h, JTI único). 5. El sistema crea una entrada en UserSession (user_id, jti, ip, user_agent, is_active=True). 6. El sistema registra el evento en AuditLog (action="login_success"). 7. El sistema retorna el JWT al cliente. 8. El frontend almacena el JWT y redirige al dashboard. |
| **Flujo Alternativo A** | 3a. Contraseña incorrecta: el sistema incrementa `failed_login_attempts`. Si llega a 5, bloquea la cuenta por 15 minutos (RN-04). Registra en AuditLog. |
| **Flujo Alternativo B** | 2a. Cuenta bloqueada: muestra "Cuenta bloqueada. Intente de nuevo en X minutos." |
| **Reglas de negocio** | RN-04 (bloqueo), RN-05 (JWT 24h), RN-09 |

---

**Caso de Uso: UC-03 — Iniciar Escaneo de Vulnerabilidades**

| **Campo** | **Descripción** |
|:---------|:----------------|
| **Nombre** | Iniciar Escaneo |
| **ID** | UC-03 |
| **Actor principal** | Usuario / Analista / Administrador |
| **Actor secundario** | Sistema (ejecución de módulos en background) |
| **Precondición** | El usuario está autenticado. No tiene ningún escaneo en estado "en progreso". |
| **Postcondición** | Un nuevo escaneo fue creado en la base de datos con estado "en progreso" y se ejecuta en background |
| **Flujo Principal** | 1. El usuario navega a la pantalla del escáner. 2. Ingresa la URL objetivo (ej: https://mi-proyecto.com). 3. Selecciona el nivel de profundidad (Básico/Estándar/Completo). 4. (Opcional — Analista+) Selecciona el stack tecnológico y configura timeout. 5. (Opcional) Habilita el análisis por IA. 6. Lee y acepta el aviso legal de uso autorizado. 7. Hace clic en "Iniciar Escaneo". 8. El sistema valida la URL (formato, no es IP privada). 9. El sistema verifica que no hay escaneo activo del usuario (RN-02). 10. El sistema crea un registro Scan en la base de datos (estado="pending"). 11. El sistema dispara la ejecución en background (BackgroundTasks). 12. El sistema retorna el scan_id al cliente con HTTP 202. 13. El frontend redirige al usuario a la pantalla de monitoreo con polling cada 3s. |
| **Flujo Alternativo A** | 8a. URL con formato inválido: HTTP 422 con descripción del error de validación. |
| **Flujo Alternativo B** | 8b. URL es IP privada: HTTP 400 "No se permiten escaneos a redes privadas". |
| **Flujo Alternativo C** | 9a. Ya hay escaneo activo: HTTP 409 "Ya tiene un escaneo en progreso". |
| **Reglas de negocio** | RN-01, RN-02, RN-06, RN-07, RN-08 |

---

**Caso de Uso: UC-04 — Ver Resultados de Escaneo**

| **Campo** | **Descripción** |
|:---------|:----------------|
| **Nombre** | Ver Resultados de Escaneo |
| **ID** | UC-04 |
| **Actor principal** | Usuario / Analista / Administrador |
| **Precondición** | Existe un escaneo completado asociado al usuario |
| **Postcondición** | El usuario visualiza las vulnerabilidades detectadas con su análisis completo |
| **Flujo Principal** | 1. El usuario accede al detalle del escaneo (desde historial o desde monitoreo al completarse). 2. El sistema carga las vulnerabilidades del escaneo desde la base de datos. 3. El sistema calcula y muestra el risk score global. 4. El sistema muestra la lista de vulnerabilidades ordenadas por severidad (Crítica → Informativa). 5. Cada vulnerabilidad muestra: nombre, módulo de origen, severidad (badge color), URL/parámetro afectado, descripción técnica, payload de prueba (PoC). 6. El usuario hace clic en una vulnerabilidad para ver su detalle completo. 7. Si el escaneo tuvo análisis IA habilitado, el usuario ve la pestaña "Análisis IA" con: CVSS score, vector, CWE, escenario de ataque, código de remediación para el stack del proyecto. 8. El usuario puede filtrar vulnerabilidades por severidad, módulo o estado. |
| **Flujo Alternativo A** | El escaneo no tiene vulnerabilidades: muestra "No se detectaron vulnerabilidades. Risk Score: 0". |
| **Flujo Alternativo B** | El análisis IA no está disponible para esa vulnerabilidad: muestra análisis del fallback local marcado como "Análisis Local". |
| **Reglas de negocio** | RN-09, RN-16, RN-17 |

---

**Caso de Uso: UC-09 — Gestionar Usuarios (Administración)**

| **Campo** | **Descripción** |
|:---------|:----------------|
| **Nombre** | Gestionar Usuarios |
| **ID** | UC-09 |
| **Actor principal** | Administrador |
| **Precondición** | El usuario tiene rol Administrador y está autenticado |
| **Postcondición** | El estado de los usuarios del sistema refleja los cambios realizados |
| **Flujo Principal** | 1. El administrador accede al Panel de Administración → sección Usuarios. 2. El sistema muestra la lista paginada de todos los usuarios. 3. El administrador puede: (a) Crear nuevo usuario con nombre/email/contraseña/rol; (b) Editar datos de un usuario existente; (c) Cambiar el rol de un usuario; (d) Bloquear/desbloquear cuenta manualmente; (e) Eliminar usuario con confirmación. 4. Cada acción se registra en AuditLog con la acción específica, usuario afectado e IP del administrador. |
| **Flujo Alternativo A** | Intentar eliminar el último administrador: el sistema rechaza con "No se puede eliminar el último administrador". |
| **Flujo Alternativo B** | Intentar asignarse a sí mismo un rol diferente a Admin: el sistema rechaza con "No puede cambiar su propio rol" (RN-18). |
| **Reglas de negocio** | RN-10, RN-18 |

---

### 3. Modelo Lógico

#### a) Análisis de Objetos

Los objetos principales del sistema y sus relaciones:

| **Objeto** | **Atributos principales** | **Responsabilidad** |
|:-----------|:--------------------------|:--------------------|
| **User** | id, name, email, hashed_password, role, is_active, is_locked, failed_login_attempts, locked_until, created_at | Representa a un usuario del sistema. Gestiona su autenticación, rol y estado de bloqueo. |
| **UserSession** | id, user_id, jti, ip_address, user_agent, is_active, created_at, expires_at | Representa una sesión JWT activa. Permite la revocación de tokens individuales. |
| **Scan** | id, user_id, target_url, status, depth, tech_stack, use_ai, risk_score, started_at, completed_at, current_module | Representa un escaneo de vulnerabilidades. Gestiona el ciclo de vida del proceso de análisis. |
| **Vulnerability** | id, scan_id, module_name, vuln_type, severity, url, parameter, evidence, description, solution, cvss_score, cwe_id, ai_analysis | Representa una vulnerabilidad detectada. Almacena todos los datos técnicos y el análisis IA. |
| **AuditLog** | id, user_id, action, ip_address, user_agent, endpoint, method, status_code, details, created_at | Representa una entrada del registro de auditoría. Inmutable. Rastrea cada acción relevante del sistema. |
| **Report** | id, scan_id, user_id, report_type, file_path, file_size, created_at | Representa un reporte generado. Gestiona la metadata de los archivos PDF/HTML/JSON. |
| **PasswordReset** | id, user_id, token, expires_at, is_used, created_at | Representa un token de recuperación de contraseña. Tiene vida útil de 1 hora y uso único. |

#### b) Diagrama de Actividades con Objetos

**Actividad: Proceso completo de escaneo**

```
[Usuario] ──► Ingresa URL y configuración
                    │
                    ▼
[Sistema] ──► Valida URL (formato, no privada)
                    │
                    ▼
[Scan:pending] ──► Se crea en BD con estado "pending"
                    │
                    ▼
[BackgroundTask] ──► Actualiza Scan.status = "in_progress"
                    │
                    ▼
         ┌──────────┴──────────────────────────┐
         │                                      │
         ▼                                      ▼
[Módulo Headers] ──────────► [Módulo SQLi] ────► ...  (13 módulos en paralelo controlado)
         │                        │
         ▼                        ▼
[Vulnerability:HIGH] ──► Se crea en BD para cada hallazgo
         │
         ▼
[DeepSeek AI] ──► Analiza vulnerabilidad → CVSS, CWE, escenario, código remediación
         │
         ▼
[Vulnerability] ──► Se actualiza con análisis IA
         │
         ▼
[Scan:completed] ──► risk_score calculado, completed_at registrado
         │
         ▼
[AuditLog] ──► Registra "scan_completed" con scan_id y risk_score
```

#### c) Diagrama de Secuencia

**Secuencia: UC-03 — Iniciar Escaneo**

```
Usuario     Frontend(Next.js)    API(FastAPI)    Scanner    DeepSeek    MySQL
   │               │                 │               │           │         │
   │──POST /scans──►               │               │           │         │
   │    {url, depth, stack, ai}    │               │           │         │
   │               │──────────────►│               │           │         │
   │               │               │──validate()───►           │         │
   │               │               │◄──valid───────            │         │
   │               │               │                           │         │
   │               │               │──INSERT Scan(pending)─────────────►│
   │               │               │◄──scan_id──────────────────────────│
   │               │               │                           │         │
   │               │               │──BackgroundTask(scan_id)──►         │
   │               │◄──202 {scan_id}│               │           │         │
   │◄──redirect /scans/{id}        │               │           │         │
   │               │               │               │           │         │
   │   [polling cada 3s]           │               │           │         │
   │──GET /scans/{id}──────────────►               │           │         │
   │               │               │               │──run_modules()      │
   │               │               │               │──UPDATE Scan(running)►│
   │               │               │               │──for each vuln:      │
   │               │               │               │──INSERT Vuln(...)───►│
   │               │               │               │──ai_analyze(vuln)──►│
   │               │               │               │◄──{cvss,cwe,code}──  │
   │               │               │               │──UPDATE Vuln(ai)────►│
   │               │               │               │──UPDATE Scan(done)──►│
   │               │◄──{status:done}│               │           │         │
   │◄──muestra resultados          │               │           │         │
```

#### d) Diagrama de Clases

```
┌─────────────────────────────────┐
│              User                │
├─────────────────────────────────┤
│ - id: int                        │
│ - name: str                      │
│ - email: str                     │
│ - hashed_password: str           │
│ - role: enum(admin,analyst,user) │
│ - is_active: bool                │
│ - is_locked: bool                │
│ - failed_login_attempts: int     │
│ - locked_until: datetime|null    │
│ - created_at: datetime           │
├─────────────────────────────────┤
│ + verify_password(pwd): bool     │
│ + generate_jwt(): str            │
│ + lock_account(): void           │
│ + unlock_account(): void         │
└──────────────┬──────────────────┘
               │ 1..*
               │
┌──────────────▼──────────────────┐    ┌─────────────────────────────────┐
│            Scan                  │    │          Vulnerability           │
├─────────────────────────────────┤    ├─────────────────────────────────┤
│ - id: int                        │    │ - id: int                        │
│ - user_id: int (FK)              │    │ - scan_id: int (FK)              │
│ - target_url: str                │    │ - module_name: str               │
│ - status: enum                   │    │ - vuln_type: str                 │
│ - depth: enum(basic/std/full)    │◄───┤ - severity: enum                 │
│ - tech_stack: str                │1.*│ - url: str                       │
│ - use_ai: bool                   │    │ - parameter: str                 │
│ - risk_score: int (0-100)        │    │ - evidence: str                  │
│ - started_at: datetime           │    │ - description: str               │
│ - completed_at: datetime|null    │    │ - solution: str                  │
│ - current_module: str            │    │ - cvss_score: float|null         │
├─────────────────────────────────┤    │ - cwe_id: str|null               │
│ + calculate_risk_score(): int    │    │ - ai_analysis: JSON|null         │
│ + mark_completed(): void         │    ├─────────────────────────────────┤
└─────────────────────────────────┘    │ + get_severity_label(): str      │
                                        └─────────────────────────────────┘

┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│          AuditLog                │    │             Report               │
├─────────────────────────────────┤    ├─────────────────────────────────┤
│ - id: int                        │    │ - id: int                        │
│ - user_id: int|null (FK)         │    │ - scan_id: int (FK)              │
│ - action: str                    │    │ - user_id: int (FK)              │
│ - ip_address: str                │    │ - report_type: enum(pdf/html/json│
│ - user_agent: str                │    │ - file_path: str                 │
│ - endpoint: str                  │    │ - file_size: int                 │
│ - method: str                    │    │ - created_at: datetime           │
│ - status_code: int               │    ├─────────────────────────────────┤
│ - details: JSON                  │    │ + generate_pdf(): bytes          │
│ - created_at: datetime           │    │ + generate_html(): str           │
├─────────────────────────────────┤    │ + generate_json(): dict          │
│ [READ ONLY — no update/delete]  │    └─────────────────────────────────┘
└─────────────────────────────────┘

┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│          UserSession             │    │         PasswordReset            │
├─────────────────────────────────┤    ├─────────────────────────────────┤
│ - id: int                        │    │ - id: int                        │
│ - user_id: int (FK)              │    │ - user_id: int (FK)              │
│ - jti: str (unique)              │    │ - token: str (unique)            │
│ - ip_address: str                │    │ - expires_at: datetime           │
│ - user_agent: str                │    │ - is_used: bool                  │
│ - is_active: bool                │    │ - created_at: datetime           │
│ - created_at: datetime           │    ├─────────────────────────────────┤
│ - expires_at: datetime           │    │ + is_valid(): bool               │
├─────────────────────────────────┤    │ + mark_used(): void              │
│ + revoke(): void                 │    └─────────────────────────────────┘
│ + revoke_all_user(): void        │
└─────────────────────────────────┘
```

<div style="page-break-after: always;"></div>

---

## CONCLUSIONES

1. VulnScan Pro cubre una necesidad real e insatisfecha en el ecosistema académico y de PYMES de Tacna: acceso gratuito a diagnósticos de seguridad web de nivel profesional, en español, con 13 módulos OWASP Top 10:2021 y análisis potenciado por IA.

2. Los **67 requerimientos funcionales** especificados en este documento abarcan de forma exhaustiva todas las capacidades del sistema: autenticación (RF-01 a RF-16), motor de escaneo (RF-17 a RF-42), análisis IA (RF-43 a RF-47), reportes (RF-48 a RF-52), dashboard (RF-53 a RF-58), administración (RF-59 a RF-63) e historial (RF-64 a RF-67).

3. Los **30 requerimientos no funcionales** garantizan que el sistema cumpla con los atributos de calidad ISO/IEC 25010 en todas sus dimensiones: seguridad (RNF-01, 07-09, 13, 15, 17, 20, 26-28, 30), rendimiento (RNF-02-03, 14, 19, 21-22), usabilidad (RNF-04, 16, 23), confiabilidad (RNF-05-06, 12), mantenibilidad (RNF-10, 18, 24-25, 29) y portabilidad (RNF-11).

4. Las **18 reglas de negocio** establecen restricciones claras y medibles que gobiernan el comportamiento del sistema, especialmente en aspectos críticos como el uso ético (RN-01), la seguridad de datos (RN-13, RN-14) y la integridad del audit log (RN-10).

5. Los modelos conceptual y lógico (diagramas de paquetes, casos de uso, secuencia, actividades y clases) proporcionan una visión completa de la arquitectura del sistema, facilitando la trazabilidad entre los requerimientos y su implementación técnica.

---

## RECOMENDACIONES

1. Ampliar los módulos de escaneo en versiones futuras para cubrir la OWASP API Security Top 10 (inyecciones en APIs REST, exceso de datos expuestos, autorizaciones rotas).

2. Implementar un sistema de notificaciones automáticas (email) al completarse un escaneo, especialmente cuando se detecten vulnerabilidades críticas.

3. Integrar VulnScan Pro con pipelines CI/CD (GitHub Actions, Jenkins) para que el escaneo se ejecute automáticamente en cada merge a la rama principal.

4. Desarrollar una biblioteca de payloads más extensa, actualizada regularmente con los últimos CVEs publicados, para mejorar la tasa de detección.

5. Considerar la implementación de un módulo de re-escaneo automático programado para detectar regresiones de seguridad en proyectos en producción.

---

## BIBLIOGRAFÍA

- OWASP Foundation (2021). *OWASP Top Ten 2021*. OWASP Foundation.
- OWASP Foundation (2021). *OWASP Testing Guide v4.2*. OWASP Foundation.
- FIRST.org (2019). *CVSS v3.1 Specification Document*. Forum of Incident Response and Security Teams.
- Mitre Corporation (2024). *CWE/SANS Top 25 Most Dangerous Software Weaknesses*. Mitre Corporation.
- ISO/IEC (2011). *ISO/IEC 25010:2011 — Systems and Software Quality Requirements and Evaluation (SQuaRE)*. International Organization for Standardization.
- Pressman, R. S. (2010). *Ingeniería del Software: Un Enfoque Práctico* (7ª ed.). McGraw-Hill.
- Sommerville, I. (2015). *Ingeniería de Software* (10ª ed.). Pearson Education.

---

## WEBGRAFÍA

- FastAPI Documentation. Recuperado de: https://fastapi.tiangolo.com/
- Next.js 16 Documentation. Recuperado de: https://nextjs.org/docs
- SQLAlchemy 2.0 Documentation. Recuperado de: https://docs.sqlalchemy.org/en/20/
- DeepSeek API Reference. Recuperado de: https://platform.deepseek.com/api-docs
- OWASP Top 10:2021. Recuperado de: https://owasp.org/Top10/
- OWASP Testing Guide v4.2. Recuperado de: https://owasp.org/www-project-web-security-testing-guide/
- Python-JOSE JWT Library. Recuperado de: https://python-jose.readthedocs.io/
- WeasyPrint PDF Generation. Recuperado de: https://weasyprint.org/
- Chart.js Documentation. Recuperado de: https://www.chartjs.org/docs/
- Ley N° 30096 — Ley de Delitos Informáticos. Recuperado de: https://www.gob.pe/institucion/congreso/normas-legales/242643-30096
- Ley N° 29733 — Ley de Protección de Datos Personales. Recuperado de: https://www.gob.pe/institucion/congreso/normas-legales/113939-29733

---

*Documento elaborado por: Calloticona Chambilla, Marymar D. y Ramos Loza, Mariela Estefany*
*Curso: Calidad y Pruebas de Software — Docente: Ing. Patrick Jose Cuadros Quiroga — UPT — 2026*
