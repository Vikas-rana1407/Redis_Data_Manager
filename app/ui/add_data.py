import gradio as gr

def add_data_book_ui():
    with gr.TabItem("Book"):
        book_file = gr.File(label="Upload Book CSV")
        book_upload_btn = gr.Button("Process & Save Books", variant="primary")
        book_status = gr.Markdown()
        return book_file, book_upload_btn, book_status

def add_data_video_ui():
    with gr.TabItem("Video"):
        video_url = gr.Textbox(label="YouTube URL")
        video_add_btn = gr.Button("Process & Save Video", variant="primary")
        video_status = gr.Markdown()
        return video_url, video_add_btn, video_status
