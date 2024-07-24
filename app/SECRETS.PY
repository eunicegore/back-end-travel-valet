import os
import secrets

# Generate a secure random key
secret_key = secrets.token_hex(24)
print(secret_key)

jwt_secret_key = secrets.token_hex(32)
print(f"JWT Secret Key: {jwt_secret_key}")
