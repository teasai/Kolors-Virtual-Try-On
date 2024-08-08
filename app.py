import sys
import os
import io
from PIL import Image
import gradio as gr
import numpy as np
import random

example_path = os.path.join(os.path.dirname(__file__), 'assets')

MAX_SEED = 999999

def start_tryon(imgs, garm_img, garment_des, seed):
    
    return None

garm_list = os.listdir(os.path.join(example_path,"cloth"))
garm_list_path = [os.path.join(example_path,"cloth",garm) for garm in garm_list]

human_list = os.listdir(os.path.join(example_path,"human"))
human_list_path = [os.path.join(example_path,"human",human) for human in human_list]

css="""
#col-left {
    margin: 0 auto;
    max-width: 600px;
}
#col-right {
    margin: 0 auto;
    max-width: 750px;
}
#button {
    color: blue;
}
"""

def load_description(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

with gr.Blocks(css=css) as Tryon:
    gr.HTML(load_description("assets/title.md"))
    with gr.Row():
        with gr.Column():
            imgs = gr.Image(label="Person image", sources='upload', type="pil")
            # category = gr.Dropdown(label="Garment category", choices=['upper_body', 'lower_body', 'dresses'],  value="upper_body")
            example = gr.Examples(
                inputs=imgs,
                examples_per_page=10,
                examples=human_list_path
            )
        with gr.Column():
            garm_img = gr.Image(label="Garment image", sources='upload', type="pil")
            example = gr.Examples(
                inputs=garm_img,
                examples_per_page=8,
                examples=garm_list_path)
        with gr.Column():
            image_out = gr.Image(label="Output", elem_id="output-img",show_share_button=False)
            try_button = gr.Button(value="Try-on")


    with gr.Column():
        with gr.Accordion(label="Advanced Settings", open=False):
            with gr.Row():
                seed = gr.Number(label="Seed", minimum=-1, maximum=2147483647, step=1, value=None)

    try_button.click(fn=start_tryon, inputs=[imgs, garm_img, seed], outputs=[image_out], api_name='tryon')

Tryon.queue(max_size=10).launch()
