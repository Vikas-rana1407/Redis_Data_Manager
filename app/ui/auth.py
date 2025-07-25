# Standard library imports
import os
from datetime import datetime, timedelta
# Third-party imports
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt
import gradio as gr

# Password hashing context for secure password storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hash a password for storage.
    """
    return pwd_context.hash(password)

from typing import Dict, Any

def create_access_token(data: Dict[str, Any]):
    """
    Create a JWT access token with a 7-day expiry.
    """
    to_encode = data.copy()
    from datetime import timezone
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_SECRET_KEY", "your-secret-key"), algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    """
    Verify a JWT token and return the payload if valid.
    """
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY", "your-secret-key"), algorithms=["HS256"])
        return payload
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def setup_auth(app):
    """
    Wraps the Gradio app with a login UI and JWT-based authentication.
    """
    load_dotenv()
    # Get the admin password from env and hash it if it's not already hashed
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    if not admin_password.startswith("$2b$"):  # Check if it's not already a bcrypt hash
        admin_password = get_password_hash(admin_password)

    def login(username, password):
        """
        Handle user login and return a JWT token if successful.
        """
        if (username == os.getenv("ADMIN_USERNAME", "admin") and 
            verify_password(password, admin_password)):
            token = create_access_token({"username": username})
            return gr.update(visible=True), gr.update(visible=False), token
        return gr.update(visible=False), gr.update(visible=True), None

    def check_auth(token):
        """
        Check if the provided token is valid and update UI visibility.
        """
        if token and verify_token(token):
            return gr.update(visible=True), gr.update(visible=False)
        return gr.update(visible=False), gr.update(visible=True)

    from app.ui.header import render_header
    with gr.Blocks() as auth_ui:
        token = gr.State(None)
        with gr.Row():
            with gr.Column(scale=1, min_width=0):
                username = gr.Textbox(label="username", placeholder="Type here...")
                password = gr.Textbox(label="password", type="password", placeholder="Type here...")
                login_btn = gr.Button("Login", elem_id="login-btn", variant="primary")
                status = gr.Markdown(visible=False)
        app_box = gr.Group(visible=False)
        with app_box:
            app.render()


        def login_wrapper(username_val, password_val):
            main_visible, login_visible, token_val = login(username_val, password_val)
            status_msg = "Login successful!" if main_visible else "Invalid credentials."
            return (
                main_visible,   # app_box.visible
                login_visible,  # username.visible
                login_visible,  # password.visible
                login_visible,  # login_btn.visible
                token_val,      # token
                status_msg      # status (Markdown value)
            )

        def check_auth_wrapper(token_val):
            main_visible, login_visible = check_auth(token_val)
            status_msg = "Authenticated" if main_visible else "Please login."
            return (
                main_visible,   # app_box.visible
                login_visible,  # username.visible
                login_visible,  # password.visible
                login_visible,  # login_btn.visible
                status_msg      # status (Markdown value)
            )

        # Check auth on page load
        auth_ui.load(
            fn=check_auth_wrapper,
            inputs=[token],
            outputs=[app_box, username, password, login_btn, status]
        )

        # Handle login
        login_btn.click(
            fn=login_wrapper,
            inputs=[username, password],
            outputs=[app_box, username, password, login_btn, token, status]
        )

    return auth_ui