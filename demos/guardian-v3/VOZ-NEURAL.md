# Narración neural sin Higgsfield

**Objetivo:** generar una voz masculina natural en español de México, dividida
en 5 frases para un video vertical de 30 segundos de El Guardián Oscuro 3.0.

La implementación usa `edge-tts`, paquete de código abierto para el servicio
de lectura neuronal de Microsoft Edge. No pide claves API ni créditos de Higgsfield.
Es un servicio en línea: puede rechazar conexiones desde servidores, cambiar o
limitar acceso. Si falla, GitHub Actions reflejará el error (no creará audio falso).

## Recursos que genera

- `guardian-narracion-neural.wav` — narración sin música ni zumbido, 30 s
- `guardian-narracion-neural.mp3` — formato conveniente para editar o escuchar
- `guion-y-tiempos.json` — frases y desplazamientos exactos

Se publica en los **Artifacts** del workflow.
El video MP4 original de v3 está en la conversación, no en esta rama. Por eso
el workflow genera la voz, NO afirma haber mezclado el MP4 todavía.
Para mezclar sin repasar el video basta aportar este audio a la conversación.
