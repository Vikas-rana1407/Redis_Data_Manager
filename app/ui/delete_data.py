import gradio as gr

def delete_data_book_ui():
    with gr.TabItem("Book"):
        del_book_key = gr.Textbox(label="Book Redis Key to Delete")
        del_book_btn = gr.Button("Delete Book", variant="primary")
        del_book_status = gr.Markdown()
        return del_book_key, del_book_btn, del_book_status

def delete_data_video_ui():
    with gr.TabItem("Video"):
        del_video_key = gr.Textbox(label="Video Redis Key to Delete")
        del_video_btn = gr.Button("Delete Video", variant="primary")
        del_video_status = gr.Markdown()
        return del_video_key, del_video_btn, del_video_status
