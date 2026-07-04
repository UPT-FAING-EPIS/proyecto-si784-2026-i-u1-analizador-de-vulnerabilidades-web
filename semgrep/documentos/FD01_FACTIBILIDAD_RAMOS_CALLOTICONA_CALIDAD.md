![C:\Users\EPIS\Documents\upt.png](media/image1.png){width="1.6949004811898514in" height="2.2815977690288713in"}

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERÍA**

**Escuela Profesional de Ingeniería de Sistemas**

**Generador de Base de datos**

Curso: *Calidad y Pruebas de Software*

*Proyecto : Analizador de vulnerabilidades web*

Docente: Ing. Patrick Jose Cuadros Quiroga

Integrantes:

**Ramos Loza, Mariela Estefany (2023077478)**

**Calloticona Chambilla, Marymar D. (2023076791)**

**Tacna -- Perú**

***2025***

[Analizador de vulnerabilidades web]{.mark}

Informe de Factibilidad

Versión *1.0*

| CONTROL DE VERSIONES |           |              |              |            |                  |
|----------------------|-----------|--------------|--------------|------------|------------------|
| Versión              | Hecha por | Revisada por | Aprobada por | Fecha      | Motivo           |
| 1.0                  |           |              |              | 28/03/2026 | Versión Original |

**ÍNDICE GENERAL**

