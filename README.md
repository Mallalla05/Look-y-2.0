# Look-Y    2.0


Este proyecto implementa una interfaz tipo aplicación móvil, moderna e interactiva, diseñada para comunicarse mediante puerto serial con un ESP32.
El sistema permite controlar funciones, enviar comandos y visualizar información, así como utilizar herramientas de traducción y selección de idioma integradas en la interfaz.
La finalidad del proyecto es ofrecer una experiencia fluida, clara y fácil de usar, simulando una app nativa desde un entorno Python.

## Funcionalidades principales
1. Envío de comandos por puerto serial
La interfaz incluye botones estilizados tipo app, cada uno asociado a una acción específica:
Enviar comando A/B/C
Conectar / Desconectar
Comando de texto
Botón de Ubicación (GPS/“Ir”)
Botones en azul marino neon, texto en blanco y diseño minimalista.
Los comandos se envían al ESP32 mediante PySerial.
2. Sistema de traducción
La app cuenta con una función que permite:
Traducir texto escrito por el usuario.
Seleccionar idioma de salida.
Mostrar el resultado en la misma interfaz.
Ideal para comunicación accesible o proyectos educativos.
3. Cambio de idioma en la interfaz
El usuario puede cambiar el idioma de toda la app (menús, botones y etiquetas) mediante un selector interno.
Idiomas típicos incluidos:
Español
Inglés
Francés (o los que el proyecto necesite)
Esto permite adaptar la experiencia del usuario según sus necesidades lingüísticas.
4. Diseño tipo aplicación móvil
Inspirado en interfaces modernas:
Fondo gris claro
Botones azul marino neon
Texto azul en etiquetas y blanco en botones
Tipografía elegante
Distribución tipo grid para pantallas estilo celular
Elementos decorativos como gráficas suaves (sin porcentajes ni datos complejos)


## Creadoras del proyecto
- Mariana Hernández Díaz

- Anell Moreno Quintan


## Requisitos
- Python 3.11.9

- pip actualizado

- Entorno virtual (venv)
- ESP32 (opcional según módulo del proyecto)

## Instalacion
- Clonar el repositorio
- Crear entorno virtual con Python 3.11.9
- Activar entorno virtual
- Instalar las dependencias
- Ejecutar la app

