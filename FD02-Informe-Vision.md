<center>

[comment]: <img src="./media/media/image1.png" style="width:1.088in;height:1.46256in" alt="escudo.png" />

![./media/media/image1.png](./media/logo-upt.png)

# UNIVERSIDAD PRIVADA DE TACNA

## FACULTAD DE INGENIERÍA

### Escuela Profesional de Ingeniería de Sistemas

**Curso:** Calidad y Pruebas de Software  
**Proyecto:** Analizador de Vulnerabilidades Web (ScanGuard UPT)  
**Docente:** Ing. Patrick Jose Cuadros Quiroga

**Integrantes:**

* Ramos Loza, Mariela Estefany (2023077478)
* Calloticona Chambilla, Marymar D. (2023076791)

**Tacna – Perú**  
**2026**

---

<div style="page-break-after: always;"></div>

## CONTROL DE VERSIONES

| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.0 | **M. Calloticona** | **M. Ramos** | | 28/03/2026 | Versión Original |
| 1.1 | **M. Calloticona** | **M. Ramos** | | 04/04/2026 | Extensión de métricas ISO 25010 e Introducción detallada |

---

<div style="page-break-after: always;"></div>


**INDICE GENERAL**

[1.	Introducción](#_Toc52661346)

1.1	Propósito

1.2	Alcance

1.3	Definiciones, Siglas y Abreviaturas

1.4	Referencias

1.5	Visión General

[2.	Posicionamiento](#_Toc52661347)

2.1	Oportunidad de negocio

2.2	Definición del problema

[3.	Descripción de los interesados y usuarios](#_Toc52661348)

3.1	Resumen de los interesados

3.2	Resumen de los usuarios

3.3	Entorno de usuario

3.4	Perfiles de los interesados

3.5	Perfiles de los Usuarios

3.6	Necesidades de los interesados y usuarios

[4.	Vista General del Producto](#_Toc52661349)

4.1	Perspectiva del producto

4.2	Resumen de capacidades

4.3	Suposiciones y dependencias

4.4	Costos y precios

4.5	Licenciamiento e instalación

[5.	Características del producto](#_Toc52661350)

[6.	Restricciones](#_Toc52661351)

[7.	Rangos de calidad](#_Toc52661352)

[8.	Precedencia y Prioridad](#_Toc52661353)

[9.	Otros requerimientos del producto](#_Toc52661354)

b) Estandares legales

c) Estandares de comunicación	](#_toc394513800)37

d) Estandaraes de cumplimiento de la plataforma	](#_toc394513800)42

e) Estandaraes de calidad y seguridad	](#_toc394513800)42

[CONCLUSIONES](#_Toc52661355)

[RECOMENDACIONES](#_Toc52661356)

[BIBLIOGRAFIA](#_Toc52661357)

[WEBGRAFIA](#_Toc52661358)


<div style="page-break-after: always; visibility: hidden"></div>

**<u>Informe de Visión</u>**
<div style="page-break-after: always; visibility: hidden"></div>


**1. Introducción**

**1.1 Propósito**

El presente documento define los objetivos estratégicos, capacidades
técnicas y alcance del sistema ScanGuard, una herramienta de análisis
dinámico de seguridad (DAST) desarrollada en el marco del curso de
Calidad y Pruebas de Software de la Escuela Profesional de Ingeniería de
Sistemas de la Universidad Privada de Tacna.

Este documento sirve como acuerdo de visión entre el equipo de
desarrollo y los interesados del proyecto, asegurando que el software
cumpla con los estándares de seguridad web establecidos por el OWASP Top
10 y los criterios de calidad definidos por la norma ISO/IEC 25010.

**1.2 Alcance**

ScanGuard es una aplicación web que realiza auditorías de seguridad
dinámica sobre URLs objetivo accesibles vía HTTP/HTTPS. El sistema
analiza:

-   Cabeceras HTTP de seguridad (CSP, HSTS, X-Frame-Options,
    X-Content-Type-Options).

-   Vulnerabilidades incluidas en el OWASP Top 10: SQL Injection y
    Cross-Site Scripting (XSS).

-   Configuración de certificados SSL/TLS: validez, protocolo y fecha de
    vencimiento.

-   Atributos de seguridad en cookies: Secure, HttpOnly y SameSite.

El sistema no realiza ataques intrusivos que afecten la disponibilidad
del servicio objetivo, limitándose a pruebas no destructivas sobre
aplicaciones en entornos de desarrollo o preproducción.

**1.3 Definiciones, Siglas y Abreviaturas**

-   DAST: Dynamic Application Security Testing -- pruebas de seguridad
    sobre la aplicación en ejecución.

-   OWASP: Open Web Application Security Project -- organización global
    de referencia en seguridad web.

-   SQLi: SQL Injection -- inyección de código SQL en parámetros de
    entrada.

-   XSS: Cross-Site Scripting -- inyección de scripts maliciosos en
    páginas web.

-   CSP: Content Security Policy -- cabecera que controla los recursos
    que el navegador puede cargar.

-   HSTS: HTTP Strict Transport Security -- cabecera que fuerza el uso
    de HTTPS.

-   SSL/TLS: Secure Sockets Layer / Transport Layer Security --
    protocolos de cifrado de comunicaciones.

-   ISO/IEC 25010: Norma internacional que define el modelo de calidad
    para productos de software.

**1.4 Referencias**

-   OWASP Foundation. (2025). OWASP Top 10 Project.
    https://owasp.org/Top10/

-   ISO/IEC 25010:2011. Systems and software engineering -- System and
    software quality models.

-   Ley N° 30096 -- Ley de Delitos Informáticos del Perú.

-   FastAPI Documentation. (2024). https://fastapi.tiangolo.com

-   React Documentation. (2024). https://react.dev

**1.5 Visión General**

ScanGuard es una herramienta automatizada de código abierto que permite
a ingenieros de QA y desarrolladores identificar riesgos de seguridad de
forma proactiva, antes del despliegue a producción. La arquitectura está
compuesta por un frontend en React con Vite y Tailwind CSS, y un backend
en Python con FastAPI, comunicados mediante una API REST. Los resultados
se presentan en un dashboard con semáforo de riesgo y pueden exportarse
como reportes en PDF o JSON para su uso en auditorías académicas y
técnicas.

**2. Posicionamiento**

**2.1 Oportunidad de negocio**

La creciente digitalización de servicios en Tacna y el Perú ha
incrementado significativamente la superficie de ataque de las
aplicaciones web locales. Sin embargo, las herramientas de seguridad
profesionales (Burp Suite Professional, Nessus, Acunetix) tienen costos
de licenciamiento elevados que las hacen inaccesibles para estudiantes,
desarrolladores independientes y pequeñas empresas de la región.

ScanGuard cubre esa brecha ofreciendo una solución gratuita, de alto
rendimiento y orientada a las vulnerabilidades más prevalentes según el
OWASP Top 10, proporcionando un punto de entrada accesible a la
seguridad aplicativa sin requerir infraestructura especializada.

**2.2 Definición del problema**

Las aplicaciones web desarrolladas en entornos académicos y de pequeñas
empresas suelen desplegarse con configuraciones de seguridad
deficientes: cabeceras HTTP ausentes, certificados vencidos, cookies sin
flags de protección y formularios susceptibles a inyección de código.
Esta situación expone datos sensibles de ciudadanos, estudiantes y
organizaciones a ataques automatizados.

El problema central es la ausencia de una instancia de verificación de
seguridad entre el desarrollo y el despliegue. ScanGuard actúa como esa
instancia, automatizando las pruebas más críticas del ciclo de vida del
desarrollo seguro (S-SDLC).

**3. Descripción de los Interesados y Usuarios**

**3.1 Resumen de los interesados**

  ---------------- ----------------- -------------------------------------
  **Interesado**   **Rol**           **Interés principal**

  Docente del      Supervisor        Evaluar la calidad técnica del
  curso            académico         sistema y su alineación con
                                     estándares de seguridad.

  Estudiantes EPIS Usuarios finales  Contar con una herramienta práctica
                                     para identificar vulnerabilidades en
                                     sus propios proyectos web.

  Auditores de TI  Revisores         Obtener reportes técnicos detallados
                   externos          que permitan validar la seguridad de
                                     aplicaciones desplegadas.

  Equipo de        Desarrolladoras   Construir un sistema funcional,
  desarrollo                         mantenible y alineado con buenas
                                     prácticas de ingeniería de software.
  ---------------- ----------------- -------------------------------------

**3.2 Resumen de los usuarios**

Los usuarios directos del sistema son ingenieros de QA y desarrolladores
fullstack con conocimientos básicos en protocolos de red y seguridad
web. Estos usuarios interactúan con el frontend para iniciar escaneos,
revisar resultados y exportar reportes. No se requiere experiencia
avanzada en ciberseguridad para operar el sistema.

**3.3 Entorno de usuario**

El sistema es accesible desde cualquier navegador web moderno (Chrome,
Firefox, Edge) en entornos de escritorio. No requiere instalación local
por parte del usuario final. El backend se ejecuta en un servidor con
acceso a internet para poder alcanzar las URLs objetivo durante el
escaneo.

**3.4 Perfiles de los interesados**

**Docente del curso**

-   Nombre: Ing. Patrick Jose Cuadros Quiroga

-   Interés: Evaluar la calidad técnica del sistema y su alineación con
    los estándares del curso.

-   Criterio de éxito: El sistema cubre al menos cinco categorías del
    OWASP Top 10 con resultados verificables.

**Auditores de TI externos**

-   Interés: Obtener reportes técnicos exportables que puedan adjuntarse
    a procesos de auditoría formal.

-   Criterio de éxito: Los reportes PDF son claros, completos y
    contienen recomendaciones de remediación accionables.

**3.5 Perfiles de los Usuarios**

**Ingeniero de QA / Estudiante avanzado**

-   Conocimientos: Protocolos HTTP/HTTPS, fundamentos de seguridad web,
    uso de herramientas de testing.

-   Frecuencia de uso: Alta -- previo a cada ciclo de despliegue o
    entrega de proyecto.

-   Objetivo: Identificar y corregir vulnerabilidades antes de que el
    software llegue a producción.

**Desarrollador fullstack**

-   Conocimientos: Desarrollo web frontend y backend, nociones básicas
    de seguridad.

-   Frecuencia de uso: Media -- durante las etapas de integración y
    pruebas del proyecto.

-   Objetivo: Validar que su implementación no introduce
    vulnerabilidades conocidas.

**3.6 Necesidades de los interesados y usuarios**

  ------------------ -------------------------- --------------------------
  **Necesidad**      **Problema actual**        **Solución propuesta**

  Identificar        Los desarrolladores no     ScanGuard realiza análisis
  vulnerabilidades   cuentan con herramientas   DAST automático sobre la
  antes del          accesibles para auditar su URL del proyecto sin
  despliegue         código antes de            requerir instalación
                     publicarlo.                local.

  Reportes           Los reportes de            El sistema genera reportes
  comprensibles para herramientas existentes    con lenguaje claro,
  no expertos        (como Burp Suite) son      niveles de severidad
                     complejos y requieren      visuales y recomendaciones
                     experiencia avanzada.      de remediación.

  Historial y        No existe un registro      El módulo de historial
  trazabilidad       histórico que permita      almacena escaneos pasados
                     comparar la seguridad del  y permite comparar
                     sistema entre versiones.   resultados entre fechas.
  ------------------ -------------------------- --------------------------

**4. Vista General del Producto -- Estudio de Factibilidad**

**4.1 Perspectiva del producto**

ScanGuard es una herramienta independiente con arquitectura
cliente-servidor. El frontend (React + Vite + Tailwind CSS) se comunica
con el backend (Python + FastAPI) mediante una API REST. El backend
orquesta los módulos de escaneo y persiste los resultados en una base de
datos SQLite. El sistema es autónomo y no depende de servicios de
terceros para ejecutar el análisis.

**4.2 Resumen de capacidades**

-   Análisis dinámico de aplicaciones web (DAST) sin agente instalado en
    el objetivo.

-   Detección de vulnerabilidades del OWASP Top 10 mediante cinco
    módulos especializados.

-   Presentación de resultados con clasificación de severidad en cuatro
    niveles: Bajo, Medio, Alto y Crítico.

-   Exportación de reportes en formato PDF y JSON para uso en
    auditorías.

-   Almacenamiento del historial de escaneos con trazabilidad por fecha
    y URL.

**4.3 Suposiciones y dependencias**

-   El servidor backend tiene acceso a internet para alcanzar las URLs
    objetivo durante el escaneo.

-   El usuario tiene permisos legales sobre la aplicación que desea
    analizar.

-   Las URLs objetivo responden mediante protocolo HTTP o HTTPS.

-   El entorno de despliegue cuenta con Python 3.11+ y Node.js 18+
    instalados.

**4.4 Costos y precios**

El proyecto es de desarrollo académico con costo de licenciamiento cero.
Todo el stack tecnológico utilizado (React, FastAPI, Python, SQLite) es
de código abierto. Los costos asociados se limitan al tiempo de
desarrollo del equipo y al uso de infraestructura de hosting gratuita
(Render, Railway o similares) para el despliegue académico.

**4.5 Licenciamiento e instalación**

El sistema se distribuye bajo Licencia Abierta MIT, lo que permite su
uso, modificación y distribución libre, siempre que se mantenga el aviso
de copyright original. La instalación se realiza clonando el repositorio
de GitHub del proyecto y ejecutando los comandos de inicialización del
frontend y backend documentados en el README.md del repositorio.

**5. Características del Producto**

La siguiente tabla describe las características funcionales del sistema
ScanGuard, ordenadas por prioridad de implementación:

  -------- -------------------- ---------------------------------------- ---------------
  **ID**   **Característica**   **Descripción**                          **Prioridad**

  F-01     Escaneo de cabeceras Detecta cabeceras de seguridad faltantes Alta
           HTTP                 o mal configuradas (CSP, HSTS,           
                                X-Frame-Options, X-Content-Type).        

  F-02     Detección de SQL     Prueba parámetros de formularios con     Alta
           Injection            payloads comunes de SQLi para            
                                identificar puntos de inyección.         

  F-03     Detección de XSS     Inyecta scripts de prueba en campos de   Alta
                                entrada para detectar Cross-Site         
                                Scripting reflejado.                     

  F-04     Validación SSL/TLS   Verifica la validez del certificado,     Alta
                                protocolo utilizado y fecha de           
                                vencimiento.                             

  F-05     Análisis de flags de Revisa si las cookies carecen de los     Media
           cookies              atributos Secure, HttpOnly o SameSite.   

  F-06     Dashboard de         Presenta los hallazgos con un semáforo   Alta
           resultados           de riesgo: Bajo, Medio, Alto y Crítico.  

  F-07     Exportación de       Genera reportes en formato PDF y JSON    Media
           reportes             para su uso en auditorías y              
                                documentación.                           

  F-08     Historial de         Almacena los resultados de escaneos      Baja
           escaneos             anteriores para comparación y            
                                trazabilidad.                            
  -------- -------------------- ---------------------------------------- ---------------

**6. Restricciones**

**6.1 Restricciones funcionales**

-   El sistema no ejecuta ataques de denegación de servicio (DoS/DDoS)
    ni pruebas que afecten la disponibilidad del objetivo.

-   El análisis está limitado a aplicaciones web accesibles mediante
    protocolo HTTP o HTTPS. No cubre aplicaciones de escritorio, APIs no
    web ni protocolos propietarios.

-   Las pruebas de SQL Injection y XSS son de tipo caja negra
    (black-box) sobre parámetros visibles; no realizan análisis de
    código fuente.

-   El sistema no garantiza la detección del 100% de las
    vulnerabilidades existentes; los resultados deben interpretarse como
    un punto de partida para una auditoría más profunda.

**6.2 Restricciones legales y éticas**

-   El uso del sistema sobre aplicaciones sin autorización expresa del
    propietario constituye una infracción a la Ley N° 30096 de Delitos
    Informáticos del Perú y a normativas internacionales equivalentes.

-   El sistema incluye un aviso legal en la interfaz que recuerda al
    usuario su responsabilidad sobre el uso ético de la herramienta.

**6.3 Restricciones técnicas**

-   El tiempo máximo de escaneo por URL está limitado a 90 segundos para
    evitar bloqueos por parte del servidor objetivo.

-   No se realizan escaneos en paralelo sobre la misma URL para evitar
    sobrecargar el objetivo.

**7. Rangos de Calidad**

El sistema se evaluará bajo la norma ISO/IEC 25010, específicamente en
las siguientes características y subcaracterísticas de calidad del
producto:

  ---------------- ----------------------------- -------------------------
  **Atributo de    **Criterio de aceptación**    **Referencia ISO 25010**
  calidad**                                      

  Eficiencia de    Un escaneo completo no debe   ISO 25010 -
  desempeño        superar los 60 segundos para  Comportamiento temporal
                   URLs estándar.                

  Fiabilidad       El sistema debe completar el  ISO 25010 - Madurez
                   95% de los escaneos sin       
                   errores fatales.              

  Seguridad        Las comunicaciones            ISO 25010 -
  interna          frontend-backend deben estar  Confidencialidad
                   cifradas mediante HTTPS.      

  Usabilidad       Un usuario con conocimientos  ISO 25010 - Capacidad de
                   básicos de redes debe operar  aprendizaje
                   el sistema sin capacitación   
                   previa.                       

  Mantenibilidad   El código debe estar          ISO 25010 -
                   documentado y modularizado    Modificabilidad
                   para facilitar la             
                   incorporación de nuevos       
                   módulos de escaneo.           
  ---------------- ----------------------------- -------------------------

**8. Precedencia y Prioridad**

La siguiente tabla define el orden de implementación de las
funcionalidades del sistema, priorizando las capacidades de detección de
vulnerabilidades críticas por encima de las características de reporte y
gestión:

  -------- ------------------------------- --------------- -----------------------
  **\#**   **Funcionalidad**               **Prioridad**   **Entrega estimada**

  1        Módulos de escaneo OWASP (SQLi, Critica         Sprint 1-2
           XSS, Headers)                                   

  2        Validación SSL/TLS y análisis   Alta            Sprint 2
           de cookies                                      

  3        Dashboard de resultados con     Alta            Sprint 3
           semáforo de riesgo                              

  4        Exportación de reportes         Media           Sprint 3
           PDF/JSON                                        

  5        Historial de escaneos y         Baja            Sprint 4
           trazabilidad                                    
  -------- ------------------------------- --------------- -----------------------

La prioridad máxima es la correcta detección de vulnerabilidades
críticas, ya que constituye el valor central del sistema. La integridad
y confiabilidad de los resultados reportados no puede ser comprometida
en favor de funcionalidades secundarias.

**9. Otros Requisitos del Producto**

**a) Estándares legales**

-   El sistema debe cumplir con la Ley N° 30096 -- Ley de Delitos
    Informáticos del Perú, asegurando que solo se analicen sistemas con
    autorización del propietario.

-   El tratamiento de datos derivados de los escaneos debe alinearse con
    la Ley N° 29733 de Protección de Datos Personales del Perú.

**b) Estándares de comunicación**

-   Toda comunicación entre el frontend y el backend debe realizarse
    mediante HTTPS en entornos de producción.

-   La API REST debe seguir las convenciones de diseño RESTful y
    documentarse automáticamente mediante Swagger UI (integrado en
    FastAPI).

**c) Estándares de cumplimiento de la plataforma**

-   El backend debe ser compatible con Python 3.11 o superior.

-   El frontend debe compilar correctamente con Node.js 18 LTS o
    superior y Vite 5.x.

-   El sistema debe funcionar correctamente en los navegadores Chrome
    120+, Firefox 120+ y Edge 120+.

**d) Estándares de calidad y seguridad**

-   El código fuente debe seguir los estándares PEP 8 para Python y las
    convenciones de ESLint con Airbnb Style Guide para JavaScript/React.

-   Las dependencias del proyecto deben auditarse con herramientas
    automáticas (pip audit, npm audit) antes de cada entrega.

-   El repositorio del proyecto debe incluir un archivo README.md con
    instrucciones claras de instalación, configuración y ejecución.

**Conclusiones**

El proyecto ScanGuard se establece como una solución técnica viable que
eleva el estándar de calidad en el desarrollo de software dentro de la
Universidad Privada de Tacna. A través de una arquitectura moderna
(React + FastAPI) y módulos de escaneo alineados con el OWASP Top 10, el
sistema provee a estudiantes y profesionales de QA una herramienta
accesible para identificar vulnerabilidades web antes del despliegue a
producción.

El documento de visión presentado define con claridad el alcance
funcional, los interesados, las características priorizadas y los
estándares de calidad bajo los cuales será evaluado el sistema,
garantizando un desarrollo alineado con las expectativas académicas y
las buenas prácticas de ingeniería de software.

**Recomendaciones**

Se recomienda a los futuros desarrolladores y colaboradores del proyecto
considerar las siguientes acciones para maximizar el impacto y la
sostenibilidad de ScanGuard:

-   Integrar el motor de escaneo en pipelines de CI/CD (GitHub Actions,
    GitLab CI) para automatizar las pruebas de seguridad en cada push de
    código, transformando ScanGuard en una herramienta de DevSecOps.

-   Ampliar la cobertura de análisis incorporando módulos adicionales
    del OWASP Top 10, como detección de componentes con vulnerabilidades
    conocidas (A06:2021) y fallas de control de acceso (A01:2021).

-   Establecer un proceso de actualización periódica de los payloads de
    prueba utilizados por los módulos de SQLi y XSS, para mantener la
    efectividad del sistema frente a nuevas técnicas de evasión.

-   Considerar el despliegue del sistema en infraestructura cloud (AWS
    Free Tier, Google Cloud o Azure for Students) para facilitar el
    acceso de toda la comunidad universitaria sin dependencia de
    instalación local.

**Bibliografía**

OWASP Foundation. (2025). OWASP Top 10 Project. Recuperado de
https://owasp.org/Top10/

ISO/IEC 25010:2011. (2011). Systems and software engineering -- System
and software quality models. International Organization for
Standardization.

McKinley, T. (2022). Web Application Security: Exploitation and
Countermeasures for Modern Web Applications. O\'Reilly Media.

Microsoft. (2024). .NET 8 Security Guide. Recuperado de
https://learn.microsoft.com/en-us/dotnet/core/security/

**Webgrafía**

FastAPI Documentation. (2024). FastAPI Framework. Recuperado de
https://fastapi.tiangolo.com

React Documentation. (2024). React -- The Library for Web and Native
User Interfaces. Recuperado de https://react.dev

Tailwind CSS Documentation. (2024). Recuperado de
https://tailwindcss.com/docs

Python Software Foundation. (2024). Python 3.11 Documentation.
Recuperado de https://docs.python.org/3.11/

Ley N° 30096 -- Ley de Delitos Informáticos. (2013). Congreso de la
República del Perú. Recuperado de
https://www.gob.pe/institucion/congreso-de-la-republica/normas-legales/139699-30096

