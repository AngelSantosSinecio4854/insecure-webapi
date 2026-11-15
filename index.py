import json
import random
import hashlib
import mysql.connector
import base64
import shutil
from datetime import datetime
from pathlib import Path
from bottle import route, run, template, post, request, static_file
from seguridad import generar_hash, verificar_password, verificar_totp
import pyotp
import gzip
import secrets


def loadDatabaseSettings(pathjs):
    pathjs = Path(pathjs)
    sjson = False
    if pathjs.exists():
        with pathjs.open() as data:
            sjson = json.load(data)
    return sjson

"""
function loadDatabaseSettings(pathjs):
    string = file_get_contents(pathjs);
    json_a = json_decode(string, true);
    return json_a;

"""
def getToken():
    tiempo = datetime.now().timestamp()
    numero = random.random()
    cadena = str(tiempo) + str(numero)
    numero2 = random.random()
    cadena2 = str(numero)+str(tiempo)+str(numero2)
    m = hashlib.sha1()
    m.update(cadena.encode())
    P = m.hexdigest()
    m = hashlib.md5()
    m.update(cadena.encode())
    Q = m.hexdigest()
    return f"{P[:20]}{Q[20:]}"

"""
*/
# Registro
/*
 * Este Registro recibe un JSON con el siguiente formato
 *
 * :
 *      "uname": "XXX",
 *      "email": "XXX",
 *      "password": "XXX"
 *
 * */
"""
@post('/Registro')
def Registro():
    dbcnf = loadDatabaseSettings('db.json');
    db = mysql.connector.connect(
        host='localhost', port = dbcnf['port'],
        database = dbcnf['dbname'],
        user = dbcnf['user'],
        password = dbcnf['password']
    )
    ####/ obtener el cuerpo de la peticion
    if not request.json:
        return {"R":-1}
    R = 'uname' in request.json and 'email' in request.json and 'password' in request.json
    # TODO checar si estan vacio los elementos del json
    if not R:
        return {"R":-1}
    # TODO validar correo en json
    # TODO Control de error de la DB
    R = False
    try:
        password_hash = generar_hash(request.json["password"])
        totp_secret = pyotp.random_base32()
        with db.cursor() as cursor:
            sql = """INSERT INTO Usuario(uname, email, password, totp_secret, totp_enabled) VALUES (%s, %s, %s, %s, %s)"""
            datos = (
                request.json["uname"],
                request.json["email"],
                password_hash,
                totp_secret, 0
            )

            cursor.execute(sql, datos)
            R = cursor.lastrowid
            db.commit()

        db.close()
    except Exception as e:
        print(e)
        return {"R":-2}
    return {"R":0,"D":R}




"""
/*
 * Este Registro recibe un JSON con el siguiente formato
 *
 * :
 *      "uname": "XXX",
 *      "password": "XXX"
 *
 *
 * Debe retornar un Token
 * */
"""

