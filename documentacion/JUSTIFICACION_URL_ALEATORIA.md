# Justificacion de nombres aleatorios para imagenes

## Problema identificado

Originalmente, la API almacenaba las imagenes utilizando
nombres basados en identificadores consecutivos:

img/1.png
img/2.png
img/3.png

Este esquema permitia predecir facilmente los nombres
de otros archivos.

## Solucion implementada

Se utilizo la biblioteca secrets de Python:

nombre_aleatorio = secrets.token_hex(16)
ruta = f'img/{nombre_aleatorio}.{extension}'

La funcion genera 16 bytes aleatorios, representados
mediante 32 caracteres hexadecimales.

Esto proporciona 128 bits de aleatoriedad.

## Justificacion de seguridad

Los nombres aleatorios dificultan la enumeracion
y prediccion de las rutas de almacenamiento.

Sin embargo, un nombre aleatorio no reemplaza
los mecanismos de autenticacion y autorizacion.

El endpoint /Descargar comprueba el token y que
la imagen pertenezca al usuario autenticado.

## Funcionamiento

1. El usuario inicia sesion.
2. La API valida sus credenciales y TOTP.
3. El cliente envia una imagen comprimida con gzip
   y codificada en Base64.
4. La API decodifica y descomprime la imagen.
5. Se genera un nombre aleatorio para almacenarla.
6. La ruta se registra en MariaDB.
7. La descarga se realiza mediante /Descargar,
   validando el token y la propiedad de la imagen.

## Evidencias obtenidas

Imagen de prueba: ID 4.

Ruta generada:
img/11e8f54687a19eb0b5c8b508296516f1.png

Pruebas realizadas:

- Subida correcta: R = 0.
- Ruta aleatoria registrada en MariaDB.
- Archivo almacenado correctamente.
- Hash SHA-256 identico al original.
- Descarga autenticada exitosa.
- Archivo PNG valido: True.
- Archivos identicos: True.

## Aclaracion

La ruta registrada es un nombre interno de
almacenamiento, no una URL publica de descarga.

La API entrega las imagenes mediante el endpoint
autenticado /Descargar.

Las imagenes anteriores conservan sus nombres
originales y no se renombran automaticamente.
