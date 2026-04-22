
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.fernet import Fernet

# CONFIG
KEY_PASSWORD = b"ultra_safe_password"  #protects private key
VAULT_FILE = "vault.file"
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"
INVALID_PASSWORD = b"i_am_an_inavlid_password" #for testing purposes

#Create keys
def generate_keys():
    print("[+] Generating RSA keys (2048 bits)...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Save ciphered key with password
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(KEY_PASSWORD)
        ))
    
    # Save public key 
    public_key = private_key.public_key()
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print("[OK] Keys saved in .pem")

# Cipher keys
def cipher(file_name):
    print(f"[+] Encoding {file_name}...")

    # Generate an AES random key (Fernet)
    aes_key = Fernet.generate_key()
    f_aes = Fernet(aes_key)

    # Read original file 
    with open(file_name, "rb") as f:
        data = f.read()
    
    # Cipher data with AES
    ciphered_data = f_aes.encrypt(data)

    # Cipher AES key with RSA Public key 
    with open(PUBLIC_KEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    
    ciphered_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Save packet
    with open(VAULT_FILE, "wb") as f:
        f.write(ciphered_aes_key + b"---SEPARATOR---" + ciphered_data)
    
    print (f"[OK] File is protected at {VAULT_FILE}")

# Decipher
def decipher():
    print(f"[+] Trying to decipher {VAULT_FILE}...")

    # Read vault and separate sections
    with open(VAULT_FILE, "rb") as f:
        content = f.read()
    ciphered_aes_key, ciphered_data = content.split(b"---SEPARATOR---")

    # Load private key (asks for password)
    with open(PRIVATE_KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=KEY_PASSWORD)

    # Decipher AES key
    plain_aes_key = private_key.decrypt(
        ciphered_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decipher final data
    f_aes = Fernet(plain_aes_key)
    original_data = f_aes.decrypt(ciphered_data)

    with open("restored.txt", "wb") as f:
        f.write(original_data)
    print("[OK] Content is restored in 'restored.txt")

# Flow trial
if __name__ == "__main__":
    # create test file
    with open("secret.txt", "w") as f:
        f.write("Ultra secret message for my project")

    generate_keys()
    cipher("secret.txt")
    decipher()
