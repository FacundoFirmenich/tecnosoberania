# LaNonApp · Supercheckpoint v0.9.0 + enmienda constitucional v0.9.0 (2026-11-03)

**Exocerebro personal, situacional, proactivo y comunitario.** Código fuente pre-alfa. Principios: libertad, responsabilidad, comunidad, humanismo, cuidado sin vigilancia. El **Sistema Personal Situacional Escalable (SPSE)** reemplaza al nombre anterior SVSE; los artefactos v0.7 se mantienen como antecedente histórico, no como normativa vigente.

## Enmienda constitucional v0.9.0 — vínculo humano e integración superadora

**La IA no sustituye la compañía, el cuidado relacional ni la sociabilidad humana.** LaNonApp puede ayudar a facilitar encuentros, llamadas, redes de cooperación, tareas y acceso a servicios, pero no se diseña para generar dependencia afectiva ni para reemplazar vínculos personales o recortar apoyo humano en políticas públicas. La persona conserva su libertad de relacionarse o no; no se vigila su vida social.

La revisión exhaustiva del estado del arte persigue **reutilizar e integrar todo componente genuinamente valioso**, incluso de productos rivales. La originalidad no es un objetivo de marketing ni un criterio de exclusión de soluciones preexistentes.

- [Principio de insustituibilidad del vínculo humano](docs/11_PRINCIPIO_INSUSTITUIBILIDAD_VINCULO_HUMANO.md)
- [Protocolo de integración superadora](docs/12_PROTOCOLO_INTEGRACION_SUPERADORA.md)
- [Política constitucional legible por máquina (NO aplicada por runtime)](docs/13_POLITICA_CONSTITUCIONAL.json)

**Importante:** esta enmienda es diseño y criterios de aceptación. No añade por sí sola mecanismos de contacto, coordinación comunitaria ni controles ejecutables que aún no estén integrados. Los documentos y binarios del corte v0.9.0 son instantáneas históricas.

## Inicio inmediato

Desde el directorio raíz:

```bash
python3 desktop/lanonapp_desktop.py
# Abre automáticamente http://127.0.0.1:8765/app/index.html
```

En Linux, también `./run-linux.sh`. Se puede servir como sitio estático HTTPS; la aplicación está en `app/index.html` y la web de presentación en `site/index.html`. En Android, el proyecto Gradle bajo `android/` envuelve la misma aplicación web como WebView, sin JavaScript bridge; hay workflow para compilar `assembleDebug`. El código SwiftUI/iOS es sólo fuente inicial, no una IPA.

### Verificación local

```bash
node --test tests/core.test.js
python3 -m py_compile desktop/lanonapp_desktop.py
```

## Funciones ejecutables de la pre-alfa

- Captura y recuperación de tareas, agenda local, finalización explícita.
- Objetos y ubicaciones **declaradas**, con tiempo de registro; no Bluetooth activo ni sonido de tags.
- Registro no clínico de pautas, toma autodeclarada, negativas y aplazamientos; regla de dos negativas que crea **incidente local no enviado**.
- Hábitos decididos por la persona y prácticas autodeclaradas.
- Cultura: enlaces explícitos a plataformas y reproductor oficial incrustado de YouTube tras acción del usuario.
- Economía: flujos manuales separados por moneda, stocks declarados y simulación WHAT-IF **condicional determinista** (no proyección probabilística).
- Contactos de cooperación, anotación de competencias declaradas **sin verificación jurídica**.
- Exportación/importación JSON, borrado local, navegación responsive, contraste alto y dictado explícitamente opt-in cuando el navegador lo permite.

## Lo que NO funciona todavía

NO hay backend de contactos ni envío real de SMS, push, correo o llamadas; NO hay sensor activo de caídas, presión arterial o Health Connect; NO hay conexión efectiva con tags ni bancos, Bizum, billeteras o plataformas de terceros; NO hay prevención clínica, dosificación ni recordatorios de segundo plano fiables; NO hay sincronización cifrada multiequipo, E2EE ni inferencia local LLM. Los datos se guardan en una bóveda **PBKDF2-SHA256 + AES-GCM** en localStorage, desbloqueada por frase de acceso. El cifrado no protege contra JavaScript malicioso ejecutado en el mismo origen, extensiones hostiles o un dispositivo comprometido. No es apta para usar datos clínicos reales ni sustituir un sistema de emergencias.

