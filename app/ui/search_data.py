import gradio as gr

def render_search_data_tab():
    with gr.Column():
        with gr.Tab("Book"):
            gr.Markdown("### Search by Title or Tags (Books)")
            book_search_input = gr.Textbox(label="Enter title or tags")
            book_search_btn = gr.Button("Search Book", variant="primary")
            book_keys = gr.Dropdown(label="Found Book Keys", choices=[])
            book_output = gr.Code(label="Book Data")

        with gr.Tab("Video"):
            gr.Markdown("### Search by Title or Tags (Videos)")
            video_search_input = gr.Textbox(label="Enter YouTube URL or video title...")
            video_search_btn = gr.Button("Search Video", variant="primary")
            video_keys = gr.Dropdown(label="Found Video Keys", choices=[])
            video_output = gr.Code(label="Video Data")
