# LaNonApp · cuatro vías independientes de compilación Android

**Estado:** definición de pipelines, sin APK producida en este entorno. No se han ejecutado aquí ni GitLab, ni Codemagic, ni Docker con SDK.

El código Java nativo se encuentra en `android/`. El builder copia `app/` a los assets, ejecuta AGP y produce un APK de depuración firmada mediante la clave debug de Android. **No instala, no activa sensores, no realiza pagos ni genera alertas reales.**

1. **Android Studio local:** abrir `android/`, instalar SDK 35/Build Tools 35 y Gradle 8.12; primero copiar `app/.` a `android/app/src/main/assets/web/`; ejecutar `:app:assembleDebug` desde la interfaz o `bash ci/build_android_debug.sh` desde la raíz con `ANDROID_SDK_ROOT` configurado.
2. **Docker local:** `bash ci/build_with_docker.sh` en un ordenador con Docker y acceso a Internet. Se usa `ghcr.io/cirruslabs/android-sdk:35` (imagen pública, verificar digest en cada ciclo).
3. **GitLab CI:** trasladar `ci/gitlab-ci.yml` al raíz del repositorio del proyecto; habilitar runner compatible. Recoger artefacto `android/app/build/outputs/apk/debug/app-debug.apk`.
4. **Codemagic:** incluir `ci/codemagic.yaml` como `codemagic.yaml` en la raíz del proyecto al conectarlo. Requiere autorizar el repositorio en la cuenta de Codemagic e iniciar una compilación. No tenemos autorización para iniciar esa compilación ni acceso a sus artefactos.

Para Gradle 8.12, el builder comprueba la huella SHA-256 del archivo ZIP contra la publicada por Gradle. No acepta un ZIP con suma diferente. Las dependencias AGP/SDK deben revisarse y fijarse antes de producción.

## Condición de aceptación

Sólo llamaremos **APK instalable verificada** al archivo compilado que exista realmente, cuyo paquete/versión/firma e integridad se inspeccionen y que haya superado al menos un ensayo de instalación y apertura en Android compatible. Actualmente ese requisito **no se cumple**.