## Estructura

```
app/            Interfaz web/PWA, estado local, reglas de dominio, estilos.
android/        Wrapper Android (Gradle, Java, recursos).
desktop/        Servidor local para navegadores de escritorio y empaquetado Windows.
ios/            Fuente SwiftUI exploratoria, no compilada.
site/           Web de presentación estática.
slides/         Presentación ejecutiva PPTX y PDF.
docs/           Whitepaper, investigación científica y de mercado, políticas, contratos, validación.
tests/          Pruebas automatizadas del dominio.
legacy/         Artefacto v0.7 preservado para trazabilidad histórica.
```

## Gobernanza e historia

- Terminología: *centum* no; **centrum** rector. Llaves constitucionales delegadas y ámbitos diferenciados; nadie adquiere permisos por la mera condición de familiar.
- Proactividad no equivale a permisos ejecutivos. Autoridad profesional, representación legal y administración técnica se separan.
- Familia SPSE: responsabilidad situacional, escalamiento humano proporcional y mínima intrusión. La «vigilancia» queda explícitamente descartada como principio.
- Salud sociocognitivo-cultural: familia provisional; higiene como subcomponente y bienestar como subfamilia distinta.
- «Nona» nombra el origen humano; «non-app», la multiplicidad de accesos y la reducción de fricción.
- La biografía sensible de la persona que inspiró el proyecto **no se incluye en el código ni en la documentación destinada a difusión**.

## Licencia y seguridad

Se propone licencia **AGPL-3.0-or-later** para el código original de este paquete; ver `LICENSE`. No arrastra licencias de los productos investigados: cualquier integración de terceros requiere su propia revisión. **No está certificado** bajo legislación de productos sanitarios. Antes de cualquier piloto real: análisis de riesgos, seguridad de almacenamiento, permisos reales y evaluación ética/profesional.

## v0.9 — cambio material
- Bóveda AES-GCM por contraseña: no admite datos clínicos reales; sesión desbloqueada en memoria. Copias de seguridad cifradas, restauración autenticada y bloqueo manual.
- Recepción de enlaces mediante Web Share Target en instalaciones PWA compatibles, con confirmación explícita.
- Auditoría local de tiempo visible dentro de LaNonApp, no monitorización de terceros.
- Proyecciones financieras con aritmética decimal exacta de centésimas y moneda explícita; no son pronósticos.
- La versión v0.8 almacenaba datos sin cifrar en `lanonapp_alpha_v08`: no se migran automáticamente ni se envían a ningún servidor. Antes de utilizar v0.9 en un navegador previo, exportar por separado los datos no sensibles si se desean conservar.
- No se ha realizado pentest ni auditoría criptográfica externa.


## Entrega v0.9.0, web y distribución

La web pre-alfa está en `app/index.html`; el sitio informativo en `index.html`. El portal y el código se distribuyen en rama pública de pruebas `FacundoFirmenich/tecnosoberania:lanonapp-preview-v09-2026-11-03`, además de este ZIP. Se requiere HTTPS o localhost para WebCrypto; la ejecución bajo `file://` puede fallar. Este paquete incluye un instalador Debian construido y un HTML autocontenido de ensayo (archivos externos al ZIP).

La bóveda usa WebCrypto (AES-GCM y PBKDF2) para cifrar la información en reposo dentro de un solo navegador. Sólo se registran tiempos de actividad del propio sitio. No hay telemetría remota ni vigilancia de otras plataformas. La sincronización y el sistema de identidad siguen sin implementar. No se deben guardar datos personales sensibles en esta pre-alfa.

La rama pública no debe confundirse con un sitio web de producción ya desplegado. La previsualización mediante un proxy de terceros no garantiza disponibilidad ni aislamiento de origen, y debe probarse exclusivamente con datos de ensayo. El build Android/Windows remoto tiene estado `startup_failure` antes de iniciar jobs.