# EL GUARDIÁN OSCURO — La campana sellada

Primer cortometraje original de SOIA CINE STUDIO, realizado con animación
procedimental Canvas 2D y diseño sonoro sintetizado.

## Formato

- 20 segundos; 540 × 960 píxeles (9:16), 24 FPS.
- Historia ficticia de misterio, cinco bloques narrativos con texto en español.
- Pontífice Oscuro: mitra negra, bordados dorados, rostro en penumbra,
  báculo ceremonial, catedral gótica, vitrales, velas y niebla.
- Sonido: música atmosférica y campanadas creadas por `audio.py`.
- **Sin narrador grabado:** esta primera prueba comunica por texto y sonido.
- Sin música comercial, fotos externas, servicios de IA de video ni claves API.

## Historia

1. La campana sonó desde una tumba sellada.
2. El guardián conocía aquel sonido.
3. No era una advertencia: era una invitación.
4. La última vela se apagó y la puerta respondió.
5. ¿Tú habrías entrado?

## Producción automatizada

El flujo `EL GUARDIÁN | Cortometraje piloto` renderiza el video mediante
`scripts/capture.mjs`, genera el audio mediante `audio.py`, y une
ambos con FFmpeg. `ffprobe` verifica video H.264, audio AAC y formato vertical.

El MP4 y un fotograma de portada se descargan desde los *Artifacts*
de GitHub Actions (con caducidad de siete días).

## Alcance de esta primera versión

Es **animación estilizada en 2D con profundidad simulada**, no 3D real ni
generación fotorrealista. Las letras se muestran en pantalla; una versión
futura podrá añadir narración humana con su autorización.
La prueba no modifica la rama `main` ni `desarrollo-soia`.
