
# Third-party imports
import gradio as gr

# App imports
from app.utils.common import search_book_by_title, search_video_by_title_or_url
from app.utils.redis_manager import redis_client
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

def handle_book_search(book_title):
    """
    Handles book search by title and logs the search action.
    """
    logger.info(f"Searching for book: {book_title}")
    keys, data = search_book_by_title(book_title)
    if not keys:
        logger.info(f"No book results found for: {book_title}")
        return gr.Dropdown(choices=[], value=None), data[0] if data else {"message": "❌ No related book results found."}
    return gr.Dropdown(choices=keys, value=keys[0]), data[0]

def handle_video_search(input_text):
    """
    Handles video search by title or URL and logs the search action.
    """
    logger.info(f"Searching for video: {input_text}")
    keys, data = search_video_by_title_or_url(input_text)
    if not keys:
        logger.info(f"No video results found for: {input_text}")
        return gr.Dropdown(choices=[], value=None), data[0] if data else {"message": "❌ No related video results found."}
    return gr.Dropdown(choices=keys, value=keys[0]), data[0]

def handle_book_dropdown_change(selected_key):
    """
    Loads book data for the selected key and logs the action.
    """
    if not selected_key:
        return None
    logger.info(f"Loading book data for key: {selected_key}")
    return redis_client.json().get(selected_key)

def handle_video_dropdown_change(selected_key):
    """
    Loads video data for the selected key and logs the action.
    """
    if not selected_key:
        return None
    logger.info(f"Loading video data for key: {selected_key}")
    return redis_client.json().get(selected_key)

def render_search_data_tab():
    """
    Renders the Search Data tab for books and videos.
    """
    with gr.Column():
        with gr.Tab("📚 Book"):
            gr.Markdown("### Search by Book Title")
            book_input = gr.Textbox(label="Enter book title...")
            book_search_btn = gr.Button("🔍 Search Book", variant="primary")

            book_key_dropdown = gr.Dropdown(label="Found Book Keys", choices=[], interactive=True)
            book_data_display = gr.Json(label="Book Data")

            book_search_btn.click(
                handle_book_search,
                inputs=book_input,
                outputs=[book_key_dropdown, book_data_display],
            )

            book_key_dropdown.change(
                handle_book_dropdown_change,
                inputs=book_key_dropdown,
                outputs=book_data_display
            )

        with gr.Tab("🎥 Video"):
            gr.Markdown("### Search by YouTube Title or URL")
            video_input = gr.Textbox(label="Enter YouTube URL or video title...")
            video_search_btn = gr.Button("🔍 Search Video", variant="primary")

            video_key_dropdown = gr.Dropdown(label="Found Video Keys", choices=[], interactive=True)
            video_data_display = gr.Json(label="Video Data")

            video_search_btn.click(
                handle_video_search,
                inputs=video_input,
                outputs=[video_key_dropdown, video_data_display],
            )

            video_key_dropdown.change(
                handle_video_dropdown_change,
                inputs=video_key_dropdown,
                outputs=video_data_display
            )
