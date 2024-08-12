import os
import cv2
from PIL import Image
import gradio as gr
import numpy as np
import random
import base64
import requests
import json


def start_tryon(person_img, garment_img, seed, randomize_seed):
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    encoded_person_img = cv2.imencode('.jpg', cv2.cvtColor(person_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_person_img = base64.b64encode(encoded_person_img).decode('utf-8')
    encoded_garment_img = cv2.imencode('.jpg', cv2.cvtColor(garment_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_garment_img = base64.b64encode(encoded_garment_img).decode('utf-8')

    url = "https://" + os.environ['tryon_url']
    token = os.environ['token']
    cookie = os.environ['Cookie']
    
    headers = {'Content-Type': 'application/json', 'token': token, 'Cookie': cookie}
    data = {
        "clothImage": encoded_garment_img,
        "humanImage": encoded_person_img,
        "seed": seed
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("response code", response.status_code)
    result_img = None
    if response.status_code == 200:
        result = response.json()['result']
        status = result['status']
        if status == "success":
            result = base64.b64decode(result['result'])
            result_np = np.frombuffer(result, np.uint8)
            result_img = cv2.imdecode(result_np, cv2.IMREAD_UNCHANGED)
            result_img = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
            info = "Success"
        else:
            info = "Try again latter"
    else:
        info = "URL error"

    return result_img, seed, info

MAX_SEED = 999999

example_path = os.path.join(os.path.dirname(__file__), 'assets')

garm_list = os.listdir(os.path.join(example_path,"cloth"))
garm_list_path = [os.path.join(example_path,"cloth",garm) for garm in garm_list]

human_list = os.listdir(os.path.join(example_path,"human"))
human_list_path = [os.path.join(example_path,"human",human) for human in human_list]

css="""
#col-left {
    margin: 0 auto;
    max-width: 380px;
}
#col-mid {
    margin: 0 auto;
    max-width: 380px;
}
#col-right {
    margin: 0 auto;
    max-width: 520px;
}
#col-showcase {
    margin: 0 auto;
    max-width: 1000px;
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
        with gr.Column(elem_id = "col-left"):
            imgs = gr.Image(label="Person image", sources='upload', type="numpy")
            # category = gr.Dropdown(label="Garment category", choices=['upper_body', 'lower_body', 'dresses'],  value="upper_body")
            example = gr.Examples(
                inputs=imgs,
                examples_per_page=10,
                examples=human_list_path
            )
        with gr.Column(elem_id = "col-mid"):
            garm_img = gr.Image(label="Garment image", sources='upload', type="numpy")
            example = gr.Examples(
                inputs=garm_img,
                examples_per_page=10,
                examples=garm_list_path)
        with gr.Column(elem_id = "col-right"):
            image_out = gr.Image(label="Output", show_share_button=False)
            with gr.Row():
                seed_used = gr.Number(label="Seed Used")
                result_info = gr.Text(label="Info")
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

    try_button.click(fn=start_tryon, inputs=[imgs, garm_img, seed, randomize_seed], outputs=[image_out, seed_used, result_info], api_name='tryon')

    gr.HTML("""
    <div style="display: flex; justify-content: center; align-items: center; text-align: center;">
        <div>
    <h1>Show Case</h1>
        </div>
    </div>
    """)
    with gr.Column(elem_id = "col-showcase"):
        with gr.Row():
            image1  = gr.Image(label="Model", scale=1, value="assets/examples/model1.png", show_share_button=False, type="numpy")
            image2  = gr.Image(label="Garment", scale=1, value="assets/examples/garment1.png", show_share_button=False, type="numpy")
            image3  = gr.Image(label="Result", scale=1, value="assets/examples/result1.png", show_share_button=False, type="numpy")
        show_case = gr.Examples(
            examples=[
                ["assets/examples/model1.png", "assets/examples/garment1.png", "assets/examples/result1.png"],
                ["assets/examples/model2.png", "assets/examples/garment2.png", "assets/examples/result2.png"]
            ],
            inputs=[image1, image2, image3],
            label=None,
            fn = start_tryon(image1, image2, seed, randomize_seed),
            outputs = [image_out, seed_used, result_info],
            cache_examples = "lazy"
        )


ip = requests.get('http://ifconfig.me/ip', timeout=1).text.strip()
print("ip address", ip)
Tryon.queue(max_size=10).launch()
