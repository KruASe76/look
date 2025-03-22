import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from sqlalchemy import URL

POSTGRES_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

PRIVATE_KEY: RSAPrivateKey = serialization.load_ssh_private_key(
    data=Path("keys/id_rsa").read_bytes(),
    password=None,
)
PUBLIC_KEY: RSAPublicKey = serialization.load_ssh_public_key(
    data=Path("keys/id_rsa.pub").read_bytes()
)
