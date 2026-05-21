"""
Cifrado simetrico de datos sensibles del metodo de pago.

Se usa Fernet (AES-128-CBC + HMAC-SHA256) para cifrar el identificador completo
(numero de tarjeta, CLABE, numero de cuenta). En paralelo se calcula un
fingerprint HMAC-SHA256 con una pimienta secreta para poder detectar duplicados
del mismo identificador sin necesidad de descifrar nada.

El fingerprint se calcula sobre el valor normalizado (solo digitos y mayusculas)
para que dos representaciones equivalentes del mismo dato choquen como duplicado.
"""

import hashlib
import hmac
import re

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


_fernet = Fernet(settings.FERNET_KEY.encode())


def encrypt_identifier(plain: str) -> str:
    """Cifra el identificador y devuelve el ciphertext en base64 url-safe."""
    return _fernet.encrypt(plain.encode()).decode()


def decrypt_identifier(ciphertext: str) -> str:
    """Descifra el identificador. Lanza ValueError si el token es invalido."""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("No se pudo descifrar el identificador") from exc


def normalize_identifier(plain: str) -> str:
    """Quita espacios, guiones y normaliza a mayusculas."""
    return re.sub(r"[\s\-]", "", plain).upper()


def fingerprint_identifier(plain: str) -> str:
    """
    HMAC-SHA256 del identificador normalizado. Se usa como columna indexable
    para detectar duplicados sin exponer el dato.
    """
    normalized = normalize_identifier(plain).encode()
    pepper = settings.FINGERPRINT_PEPPER.encode()
    return hmac.new(pepper, normalized, hashlib.sha256).hexdigest()


def mask_identifier(plain: str, visible_last: int = 4) -> str:
    """Devuelve una representacion enmascarada (ej. **** **** **** 1234)."""
    normalized = normalize_identifier(plain)
    if len(normalized) <= visible_last:
        return normalized
    masked = "*" * (len(normalized) - visible_last) + normalized[-visible_last:]
    # Se reagrupa cada 4 caracteres para mejorar la legibilidad en frontend
    return " ".join(masked[i:i + 4] for i in range(0, len(masked), 4))


def last_four(plain: str) -> str:
    normalized = normalize_identifier(plain)
    return normalized[-4:] if len(normalized) >= 4 else normalized
