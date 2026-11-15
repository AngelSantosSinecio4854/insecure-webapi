
import bcrypt
import pyotp

def generar_hash(password):
    password_bytes = password.encode("utf-8")

    hash_bytes = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=12)
    )

    return hash_bytes.decode("utf-8")


def verificar_password(password, hash_guardado):
    password_bytes = password.encode("utf-8")
    hash_bytes = hash_guardado.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hash_bytes)

def verificar_totp(secreto, codigo):
    if not isinstance(codigo, str):
        return False

    if len(codigo) != 6 or not codigo.isdigit():
        return False

    return pyotp.TOTP(secreto).verify(codigo, valid_window=1)
