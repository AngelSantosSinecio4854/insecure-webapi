# V05 - Exposicion de credenciales de base de datos

## Descripcion de la vulnerabilidad

La Web API utilizaba un archivo db.json que contenia
los datos de conexion a MariaDB, incluyendo usuario
y contrasena.

Este archivo estaba incluido anteriormente en el
control de versiones Git.

La publicacion de credenciales puede permitir que
personas no autorizadas obtengan informacion sensible.

## Impacto

Si un atacante obtiene credenciales validas, podria
intentar conectarse a la base de datos y acceder,
modificar o eliminar informacion, dependiendo de
los permisos asignados al usuario.

## Correccion implementada

Se realizaron las siguientes acciones:

1. Se retiro db.json del seguimiento de Git.
2. Se configuro .gitignore para excluir db.json.
3. Se creo db.example.json con valores de ejemplo.
4. Se cambio la contrasena del usuario de MariaDB.
5. Se creo la rama seguridad-publica con un
   historial independiente que no incluye db.json.

## Pruebas realizadas

1. Verificacion de archivos incluidos en Git.
2. Confirmacion de que db.json no aparece en el commit.
3. Revision de db.example.json sin contrasenas reales.
4. Comprobacion de conexion con MariaDB: CORRECTA.
5. Publicacion de seguridad-publica en GitHub.

## Resultado

El archivo de configuracion con credenciales reales
no se incluye en la rama seguridad-publica.

Se conserva un archivo de ejemplo para facilitar
la configuracion de nuevas instalaciones.

## Limitaciones

Excluir db.json de una rama nueva no elimina
automaticamente posibles secretos publicados
en el historial de otras ramas o repositorios.

Es necesario comprobar su exposicion anterior,
mantener las credenciales rotadas y revisar
los permisos del usuario de MariaDB.

## Evidencias

- Archivo .gitignore.
- Archivo db.example.json.
- Listado de archivos de la rama seguridad-publica.
- Prueba de conexion correcta con MariaDB.
- Publicacion de la rama en GitHub.
