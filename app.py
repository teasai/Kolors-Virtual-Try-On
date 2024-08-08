import os
import cv2
from PIL import Image
import gradio as gr
import numpy as np
import random
import base64
import requests


def start_tryon(person_img, garment_img, seed, randomize_seed):
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    encoded_person_img = cv2.imencode('.jpg', person_img)[1].tobytes()
    encoded_person_img = base64.b64encode(encoded_person_img).decode('utf-8')
    encoded_garment_img = cv2.imencode('.jpg', garment_img)[1].tobytes()
    encoded_garment_img = base64.b64encode(encoded_garment_img).decode('utf-8')
    
    return person_img, seed

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
            imgs = gr.Image(label="Person image", sources='upload', type="numpy")
            # category = gr.Dropdown(label="Garment category", choices=['upper_body', 'lower_body', 'dresses'],  value="upper_body")
            example = gr.Examples(
                inputs=imgs,
                examples_per_page=10,
                examples=human_list_path
            )
        with gr.Column():
            garm_img = gr.Image(label="Garment image", sources='upload', type="numpy")
            example = gr.Examples(
                inputs=garm_img,
                examples_per_page=10,
                examples=garm_list_path)
        with gr.Column():
            image_out = gr.Image(label="Output", show_share_button=False)
            seed_used = gr.Number(label="Seed Used")
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

    try_button.click(fn=start_tryon, inputs=[imgs, garm_img, seed, randomize_seed], outputs=[image_out, seed_used], api_name='tryon')

ip = requests.get('http://ifconfig.me/ip', timeout=1).text.strip()
print("ip address alibaba", ip)
Tryon.queue(max_size=10).launch()
