# LaNonApp v0.9.1 — Rutas de compilación independientes

Con respecto a v0.9.0, se añade un lanzador nativo Go sin dependencias externas, compilado en Windows x86-64, Linux x86-64/ARM64 y macOS x86-64/ARM64. Estos ejecutables sirven los activos de la web incrustados en `127.0.0.1` usando un puerto libre y abren el navegador; **no integran los sensores del sistema operativo**. La app web mantiene la bóveda cifrada basada en WebCrypto. El campo `version` y la cache PWA se elevaron a v0.9.1, y la lista de caché ahora incluye `vault.js`; el manifest PWA incluye iconos PNG de 192 y 512 px.

Se documentan cuatro vías alternativas de compilación APK (Android Studio, Docker SDK, GitLab CI, Codemagic). Ninguna se ejecutó en el entorno actual por ausencia de Android SDK y red directa. NO hay APK verificable. **El prototipo no es un producto sanitario ni un servicio de emergencias, no contacta a terceros ni se integra con bancos.**

### Pruebas verificadas
- Linux nativo: `LaNonApp_linux_amd64 --version` y HTTP loopback con `GET`, métodos inválidos, host inválido y recurso inexistente: PASS.
- Node.js: 21/21 pruebas JS incluyendo cifrado y lógica de dominio: PASS.
- Python: 26/26 pruebas SPSE: PASS.
- Windows/macOS: binarios con formato nativo verificado estáticamente; **sin ejecución real en Windows/macOS**.
- Navegador real sobre localhost: bloqueado por política del navegador del entorno, sin PASS; la verificación de cifrado JavaScript se hizo por separado.

### Incompatibilidades y limitaciones
- Ejecutables no firmados, no notarizados.
- La web guarda sus datos cifrados dentro del navegador local (almacenamiento específico por origen y puerto). El lanzador utiliza **puerto fijo 18765 por defecto** para conservar el mismo origen entre aperturas, y reutiliza una sesión existente tras verificar identidad y versión. Si el puerto está ocupado por otro servicio, se detiene sin cambiar de origen. La elección explícita de `--port 0` crea un origen efímero y no preserva la bóveda entre sesiones. Se requiere prueba de recuperación en equipos Windows y macOS reales antes de uso general.
- LaNonApp sigue en fase pre-alfa; sólo datos de ensayo no sensibles.
