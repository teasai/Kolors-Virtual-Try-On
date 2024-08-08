import sys
import os
import io
from PIL import Image
import gradio as gr
import numpy as np
import random


def start_tryon(imgs, garm_img, garment_des, seed):
    
    return None

MAX_SEED = 999999

example_path = os.path.join(os.path.dirname(__file__), 'assets')

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
                examples_per_page=10,
                examples=garm_list_path)
        with gr.Column():
            image_out = gr.Image(label="Output", show_share_button=False)
            try_button = gr.Button(value="Try-on", elem_id="button")


    with gr.Column():
        with gr.Accordion(label="Advanced Settings", open=False):
            seed = gr.Slider(
                    label="Seed",
                    minimum=0,
                    maximum=MAX_SEED,
                    step=1,
                    value=0,
                )
            randomize_seed = gr.Checkbox(label="Randomize seed", value=True)

    try_button.click(fn=start_tryon, inputs=[imgs, garm_img, seed], outputs=[image_out], api_name='tryon')

Tryon.queue(max_size=10).launch()