[**1. DESCRIPCIÓN DEL PROYECTO 4**](#descripción-del-proyecto)

> [1.1. NOMBRE DEL PROYECTO 4](#nombre-del-proyecto)
>
> [1.2. DURACIÓN DEL PROYECTO 4](#duración-del-proyecto)
>
> [1.3. OBJETIVOS 5](#objetivos)
>
> [1.3.1. OBJETIVO GENERAL 5](#objetivo-general)
>
> [1.3.2. OBJETIVOS ESPECÍFICOS 5](#objetivos-específicos)

[**2. RIESGOS 6**](#riesgos)

[**3. ANÁLISIS DE LA SITUACIÓN ACTUAL 6**](#análisis-de-la-situación-actual)

> [3.1. PLANTEAMIENTO DEL PROBLEMA 6](#planteamiento-del-problema)
>
> [4. CONSIDERACIONES DE HARDWARE Y SOFTWARE 6](#consideraciones-de-hardware-y-software)
>
> [4.1. Stack Tecnológico Completo 6](#stack-tecnológico-completo)

[**5. VIABILIDAD TÉCNICA 8**](#viabilidad-técnica)

> [5.1. Medidas de Seguridad Implementadas 8](#medidas-de-seguridad-implementadas)
>
> [6.1. FACTIBILIDAD TÉCNICA 9](#factibilidad-técnica)
>
> [6.2. FACTIBILIDAD ECONÓMICA 9](#factibilidad-económica)
>
> [6.2.1. Definición de costos 10](#definición-de-costos)
>
> [6.2.2. Costos Operativos durante el desarrollo 10](#costos-operativos-durante-el-desarrollo)
>
> [6.2.3. Costos del Stack Tecnológico y Ambiente 11](#costos-del-stack-tecnológico-y-ambiente)
>
> [6.2.4. Inversión en activos 12](#inversión-en-activos)
>
> [6.2.5. Resumen de Inversión del Total del Proyecto 12](#resumen-de-inversión-del-total-del-proyecto)
>
> [6.3. FACTIBILIDAD LEGAL 13](#factibilidad-legal)
>
> [6.4. FACTIBILIDAD SOCIAL 14](#factibilidad-social)
>
> [6.5. FACTIBILIDAD AMBIENTAL 14](#factibilidad-ambiental)

[**7. ANÁLISIS FINANCIERO 15**](#análisis-financiero)

> [7.1. JUSTIFICACIÓN DE LA INVERSIÓN 15](#justificación-de-la-inversión)
>
> [7.2. BENEFICIOS DEL PROYECTO 15](#beneficios-del-proyecto)
>
> [7.3. CRITERIOS DE INVERSIÓN 16](#criterios-de-inversión)
>
> [7.3.1. RELACIÓN BENEFICIO/COSTO (B/C) 16](#relación-beneficiocosto-bc)
>
> [7.3.2. VALOR ACTUAL NETO (VAN) 16](#valor-actual-neto-van)
>
> [7.3.3. TASA INTERNA DE RETORNO (TIR) 16](#tasa-interna-de-retorno-tir)

[**8. CONCLUSIONES 16**](#conclusiones)

# **DESCRIPCIÓN DEL PROYECTO**

## NOMBRE DEL PROYECTO

> [Sistema de Auditoría y Análisis de Seguridad Web]{.mark}

## DURACIÓN DEL PROYECTO

- **Tiempo total de desarrollo:** 1mes (4 semanas)

| **Fase**                             | **Duración** | **Actividades Clave**                                                                                                 |
|--------------------------------------|--------------|-----------------------------------------------------------------------------------------------------------------------|
| **Fase 1: Definición y Setup**       | **Semana 1** | Redacción de Visión/Factibilidad. Configuración de proyectos Angular y C# (.NET 8). Definición del JSON de respuesta. |
| **Fase 2: El \"Cerebro\" (Backend)** | **Semana 2** | Programación del servicio de escaneo en C#. Análisis de Headers y detección de errores SSL. Pruebas con Postman.      |
| **Fase 3: La Interfaz (Frontend)**   | **Semana 3** | Creación del formulario de URL y tabla de resultados en Angular. Conexión mediante HttpClient al Backend.             |
| **Fase 4: Pulido y Cierre**          | **Semana 4** | Manejo de errores (URL no válida). Pruebas finales de integración. Redacción de conclusiones y entrega del informe.   |

## OBJETIVOS

### OBJETIVO GENERAL

> Desarrollar una aplicación web integral que permita a administradores y desarrolladores identificar brechas de seguridad y configuraciones erróneas en sitios web mediante escaneos pasivos y activos.

### OBJETIVOS ESPECÍFICOS

1.  **Objetivos Técnicos**

- Implementar un motor de escaneo en C# capaz de analizar cabeceras HTTP y estructuras HTML.

- Desarrollar una interfaz de usuario en Angular que visualice los hallazgos de forma intuitiva.

- Categorizar las vulnerabilidades según su nivel de criticidad (Bajo, Medio, Alto).

- Generar reportes técnicos resumidos con recomendaciones de mitigación.

# **RIESGOS**

- **Bloqueo de IPs:** Que los servidores objetivo bloqueen las peticiones del analizador.

- **Falsos Positivos:** Identificar vulnerabilidades donde no las hay.

- **Complejidad Legal:** Uso indebido de la herramienta en sitios sin autorización.

# **ANÁLISIS DE LA SITUACIÓN ACTUAL**

## PLANTEAMIENTO DEL PROBLEMA

> [En la actualidad, las PYMES y desarrolladores independientes carecen de herramientas de seguridad accesibles y fáciles de interpretar. Las soluciones existentes son costosas o requieren conocimientos avanzados de ciberseguridad, lo que deja a muchas aplicaciones web expuestas a ataques comunes como XSS o secuestro de clics (Clickjacking).]{.mark}

## CONSIDERACIONES DE HARDWARE Y SOFTWARE

### Stack Tecnológico Completo

| **Tecnología a Aplicar** | **Versión** | **Propósito**                                                         | **Costo**            |
|--------------------------|-------------|-----------------------------------------------------------------------|----------------------|
| **Angular**              | 17.x / 18.x | Framework para la interfaz de usuario (Frontend) y gestión de estado. | \$0 (Open Source)    |
| **C# / .NET**            | 8.0 (LTS)   | Lenguaje y framework para el motor de escaneo y API (Backend).        | \$0 (Open Source)    |
| **ASP.NET Core Web API** | 8.0         | Creación de endpoints RESTful para comunicación con el Frontend.      | \$0 (Open Source)    |
| **TypeScript**           | 5.x         | Lenguaje de programación para el desarrollo robusto en Angular.       | \$0 (Open Source)    |
| **HttpClient (.NET)**    | Nativo      | Realización de peticiones asíncronas a las URLs objetivo.             | \$0 (Incluido)       |
| **HtmlAgilePack**        | 1.11.x      | Librería de C# para parsear y analizar el DOM/HTML de los sitios.     | \$0 (MIT License)    |
| **Tailwind CSS**         | 3.x         | Framework de utilidades CSS para un diseño responsivo y moderno.      | \$0 (Open Source)    |
| **Visual Studio Code**   | Latest      | Entorno de desarrollo (IDE) principal para ambos lenguajes.           | \$0 (Gratis)         |
| **Git / GitHub**         | 2.x         | Control de versiones y respaldo del código fuente.                    | \$0 (Plan Free)      |
| **Azure App Service**    | Free Tier   | Hosting inicial para pruebas de concepto y demostración.              | \$0 (Nivel Gratuito) |

# **VIABILIDAD TÉCNICA**

## Medidas de Seguridad Implementadas

- Sanitización de Entradas: Evitar que el usuario inyecte código malicioso en la barra de búsqueda del analizador.

- Timeouts: Limitar el tiempo de espera de las peticiones para evitar consumo excesivo de recursos (DoS accidental).

| **Criterio**                 | **Puntuación (1-5)** | **Justificación**                                                             |
|------------------------------|----------------------|-------------------------------------------------------------------------------|
| Disponibilidad de Tecnología | 5                    | .NET y Angular son tecnologías maduras y gratuitas.                           |
| Curva de Aprendizaje         | 4                    | Requiere dominio intermedio de C# y TypeScript.                               |
| Escalabilidad                | 4                    | La arquitectura desacoplada permite añadir más tests de seguridad fácilmente. |

1.  **VIABILIDAD OPERATIVA**

## FACTIBILIDAD TÉCNICA

> modernos y gratuitos (Next.js, Supabase, etc.) que reducen costos y facilitan escalabilidad. Además, el equipo cuenta con los conocimientos necesarios en desarrollo web y bases de datos.El proyecto es técnicamente factible gracias al uso de frameworks

## FACTIBILIDAD ECONÓMICA

> La factibilidad económica de **Analizador de vulnerabilidades web** se evalúa bajo un modelo de desarrollo de software de bajo costo, orientado a la eficiencia de recursos y el uso de tecnologías abiertas. Dado que es un proyecto de investigación académica, no requiere una inversión de capital inicial (CAPEX) externa, sino una gestión optimizada de los recursos operativos existentes.

### Definición de costos

> El proyecto se clasifica como de **Inversión Mínima**, ya que el stack tecnológico elegido (Angular y .NET 8) no requiere el pago de licencias comerciales. Los costos se dividen en operativos y de infraestructura digital.

### Costos Operativos durante el desarrollo

> Estos representan los gastos mensuales necesarios para mantener el entorno de desarrollo activo durante las 4 semanas de ejecución.

| **Ítem**                                     | **Cantidad (Mes)** | **Costo Unitario (S/.)** | **Costo Total (S/.)** |
|----------------------------------------------|--------------------|--------------------------|-----------------------|
| Energía Eléctrica (Consumo PC de desarrollo) | 1                  | S/. 30.00                | S/. 30.00             |
| Servicio de Internet (Fibra Óptica 200 Mbps) | 1                  | S/. 35.00\*              | S/. 35.00             |
| **Total Costos Operativos**                  |                    |                          | **S/. 65.00**         |

### Costos del Stack Tecnológico y Ambiente

> Se detalla la inversión en herramientas de software para garantizar que el presupuesto de licencias se mantenga en cero.

| **Recurso / Software**       | **Proveedor** | **Tipo de Licencia** | **Costo (S/.)** |
|------------------------------|---------------|----------------------|-----------------|
| Framework Angular            | Google        | Open Source (MIT)    | S/. 0.00        |
| .NET 8 SDK / C#              | Microsoft     | Open Source (MIT)    | S/. 0.00        |
| IDE Visual Studio Code       | Microsoft     | Gratuita             | S/. 0.00        |
| Repositorio GitHub           | GitHub        | Plan Free            | S/. 0.00        |
| Hosting Azure Static Web     | Microsoft     | Free Tier            | S/. 0.00        |
| **Total Costos de Ambiente** |               |                      | **S/. 0.00**    |

### Inversión en activos  {#inversión-en-activos}

> El hardware es propiedad del equipo de desarrollo, por lo que se considera una inversión ya realizada (costo hundido), pero necesaria para la factibilidad.

| **Activo**                  | **Especificación**                 | **Estado**     |
|-----------------------------|------------------------------------|----------------|
| **Laptop/PC de Desarrollo** | **CPU i5/i7, 16GB RAM, SSD 512GB** | **Disponible** |
| **Monitor Externo**         | **24\" Full HD**                   | **Disponible** |

### Resumen de Inversión del Total del Proyecto  {#resumen-de-inversión-del-total-del-proyecto}

| **Categoría**                      | **Monto Estimado (S/.)** |
|------------------------------------|--------------------------|
| **Costos Operativos (1 mes)**      | **S/. 65.00**            |
| **Costos de Software y Licencias** | **S/. 0.00**             |
| **Imprevistos (5%)**               | **S/. 3.25**             |
| **INVERSIÓN TOTAL REQUERIDA**      | **S/. 68.25**            |

## FACTIBILIDAD LEGAL

> El desarrollo y distribución de **Analizador de vulnerabilidades web** se rige bajo un marco de estricta legalidad, asegurando que la herramienta no sea considerada software malicioso.

- **Cumplimiento de la Ley N° 30096 (Ley de Delitos Informáticos - Perú):** El software está diseñado como una herramienta de auditoría y diagnóstico. Se establecerán mecanismos de advertencia dentro de la interfaz para que el usuario declare poseer los permisos necesarios antes de iniciar un escaneo, evitando la figura de \"Acceso Ilícito\" (Art. 2).

- **Licenciamiento de Software:** Se utilizará la licencia **MIT o Apache 2.0**, permitiendo que el código sea abierto y transparente. Esto garantiza que no existan funciones ocultas de espionaje o robo de datos, alineándose con las buenas prácticas de la comunidad de ciberseguridad.

- **Aviso de Deslinde de Responsabilidad (Disclaimer):** Se implementará un contrato de \"Aceptación de Términos\" al ejecutar la aplicación. Este documento legal especifica que los autores no se hacen responsables por el uso indebido del software en redes ajenas sin autorización expresa.

- **Protección de Datos Personales (Ley N° 29733):** El sistema no recolecta, almacena ni procesa datos personales de los usuarios ni de los sitios escaneados; los resultados del análisis residen únicamente en la sesión local del navegador (Angular) y en la memoria volátil del servidor (C#), garantizando la privacidad de la información.

## FACTIBILIDAD SOCIAL  {#factibilidad-social}

> El impacto social de **Analizador de vulnerabilidades web** radica en la democratización de la tecnología de defensa digital en el contexto local de Tacna y el Perú.
>
> **Reducción de la Brecha Digital en Ciberseguridad:** Actualmente, la seguridad informática de alto nivel es un privilegio de grandes corporaciones. Este proyecto permite que estudiantes, emprendedores y pequeñas empresas (PYMES) accedan a diagnósticos de vulnerabilidades de forma gratuita, elevando el estándar de seguridad de la región.
>
> **Fomento de la Cultura Ética:** Al ser un proyecto desarrollado en el ámbito académico de la **UPT**, promueve el uso de herramientas de \"Hacking Ético\" para la prevención, educando a los futuros ingenieros de sistemas en la importancia de la seguridad por diseño (*Security by Design*).
>
> **Seguridad para el Ciudadano Final:** Indirectamente, al ayudar a los pequeños negocios locales a asegurar sus portales web, se protege la información (nombres, correos, transacciones) de los ciudadanos tacneños que consumen servicios en línea, generando un entorno digital más confiable.

## FACTIBILIDAD AMBIENTAL

> A diferencia de los procesos industriales, el desarrollo de software tiene un impacto físico menor, pero este proyecto se alinea con las tendencias de **Green IT** (Tecnologías Verdes).

- **Eficiencia Computacional (C# y .NET 8):** El uso de la última versión de .NET permite una ejecución de código más eficiente y un menor consumo de CPU por ciclo de escaneo. Esto se traduce en un menor gasto energético de los servidores y estaciones de trabajo donde se ejecute el sistema.

- **Optimización del Frontend (Angular):** Mediante la técnica de *Lazy Loading* y la minimización de paquetes, el frontend reduce el tráfico de datos y la carga procesal en el dispositivo del usuario final, optimizando el ciclo de vida de las baterías en dispositivos móviles y laptops.

- **Cero Residuos Físicos:** La distribución es 100% digital a través de repositorios en la nube (GitHub). No se requiere el uso de medios físicos (CDs, USBs) ni documentación impresa, eliminando la generación de residuos sólidos y el uso de papel en todo el ciclo de vida del proyecto.

- **Infraestructura Cloud Sostenible:** Al recomendar el despliegue en plataformas como Azure o AWS, se aprovecha la infraestructura de centros de datos que operan mayoritariamente con energías renovables.

# **ANÁLISIS FINANCIERO**

## JUSTIFICACIÓN DE LA INVERSIÓN

> La inversión se justifica por la reducción de costos operativos que implicaría un ciberataque real (robo de datos, multas legales y pérdida de reputación).

## BENEFICIOS DEL PROYECTO

#### Para los Negocios Locales: {#para-los-negocios-locales .unnumbered}

- Reducción de riesgos de fraude.

- Cumplimiento básico de normativas de protección de datos.

## CRITERIOS DE INVERSIÓN

### RELACIÓN BENEFICIO/COSTO (B/C)

> B/C = 1.8 (Se estima que por cada dólar invertido, se ahorran 1.8 dólares en servicios de consultoría externa).

### VALOR ACTUAL NETO (VAN)  {#valor-actual-neto-van}

> Positivo, proyectando una vida útil del software de 2 años con actualizaciones mínimas.

### TASA INTERNA DE RETORNO (TIR)

> 25%, superando la tasa de descuento promedio para proyectos tecnológicos.

# **CONCLUSIONES**

> El proyecto de Analizador de vulnerabilidades web es altamente factible desde el punto de vista técnico y legal. La combinación de Angular y C# garantiza un producto rápido y escalable que resuelve una necesidad real en el mercado actual de seguridad web.
