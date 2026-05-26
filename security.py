import base64
import hashlib
import hmac
import os

HASH_ALGORITMO = "pbkdf2_sha256"
HASH_ITERACOES = 100_000


def gerar_hash_senha(senha):
    """Gera hash PBKDF2 com salt aleatório para armazenar no banco."""
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, HASH_ITERACOES)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(hash_bytes).decode("utf-8")
    return f"{HASH_ALGORITMO}${HASH_ITERACOES}${salt_b64}${hash_b64}"


def verificar_hash_senha(senha_digitada, senha_armazenada):
    """Valida senha digitada contra o hash salvo."""
    try:
        algoritmo, iteracoes, salt_b64, hash_b64 = senha_armazenada.split("$", 3)
        if algoritmo != HASH_ALGORITMO:
            return False

        salt = base64.b64decode(salt_b64.encode("utf-8"))
        hash_original = base64.b64decode(hash_b64.encode("utf-8"))

        hash_teste = hashlib.pbkdf2_hmac(
            "sha256",
            senha_digitada.encode("utf-8"),
            salt,
            int(iteracoes),
        )
        return hmac.compare_digest(hash_original, hash_teste)
    except (ValueError, TypeError):
        return False
