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
    if person_img is None or garment_img is None:
        return None, None, "Empty image"
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    encoded_person_img = cv2.imencode('.jpg', cv2.cvtColor(person_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_person_img = base64.b64encode(encoded_person_img).decode('utf-8')
    encoded_garment_img = cv2.imencode('.jpg', cv2.cvtColor(garment_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_garment_img = base64.b64encode(encoded_garment_img).decode('utf-8')

    url = "https://" + os.environ['tryon_url']
    token = os.environ['token']
    
    headers = {'Content-Type': 'application/json', 'token': token}
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
            print(response.json()['result'])
            info = "Try again latter"
    else:
        print(response.json()['result'])
        info = "URL error, pleace contact the admin"

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
    max-width: 1100px;
}
#button {
    color: blue;
}
"""

def load_description(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def change_imgs(image1, image2):
    return image1, image2

with gr.Blocks(css=css) as Tryon:
    gr.HTML(load_description("assets/title.md"))
    with gr.Row():
        with gr.Column(elem_id = "col-left"):
            imgs = gr.Image(label="Person image", sources='upload', type="numpy")
            # category = gr.Dropdown(label="Garment category", choices=['upper_body', 'lower_body', 'dresses'],  value="upper_body")
            example = gr.Examples(
                inputs=imgs,
                examples_per_page=12,
                examples=human_list_path
            )
        with gr.Column(elem_id = "col-mid"):
            garm_img = gr.Image(label="Garment image", sources='upload', type="numpy")
            example = gr.Examples(
                inputs=garm_img,
                examples_per_page=12,
                examples=garm_list_path)
        with gr.Column(elem_id = "col-right"):
            image_out = gr.Image(label="Output", show_share_button=False)
            with gr.Row():
                seed = gr.Slider(
                    label="Seed",
                    minimum=0,
                    maximum=MAX_SEED,
                    step=1,
                    value=0,
                )
                randomize_seed = gr.Checkbox(label="Random seed", value=True)
            with gr.Row():
                seed_used = gr.Number(label="Seed Used")
                result_info = gr.Text(label="Response")
            try_button = gr.Button(value="Run", elem_id="button")


    try_button.click(fn=start_tryon, inputs=[imgs, garm_img, seed, randomize_seed], outputs=[image_out, seed_used, result_info], api_name='tryon')

    gr.HTML("""
    <div style="display: flex; justify-content: center; align-items: center; text-align: center;">
        <div>
    <h1>Show Case</h1>
        </div>
    </div>
    """)
    with gr.Column(elem_id = "col-showcase"):
        show_case = gr.Examples(
            examples=[
                ["assets/examples/model1.png", "assets/examples/garment1.png", "assets/examples/result1.png"],
                ["assets/examples/model2.png", "assets/examples/garment2.png", "assets/examples/result2.png"],
                ["assets/examples/model3.png", "assets/examples/garment3.png", "assets/examples/result3.png"],
            ],
            inputs=[imgs, garm_img, image_out],
            label=None
        )

ip = requests.get('http://ifconfig.me/ip', timeout=1).text.strip()
print("ip address", ip)
Tryon.queue(max_size=10).launch()