@post('/Login')
def Login():
    dbcnf = loadDatabaseSettings('db.json');
    db = mysql.connector.connect(
        host='localhost', port = dbcnf['port'],
        database = dbcnf['dbname'],
        user = dbcnf['user'],
        password = dbcnf['password']
    )
    ###/ obtener el cuerpo de la peticion
    if not request.json:
        return {"R":-1}
    ######/
    R = 'uname' in request.json  and 'password' in request.json
    # TODO checar si estan vacio los elementos del json
    if not R:
        return {"R":-1}

    # TODO validar correo en json
    # TODO Control de error de la DB
    R = False
    try:
        with db.cursor() as cursor:
            sql = "SELECT id, password, totp_secret, totp_enabled FROM Usuario WHERE uname = %s"
            cursor.execute(sql, (request.json["uname"],))
            usuario = cursor.fetchone()

        if not usuario:
            db.close()
            return {"R": -3}

        if not verificar_password(request.json["password"], usuario[1]):
            db.close()
            return {"R": -3}

        if usuario[3] == 1:
            codigo = request.json.get("codigo")
            if not verificar_totp(usuario[2], codigo):
                db.close()
                return {"R": -5}

        R = [(usuario[0],)]
    except Exception as e:
        print(e)
        db.close()
        return {"R": -2}


    if not R:
        db.close()
        return {"R":-3}

    T = getToken();
    #file_put_contents('/tmp/log','insert into AccesoToken values('.R[0].',"'.T.'",now())');
    with open("/tmp/log","a") as log:
        log.write(f'Delete from AccesoToken where id_Usuario = "{R[0][0]}"\n')
        log.write(f'insert into AccesoToken values({R[0][0]},"{T}",now())\n')


    try:
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM AccesoToken WHERE id_Usuario = %s",
            (R[0][0],)
            )
            cursor.execute(
                "INSERT INTO AccesoToken VALUES (%s, %s, NOW())",
                (R[0][0], T)
            )
            db.commit()
            db.close()
            return {"R":0,"D":T}
    except Exception as e:
        print(e)
        db.close()
        return {"R":-4}

"""
/*
 * Este subir imagen recibe un JSON con el siguiente formato
 *
 *
 *      "token: "XXX"
 *      "name": "XXX",
 *      "data": "XXX",
 *      "ext": "PNG"
 *
 *
 * Debe retornar codigo de estado
 * */
"""
@post('/Imagen')

def Imagen():
    tmp = Path('tmp')
    tmp.mkdir(exist_ok=True)

    img = Path('img')
    img.mkdir(exist_ok=True)

    if not request.json:
        return {"R": -1}

    datos = request.json

    if not all(k in datos for k in ('name', 'data', 'ext', 'token')):
        return {"R": -1}

    if not all(isinstance(datos[k], str) and datos[k] for k in ('name', 'data', 'ext', 'token')):
        return {"R": -1}

    extension = datos['ext'].lower()

    if extension not in ('png', 'jpg', 'jpeg'):
        return {"R": -1}

    dbcnf = loadDatabaseSettings('db.json')
    db = mysql.connector.connect(
        host='localhost',
        port=dbcnf['port'],
        database=dbcnf['dbname'],
        user=dbcnf['user'],
        password=dbcnf['password']
    )

    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id_Usuario FROM AccesoToken WHERE token = %s",
                (datos['token'],)
            )
            usuario = cursor.fetchone()

            if not usuario:
                return {"R": -2}

            id_usuario = usuario[0]

            imagen_comprimida = base64.b64decode(datos['data'], validate=True)
            imagen_bytes = gzip.decompress(imagen_comprimida)

            cursor.execute(
                "INSERT INTO Imagen (name, ruta, id_Usuario) VALUES (%s, %s, %s)",
                (datos['name'], 'img/', id_usuario)
            )

            id_imagen = cursor.lastrowid
            nombre_aleatorio = secrets.token_hex(16)
            ruta = f'img/{nombre_aleatorio}.{extension}'

            cursor.execute(
                "UPDATE Imagen SET ruta = %s WHERE id = %s",
                (ruta, id_imagen)
            )

            with open(ruta, 'wb') as archivo:
                archivo.write(imagen_bytes)

            db.commit()
            return {"R": 0, "D": id_imagen}

    except Exception as e:
        print(e)
        db.rollback()
        return {"R": -3}

    finally:
        db.close()

"""
/*
 * Este Registro recibe un JSON con el siguiente formato
 *
 * :
 *      "token: "XXX",
 *      "id": "XXX"
 *
 *
 * Debe retornar un Token
 * */
"""

@post('/Descargar')

