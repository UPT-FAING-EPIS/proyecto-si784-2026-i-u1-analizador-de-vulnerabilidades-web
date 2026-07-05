Feature: Deteccion de vulnerabilidades web
  Como analista de seguridad
  Quiero que el scanner detecte vulnerabilidades en sitios web
  Para generar reportes de riesgo y guias de remediacion

  Scenario: Detectar cabeceras de seguridad faltantes
    Given un sitio sin cabeceras de seguridad configuradas
    When analizo las cabeceras del sitio
    Then debo encontrar al menos una vulnerabilidad de cabecera faltante

  Scenario: No reportar falsos positivos cuando las cabeceras estan presentes
    Given un sitio con todas las cabeceras de seguridad configuradas
    When analizo las cabeceras del sitio
    Then no debo encontrar vulnerabilidades de cabecera faltante

  Scenario: Detectar CORS wildcard permisivo
    Given un sitio con CORS configurado como wildcard
    When analizo las cabeceras del sitio
    Then debo encontrar una vulnerabilidad de tipo CORS Misconfiguration

  Scenario: Retornar lista vacia cuando el sitio no responde
    Given un sitio que no responde
    When analizo las cabeceras del sitio
    Then debo obtener una lista de hallazgos vacia

  Scenario: Detectar WordPress en el cuerpo de la respuesta
    Given un sitio que usa WordPress
    When detecto las tecnologias del sitio
    Then WordPress debe estar en la lista de CMS detectados

  Scenario: Retornar estructura vacia cuando el sitio no responde al detectar tecnologias
    Given un sitio que no responde
    When detecto las tecnologias del sitio
    Then la lista de CMS detectados debe estar vacia

  Scenario: Construir hallazgo con campos correctos
    Given un hallazgo de tipo sqli con severidad high
    When verifico la estructura del hallazgo
    Then el tipo de vulnerabilidad debe ser sqli
    And la severidad debe ser high

  Scenario: Truncar evidencia larga a 500 caracteres
    Given un hallazgo con evidencia de 600 caracteres
    When verifico la estructura del hallazgo
    Then la evidencia debe tener exactamente 500 caracteres

  Scenario: Inyectar payload en parametros de URL existentes
    Given una URL con parametros de consulta
    When inyecto un payload en los parametros
    Then el payload debe aparecer en la URL resultante

  Scenario: Agregar parametros cuando la URL no tiene ninguno
    Given una URL sin parametros de consulta
    When inyecto un payload en los parametros
    Then la URL resultante debe contener parametros con el payload
