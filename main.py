import os
from dotenv import load_dotenv
import gradio as gr
from app.ui.ui import launch


def main():
    """
    Entry point for the Redis Data Manager application.
    Loads environment variables and launches the Gradio UI.
    """
    load_dotenv()
    print("Environment variables loaded")
    print(f"Server will run on: http://127.0.0.1:7860")
    print(f"Admin username: {os.getenv('ADMIN_USERNAME', 'admin')}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    # Launch the Gradio app
    launch()

if __name__ == "__main__":
    main()