def Descargar():
    if not request.json:
        return {"R": -1}

    datos = request.json

    if "token" not in datos or "id" not in datos:
        return {"R": -1}

    token = datos["token"]

    try:
        id_imagen = int(datos["id"])
        if id_imagen <= 0:
            return {"R": -1}
    except (ValueError, TypeError):
        return {"R": -1}

    if not isinstance(token, str) or not token:
        return {"R": -1}

    dbcnf = loadDatabaseSettings("db.json")

    db = mysql.connector.connect(
        host="localhost",
        port=dbcnf["port"],
        database=dbcnf["dbname"],
        user=dbcnf["user"],
        password=dbcnf["password"]
    )

    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id_Usuario FROM AccesoToken WHERE token = %s",
                (token,)
            )

            usuario = cursor.fetchone()

            if not usuario:
                return {"R": -2}

            cursor.execute(
                """SELECT name, ruta FROM Imagen
                   WHERE id = %s AND id_Usuario = %s""",
                (id_imagen, usuario[0])
            )

            imagen = cursor.fetchone()

            if not imagen:
                return {"R": -3}

            nombre, ruta = imagen

            carpeta = Path("img").resolve()
            archivo = Path(ruta).resolve()

            if not archivo.is_relative_to(carpeta):
                return {"R": -3}

            if not archivo.is_file():
                return {"R": -3}

            return static_file(
                archivo.name,
                root=str(carpeta),
                download=nombre
            )

    except Exception as e:
        print(e)
        return {"R": -3}

    finally:
        db.close()
@post('/ActivarTOTP')
def ActivarTOTP():
    datos = request.json

    if not isinstance(datos, dict):
        return {"R": -1}

    token = datos.get("token")
    codigo = datos.get("codigo")

    if not isinstance(token, str) or not token:
        return {"R": -1}

    if not isinstance(codigo, str):
        return {"R": -1}

    dbcnf = loadDatabaseSettings("db.json")

    try:
        db = mysql.connector.connect(
            host="localhost",
            port=dbcnf["port"],
            database=dbcnf["dbname"],
            user=dbcnf["user"],
            password=dbcnf["password"]
        )
    except Exception:
        return {"R": -2}

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """SELECT U.id, U.totp_secret, U.totp_enabled
                   FROM Usuario U
                   JOIN AccesoToken A ON A.id_Usuario = U.id
                   WHERE A.token = %s""",
                (token,)
            )

            usuario = cursor.fetchone()

            if not usuario:
                return {"R": -3}

            id_usuario, secreto, activado = usuario

            if activado == 1 or not secreto:
                return {"R": -4}

            if not verificar_totp(secreto, codigo):
                return {"R": -5}

            cursor.execute(
                "UPDATE Usuario SET totp_enabled = 1 WHERE id = %s",
                (id_usuario,)
            )

            db.commit()
            return {"R": 0, "D": "TOTP activado"}

    except Exception as e:
        print(type(e).__name__)
        db.rollback()
        return {"R": -2}

    finally:
        db.close()

@post('/ConfigurarTOTP')
def ConfigurarTOTP():
    datos = request.json

    if not isinstance(datos, dict):
        return {"R": -1}

    token = datos.get("token")

    if not isinstance(token, str) or not token:
        return {"R": -1}

    dbcnf = loadDatabaseSettings("db.json")

    try:
        db = mysql.connector.connect(
            host="localhost",
            port=dbcnf["port"],
            database=dbcnf["dbname"],
            user=dbcnf["user"],
            password=dbcnf["password"]
        )
    except Exception:
        return {"R": -2}

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """SELECT U.email, U.totp_secret, U.totp_enabled
                   FROM Usuario U
                   JOIN AccesoToken A ON A.id_Usuario = U.id
                   WHERE A.token = %s""",
                (token,)
            )

            usuario = cursor.fetchone()

            if not usuario:
                return {"R": -3}

            email, secreto, activado = usuario

            if activado == 1 or not secreto:
                return {"R": -4}

            uri = pyotp.TOTP(secreto).provisioning_uri(
                name=email,
                issuer_name="WebAPI-R004"
            )

            return {"R": 0, "D": uri}

    except Exception:
        return {"R": -2}

    finally:
        db.close()

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=False)
