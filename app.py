import PIL
import requests
import torch
from flask import Flask, request, jsonify, send_file
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler
import io

app = Flask(__name__)

# Load model
model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(model_id, torch_dtype=torch.float16, safety_checker=None)
pipe.to("cuda")
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

def download_image(url):
    image = PIL.Image.open(requests.get(url, stream=True).raw)
    image = PIL.ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    return image

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    image_url = data.get('url')
    prompt = data.get('prompt')

    # Download the image
    image = download_image(image_url)

    # Generate new image
    images = pipe(prompt, image=image, num_inference_steps=10, image_guidance_scale=1).images
    
    # Save the generated image to a BytesIO object
    img_byte_arr = io.BytesIO()
    images[0].save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)  # Go to the beginning of the BytesIO object
    
    return send_file(img_byte_arr, mimetype='image/png')

@app.route('/output', methods=['GET'])
def get_image():
    # This is just a placeholder; implement your logic to return the generated image if needed.
    return jsonify({"message": "This is a placeholder for the output endpoint."})

if __name__ == '__main__':
    app.run(debug=True)
