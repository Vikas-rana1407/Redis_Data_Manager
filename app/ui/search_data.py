import gradio as gr

def render_search_data_tab():
    with gr.Column():
        with gr.Tab("Book"):
            gr.Markdown("### Search by Name (Books)")
            book_search_input = gr.Textbox(label="Enter book name...")
            book_search_btn = gr.Button("Search Book", variant="primary")
            book_keys = gr.Textbox(label="Founded Book Key", interactive=False, show_copy_button=True)
            book_output = gr.Code(label="Book Data")

        with gr.Tab("Video"):
            gr.Markdown("### Search by Title or URL (Videos)")
            video_search_input = gr.Textbox(label="Enter YouTube URL or video title...")
            video_search_btn = gr.Button("Search Video", variant="primary")
            video_keys = gr.Textbox(label="Founded Video Key", interactive=False, show_copy_button=True)
            video_output = gr.Code(label="Video Data")
