
# Third-party imports
import gradio as gr

# App imports
from app.utils.common import delete_multiple_keys
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

def handle_book_deletion(book_keys: str) -> str:
    """
    Handles deletion of book keys and logs the action.
    """
    logger.info(f"Deleting book keys: {book_keys}")
    return delete_multiple_keys(book_keys, expected_prefix="book:")

def handle_video_deletion(video_keys: str) -> str:
    """
    Handles deletion of video keys and logs the action.
    """
    logger.info(f"Deleting video keys: {video_keys}")
    return delete_multiple_keys(video_keys, expected_prefix="video:")

def render_delete_data_tab():
    """
    Renders the Delete Data tab for books and videos.
    """
    with gr.Column():
        with gr.Tab("📚Book"):
            gr.Markdown("### Delete Book(s) from Redis")
            book_delete_key = gr.Textbox(
                label="Enter a key or comma-separated Redis keys (e.g., book:abc, book:def)", 
                lines=2
            )
            book_delete_btn = gr.Button("Delete Book(s)", variant="primary")
            book_delete_status = gr.Markdown()

            book_delete_btn.click(
                fn=handle_book_deletion,
                inputs=[book_delete_key],
                outputs=[book_delete_status]
            )

            gr.Markdown("""
---
### ℹ️ **Book Deletion Instructions**
- **Each key must start with `book:`**
- Keys are unique UUIDs, e.g., `book:92f1e63a-8c10-4b4c-9c11-30204d3ac40f`
- You can find book keys on the **Search Data** tab by looking up book titles.
- **To delete multiple books**, separate keys with commas:  
  `book:abc, book:def, book:ghi`
""")

        with gr.Tab("🎥Video"):
            gr.Markdown("### Delete Video(s) from Redis")
            video_delete_key = gr.Textbox(
                label="Enter a key or comma-separated Redis keys (e.g., video:xyz, video:123)", 
                lines=2
            )
            video_delete_btn = gr.Button("Delete Video(s)", variant="primary")
            video_delete_status = gr.Markdown()

            video_delete_btn.click(
                fn=handle_video_deletion,
                inputs=[video_delete_key],
                outputs=[video_delete_status]
            )

            gr.Markdown("""
---
### ℹ️ **Video Deletion Instructions**
- **Each key must start with `video:`**
- The key is the last part of the YouTube URL:  
  e.g., from `https://www.youtube.com/watch?v=2l_2k5KrZmo` → `video:2l_2k5KrZmo`
- You can find video keys in the **Search Data** tab.
- **To delete multiple videos**, separate keys with commas:  
  `video:abc123, video:def456`
""")
