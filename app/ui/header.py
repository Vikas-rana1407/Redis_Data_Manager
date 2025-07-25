import gradio as gr

ZUMLO_LOGO_URL = "https://zumlo.co/assets/images/zumlo-logo.png"

def render_header():
    return gr.HTML(
        '''<div style="background: #ff6600; display: flex; align-items: center; justify-content: space-between; padding: 1.5em 2em 1em 2em; border-radius: 8px; margin-bottom: 1.5em;">
            <div style="text-align: left;">
                <h1 style="margin-bottom: 0.2em; color: #fff;">LLM Instruction Manager</h1>
                <div style="font-size: 1.1em; color: #fff;">Manage, track, and deploy your AI assistant instructions across environments.</div>
            </div>
            <img src="https://zumlo.co/assets/images/zumlo-logo.png" alt="Zumlo Logo" style="height: 60px; margin-left: 2em;" />
        </div>'''
    )
