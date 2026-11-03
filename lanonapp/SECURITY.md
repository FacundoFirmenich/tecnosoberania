# Seguridad y protección de personas — pre-alfa
LaNonApp v0.9 no está autorizada para uso clínico, emergencias, soporte vital ni pagos reales. NO introducir datos de salud, financieros, familiares ni documentos de identidad reales. La bóveda WebCrypto cifra los registros del navegador en reposo, pero NO ha pasado auditoría externa; el motor Python/SQLite separado sigue SIN cifrado ni autenticación de operadores.

## Superficies de amenaza
- Consentimiento y atribución: las llaves técnicas no demuestran representación legal o autoridad profesional. Nunca suponer por apellido o relación.
- Identidad y claves: bóveda cifrada local implementada en web, pero aún sin autenticación multifactor, recuperación de claves, sincronización cifrada ni gestión de identidad a escala.
- Mensajes y contenidos: fuentes de noticias, URLs y transcripciones deben tratarse como datos no confiables y no pueden modificar delegaciones, reglas médicas o herramientas.
- Proveedores: una función documentada no es una API autorizada; declarar país, firmware, SDK, permisos, términos y fecha de prueba.
- Medicación y accidentes: «no respuesta» no es negativa; «mensaje encolado» no es entregado; «lectura del reloj» no es diagnóstico.
- Adversarios: fraude financiero, abuso por familiar/tutor, vigilancia intrusiva, acoso por proactividad, suplantación con voz, interceptación de notificaciones y captura innecesaria de datos.

## Arquitectura protectora propuesta
Procesamiento local y minimización, autorización por ámbito con fechas y revocación, separación de identidad y contenido, auditoría de recibos sin grabación ambiental, cifrado local en reposo reforzado y auditado, E2EE para sincronización, rotación de claves, pruebas de penetración, límites de retención, borrado real y control independiente de accesos. Salvo la bóveda WebCrypto local (sin auditoría externa), estas garantías son requisitos, **NO funciones implementadas**.

## Reporte de incidentes
No publicar credenciales, historias clínicas ni reproducciones con información personal en issues públicos. Usar canales privados acordados entre responsables antes de abrir un programa de divulgación coordinada.


## Cifrado v0.9
La bóveda implementa PBKDF2-HMAC-SHA256 (310.000 iteraciones) y AES-GCM de 256 bits mediante WebCrypto, con IV aleatorio por escritura. La contraseña no se guarda; el cifrado en reposo no evita ataques por XSS, inyección de scripts, extensiones maliciosas ni teléfonos comprometidos. No se ha auditado criptográficamente ni debe guardar datos de salud reales. En previsualizaciones de terceros existe un riesgo adicional por origen compartido; usar únicamente datos de prueba.