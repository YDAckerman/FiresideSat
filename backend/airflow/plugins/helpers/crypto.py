from airflow.models import Variable
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


class Crypto:

    def __init__(self):

        self.rsa_private_key = serialization.load_pem_private_key(
            Variable.get("rsa_private_key_pem").encode(),
            None
        )

    def decrypt(self, ciphertext):

        message = self.rsa_private_key.decrypt(
            bytes(ciphertext),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return message.decode(encoding="utf-8")
