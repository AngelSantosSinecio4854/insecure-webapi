# V03 - Inyeccion SQL en la subida de imagenes

## Descripcion de la vulnerabilidad

La funcion /Imagen de la Web API original utilizaba
consultas SQL construidas mediante concatenacion
de datos proporcionados por el cliente.

Los campos de las solicitudes podian incorporarse
directamente a instrucciones SQL, permitiendo
potencialmente alterar su comportamiento.

## Impacto

Un atacante podria intentar manipular consultas,
modificar registros de imagenes o acceder a
informacion sin autorizacion.

Tambien existia riesgo de afectar la integridad
de los datos almacenados en MariaDB.

## Correccion implementada

Se sustituyeron las consultas SQL concatenadas
por instrucciones parametrizadas con marcadores %s.

Se modificaron las operaciones relacionadas con:

- Validacion de tokens de acceso.
- Registro de informacion de imagenes.
- Obtencion del identificador de la imagen.
- Actualizacion de la ruta del archivo.

Para recuperar el identificador generado por MariaDB
se utiliza cursor.lastrowid, evitando una consulta
adicional basada en MAX(id).

## Pruebas realizadas

1. Inicio de sesion exitoso.
2. Envio de imagen mediante /Imagen.
3. Registro exitoso de la imagen: R = 0.
4. Obtencion del identificador de imagen.
5. Descarga posterior mediante /Descargar.
6. Comparacion SHA-256: archivos identicos.

## Resultado

Las consultas identificadas en /Imagen se
reemplazaron por consultas parametrizadas.

Las pruebas funcionales comprobaron que las
operaciones de subida y descarga continuaron
funcionando correctamente.

No se realizo una prueba especifica de
explotacion de inyeccion SQL.

## Evidencias

- Consultas SQL originales de /Imagen.
- Consultas parametrizadas en index.py.
- Respuesta de subida exitosa: R = 0.
- Imagen registrada con ID 3.
- Comparacion SHA-256 satisfactoria.
