# V02 - Inyeccion SQL en autenticacion y tokens

## Descripcion de la vulnerabilidad

La Web API original construia consultas SQL mediante
concatenacion de cadenas y datos proporcionados por el usuario.

Este procedimiento permitia que entradas manipuladas
alteraran potencialmente la estructura de las consultas SQL.

## Impacto

Una inyeccion SQL puede permitir la consulta o modificacion
no autorizada de informacion y comprometer la seguridad
de la base de datos.

## Correccion implementada

Se reemplazaron consultas construidas mediante concatenacion
por consultas parametrizadas utilizando mysql.connector.

Los valores del usuario se envian como parametros separados
de las instrucciones SQL mediante marcadores %s.

Se modificaron las consultas de autenticacion y administracion
de tokens de acceso.

## Pruebas realizadas

1. Registro de usuarios: exitoso.
2. Inicio de sesion con credenciales correctas: R = 0.
3. Rechazo de contrasena incorrecta: R = -3.
4. Verificacion de consultas parametrizadas en index.py.

## Resultado

Se eliminaron las concatenaciones inseguras identificadas
en las consultas de autenticacion y gestion de tokens.

Estas pruebas comprueban el funcionamiento de los endpoints
modificados, pero no sustituyen una prueba especifica
de resistencia frente a inyeccion SQL.

## Evidencias

- Codigo original con consultas concatenadas.
- Codigo corregido con parametros %s.
- Prueba de autenticacion correcta.
- Prueba de autenticacion rechazada.
