import os
import bcrypt
import base64

from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

load_dotenv()

PEPPER = os.getenv("PEPPER")
AES_KEY = os.getenv("AES_KEY").encode()


def hash_password(password: str):

    password_pepper = password + PEPPER

    hashed = bcrypt.hashpw(
        password_pepper.encode(),
        bcrypt.gensalt()
    )

    return hashed.decode()


def verify_password(password: str, hashed_password: str):

    password_pepper = password + PEPPER

    return bcrypt.checkpw(
        password_pepper.encode(),
        hashed_password.encode()
    )


def encrypt_data(data: str):

    cipher = AES.new(AES_KEY, AES.MODE_CBC)

    encrypted = cipher.encrypt(
        pad(data.encode(), AES.block_size)
    )

    iv = base64.b64encode(cipher.iv).decode()

    encrypted_text = base64.b64encode(
        encrypted
    ).decode()

    return iv + ":" + encrypted_text


def decrypt_data(encrypted_data: str):

    iv, encrypted_text = encrypted_data.split(":")

    iv = base64.b64decode(iv)

    encrypted_text = base64.b64decode(
        encrypted_text
    )

    cipher = AES.new(
        AES_KEY,
        AES.MODE_CBC,
        iv
    )

    decrypted = unpad(
        cipher.decrypt(encrypted_text),
        AES.block_size
    )

    return decrypted.decode()