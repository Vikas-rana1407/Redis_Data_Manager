import gradio as gr

def search_data_book_ui():
    with gr.TabItem("Book"):
        search_book_title = gr.Textbox(label="Book Title", placeholder="Enter book title or description...")
        search_book_btn = gr.Button("Search Book", variant="primary")
        book_sim_keys = gr.Dropdown(choices=[], label="Found Book Keys", interactive=True, allow_custom_value=False)
        book_sim_data = gr.Code(label="Book Data", language="json")
        return search_book_title, search_book_btn, book_sim_keys, book_sim_data

def search_data_video_ui():
    with gr.TabItem("Video"):
        search_video_query = gr.Textbox(label="Video Title or URL", placeholder="Enter YouTube URL or video title...")
        search_video_btn = gr.Button("Search Video", variant="primary")
        video_sim_keys = gr.Dropdown(choices=[], label="Found Video Keys", interactive=True, allow_custom_value=False)
        video_sim_data = gr.Code(label="Video Data", language="json")
        return search_video_query, search_video_btn, video_sim_keys, video_sim_data
