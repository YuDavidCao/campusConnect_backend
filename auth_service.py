from firebase_admin import auth
import email_service
import requests

from env import FIREBASE_API_KEY

def create_user_with_email_and_password(email: str, password: str):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        print('Successfully created new user:', user.uid)
        return user
    except Exception as e:
        print('Error creating new user:', e)
        return None
    
def signIn_user_with_email_and_password(email: str, password: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    return response.json()

def verify_user_email(uid: str):
    try:
        auth.update_user(
            uid,
            email_verified=True,
        )
        return True
    except:
        return False
    

def change_password(uid: str, newPassword: str):
    try:
        auth.update_user(
            uid,
            password=newPassword,
        )
        return True
    except:
        return False
        

