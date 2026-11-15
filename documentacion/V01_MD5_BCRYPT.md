
# V01 - Almacenamiento inseguro de contraseñas con MD5

## Descripción de la vulnerabilidad

La Web API original utilizaba el algoritmo MD5 para almacenar y verificar las contraseñas de los usuarios.

MD5 es un algoritmo de hash criptográfico que no resulta adecuado para proteger contraseñas, debido a su velocidad de cálculo y a la ausencia de un mecanismo de endurecimiento diseñado para dificultar los ataques de fuerza bruta.

Si un atacante obtiene los hashes de la base de datos, podría intentar recuperar contraseñas mediante ataques de diccionario o fuerza bruta.

## Impacto

Esta vulnerabilidad compromete la confidencialidad de las credenciales de los usuarios y podría permitir accesos no autorizados.

## Corrección implementada

Se sustituyó MD5 por bcrypt mediante el archivo seguridad.py.

Se implementaron dos funciones:

- generar_hash(): genera hashes bcrypt con factor de costo 12.
- verificar_password(): valida las contraseñas utilizando bcrypt.checkpw().

También se modificaron los endpoints /Registro y /Login para utilizar estas funciones.

Las consultas SQL de búsqueda e inserción de usuarios se parametrizaron para evitar la concatenación directa de datos del usuario.

## Pruebas realizadas

1. Registro del usuario test_bcrypt01: exitoso.
2. Consulta en MariaDB: hash con prefijo $2b$12$ y longitud de 60 caracteres.
3. Inicio de sesión con contraseña correcta: R = 0.
4. Inicio de sesión con contraseña incorrecta: R = -3.

## Resultado

Se comprobó que los usuarios nuevos pueden registrarse e iniciar sesión utilizando bcrypt.

Los usuarios antiguos con contraseñas MD5 requieren un procedimiento de migración o restablecimiento de contraseña.

## Evidencias

- R004-01: registro exitoso.
- R004-02: hash bcrypt en MariaDB.
- R004-03: autenticación exitosa.
- R004-04: rechazo de contraseña incorrecta.
