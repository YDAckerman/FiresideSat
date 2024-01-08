from cryptography.hazmat.primitives import serialization
from airflow.models import Variable


class Crypto:

    def __init__(self):

        self.rsa_private_key = serialization.load_pem_private_key(
            Variable.get("rsa_private_key_pem"),
            password=None,
        )

    def decrypt(self, ciphertext):

        return self.rsa_private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

