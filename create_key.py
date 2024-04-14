from pathlib import Path

from Crypto.PublicKey import RSA

certsfolder = Path('certs/').exists()
if not certsfolder:
    certsfolder = Path('certs/').mkdir()  # type: ignore


def generate(bit_size):
    keys = RSA.generate(bit_size)
    return keys


keys = generate(2048)

print('Generate RSA private key')
with open('certs/jwt-private.key', 'wb') as file:
    file.write(keys.export_key())

print('Generate RSA public key')
with open('certs/jwt-public.key', 'wb') as file:
    file.write(keys.publickey().export_key('PEM'))
