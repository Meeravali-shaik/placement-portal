from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app import supabase

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hashes a password using Argon2."""
    return ph.hash(password)

def verify_password(hash_str: str, password: str) -> bool:
    """Verifies a password against an Argon2 hash."""
    try:
        return ph.verify(hash_str, password)
    except VerifyMismatchError:
        return False

def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticates a user by email and password.
    Returns the user record if successful, or None if failed.
    """
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        users = response.data
        if not users:
            return None
        
        user = users[0]
        if verify_password(user['password_hash'], password):
            return user
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def create_user(name: str, email: str, password: str, role: str) -> dict:
    """
    Creates a new user with a hashed password.
    """
    password_hash = hash_password(password)
    try:
        response = supabase.table('users').insert({
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'role': role
        }).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
