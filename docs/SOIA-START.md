# SOIA CINE STUDIO — Inicio de desarrollo

Esta es una bifurcacion (fork) de [sarpstar/cinecode](https://github.com/sarpstar/cinecode).
Conservamos su licencia MIT y el archivo LICENSE original. Las nuevas funciones se
desarrollan por separado antes de integrarlas.

## Estado del proyecto

- `main`: base original conservada.
- `desarrollo-soia`: trabajo de adaptacion para SOIA.
- El motor de video de Cinecode no se ha modificado en esta fase.
- El diagnostico comprueba herramientas presentes, NO confirma GPU ni un MP4 funcional.

## Verificacion desde Codespaces

Abrir la terminal del Codespace y ejecutar:

```bash
python3 scripts/soia_doctor.py
```

Para un resultado estructurado:

```bash
python3 scripts/soia_doctor.py --json
```

El modo estricto termina con codigo 1 si falta una dependencia:

```bash
python3 scripts/soia_doctor.py --strict
```

Requisitos comprobados: Python >= 3.9, Node.js >= 22, FFmpeg, FFprobe y Chrome/Chromium.

## Validacion en GitHub

El flujo `SOIA | Diagnostico del entorno` de GitHub Actions se ejecuta al enviar
cambios relevantes a `desarrollo-soia`, usando un entorno de Ubuntu de GitHub.
Esto NO prueba el estado del Codespace personal: verifica un entorno diferente.
El repositorio original ya contiene otro flujo de pruebas que tambien se ejecuta
con los pushes. GitHub Actions puede consumir cuota de la cuenta.

## Proxima fase propuesta

1. Revisar resultados del diagnostico y del flujo existente de pruebas.
2. Ejecutar una prueba de captura de un fotograma sin modificar el motor.
3. Comprobar GPU y render de un clip MP4 corto.
4. Integrar una direccion visual propia y sincronizacion musical para ROQUE.
5. Corregir incidencias documentadas solo con pruebas de regresion.

No poner claves API en el repositorio ni subir musica o recursos sin permiso.
