
# Third-party imports
import gradio as gr

# App imports
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

def render_header():
    """
    Renders the application header for the Gradio UI.
    """
    logger.info("Rendering Gradio UI header.")
    return gr.HTML(
        '''
        <div style="
            background: #ff5e00;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.5em 2em 1em 2em;
            border-radius: 8px;
            margin-bottom: 1.5em;
        ">
            <div style="text-align: left;">
                <h1 style="margin: 0 0 0.2em 0; color: #fff; font-size: 1.9em;">
                    Redis Data Manager
                </h1>
                <p style="margin: 0; font-size: 1.1em; color: #fff;">
                    Effortlessly manage, query, and maintain your book and video data in Redis.
                </p>
            </div>
            <img src="https://zumlo.co/assets/images/zumlo-logo.png"
                 alt="Zumlo Logo"
                 style="height: 60px; margin-left: 2em;" />
        </div>
        '''
    )
