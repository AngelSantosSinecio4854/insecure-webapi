# V04 - Control de acceso insuficiente a imagenes

## Descripcion de la vulnerabilidad

La Web API original permitia solicitar la descarga
de imagenes mediante su identificador.

El sistema no comprobaba adecuadamente que la imagen
solicitada perteneciera al usuario autenticado.

Esta vulnerabilidad corresponde a un problema de
autorizacion a nivel de objeto (IDOR/BOLA).

## Impacto

Un usuario autenticado podria intentar acceder
a imagenes pertenecientes a otros usuarios,
modificando el identificador enviado a /Descargar.

Esto comprometeria la confidencialidad de los archivos.

## Correccion implementada

Se modifico el endpoint /Descargar para:

1. Validar el token de sesion.
2. Identificar al usuario autenticado.
3. Consultar la imagen mediante su identificador.
4. Comprobar que id_Usuario corresponda al propietario.
5. Rechazar solicitudes sin autorizacion.

Las consultas SQL se parametrizaron utilizando %s.

## Pruebas realizadas

1. Inicio de sesion correcto.
2. Obtencion de un token valido.
3. Descarga de una imagen del usuario autenticado.
4. Respuesta HTTP 200 al descargar la imagen autorizada.
5. Verificacion de integridad mediante SHA-256.

## Resultado

Se implemento una comprobacion de propiedad
para restringir el acceso a las imagenes.

La descarga autorizada se verifico correctamente.

Se realizo una prueba de acceso cruzado entre dos usuarios.
El sistema rechazo la descarga no autorizada con R = -3.

## Evidencias

- Codigo del endpoint /Descargar corregido.
- Consulta SQL con validacion del propietario.
- Descarga autorizada exitosa.
- Comparacion SHA-256 satisfactoria.

## Prueba adicional de acceso entre usuarios

Se realizo una prueba utilizando dos usuarios diferentes:

- test_totp01 (ID 4): propietario de la imagen ID 3.
- test_acceso02 (ID 5): usuario sin autorizacion sobre esa imagen.

El segundo usuario inicio sesion correctamente
y obtuvo un token valido (R = 0).

Posteriormente intento descargar la imagen ID 3,
perteneciente al primer usuario.

Resultado obtenido:

- Login del segundo usuario: 0.
- Intento de descarga: -3.
- ACCESO NO AUTORIZADO BLOQUEADO.

Conclusion:

Se comprobo que el endpoint /Descargar impide
que un usuario autenticado descargue imagenes
pertenecientes a otra cuenta.

La validacion se realiza mediante la consulta
SQL que comprueba simultaneamente el ID de
la imagen y el ID del usuario autenticado.
