import gradio as gr

def render_delete_data_tab():
    with gr.Column():
        with gr.Tab("Book"):
            gr.Markdown("### Delete Book from Redis by Key")
            book_delete_key = gr.Textbox(label="Redis Key to Delete Book data")
            book_delete_btn = gr.Button("Delete Book", variant="primary")

        with gr.Tab("Video"):
            gr.Markdown("### Delete Video from Redis by Key")
            video_delete_key = gr.Textbox(label="Redis Key to Delete Video data")
            video_delete_btn = gr.Button("Delete Video", variant="primary")
