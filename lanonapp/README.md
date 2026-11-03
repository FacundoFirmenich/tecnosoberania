# LaNonApp · Supercheckpoint v0.8.0 + enmienda constitucional v0.8.1 (2026-11-03)

**Exocerebro personal, situacional, proactivo y comunitario.** Código fuente pre-alfa. Principios: libertad, responsabilidad, comunidad, humanismo, cuidado sin vigilancia. El **Sistema Personal Situacional Escalable (SPSE)** reemplaza al nombre anterior SVSE; los artefactos v0.7 se mantienen como antecedente histórico, no como normativa vigente.

## Enmienda constitucional v0.8.1 — vínculos humanos e integración
**LaNonApp no sustituye contacto, afecto, sociabilidad o acompañamiento humano.** Puede facilitar comunicación, encuentros, cuidado, accesibilidad y tareas (incluida robótica futura), pero jamás proponerse como reemplazo de vínculos ni justificar reducciones de cuidados humanos en políticas públicas. No se fuerza sociabilidad ni se vigila la vida social. La revisión del estado del arte busca integrar soluciones preexistentes de mayor valor, no reivindicar originalidad.
- [Principio de insustituibilidad](docs/11_PRINCIPIO_INSUSTITUIBILIDAD_VINCULO_HUMANO.md)
- [Protocolo de integración superadora](docs/12_PROTOCOLO_INTEGRACION_SUPERADORA.md)
- [Política constitucional estática](docs/13_POLITICA_CONSTITUCIONAL.json)
**Estado:** compromisos de diseño; no equivale a mecanismos efectivos ni validación social o clínica. La documentación PDF y las diapositivas v0.8.0 son instantáneas históricas.

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
python3 -m unittest discover -s tests -p test_engine.py
# UI móvil opcional: python3 tests/test_ui_playwright.py (Playwright + Chromium)
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

NO hay backend de contactos ni envío real de SMS, push, correo o llamadas; NO hay sensor activo de caídas, presión arterial o Health Connect; NO hay conexión efectiva con tags ni bancos, Bizum, billeteras o plataformas de terceros; NO hay prevención clínica, dosificación ni recordatorios de segundo plano fiables; NO hay sincronización cifrada multiequipo, E2EE ni inferencia local LLM. Los datos se guardan en localStorage del navegador **sin cifrado en reposo**. No es apta para usar datos clínicos reales ni sustituir un sistema de emergencias.

## Estructura

```
app/            Interfaz web/PWA, estado local, reglas de dominio, estilos.
android/        Wrapper Android (Gradle, Java, recursos).
desktop/        Servidor local para navegadores de escritorio y empaquetado Windows.
ios/            Fuente SwiftUI exploratoria, no compilada.
site/           Web de presentación estática.
slides/         Presentación ejecutiva PPTX y PDF.
docs/           Whitepaper, investigación científica y de mercado, políticas, contratos, validación.
engine/         Motor SQLite SPSE; autónomo, no integrado con UI ni envíos.
tests/          Pruebas JS/Python y verificación opcional de navegador.
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

## Segunda implementación autónoma
`engine/spse.py`: ledger SQLite de eventos e idempotencia, delegaciones por ámbito y revocación, recibos SPSE, router de capacidades fail-closed y aritmética condicional exacta `Decimal`. No autentica identidades reales, no cifra la base ni envía alertas. 14 tests JavaScript, 26 tests Python y 8 checks UI móviles PASS en este entorno. Ver `docs/08_DICTAMEN.md` y `docs/09_RECIBOS.md`. GitHub CI falló antes de ejecutar jobs (`startup_failure`); no hay APK/EXE/IPA verificados.