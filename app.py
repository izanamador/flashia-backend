import os
import PIL
import requests
import torch
from flask import Flask, jsonify, request, send_file
from PIL import ImageOps
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

app = Flask(__name__)

# Load the model
model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(model_id, torch_dtype=torch.float16, safety_checker=None)
pipe.to("cuda")
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

def download_image(url):
    image = PIL.Image.open(requests.get(url, stream=True).raw)
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    return image

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    url = data.get('url')
    prompt = data.get('prompt')

    if not url or not prompt:
        return jsonify({"error": "URL and prompt are required"}), 400

    # Download image
    try:
        image = download_image(url)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Generate images
    images = pipe(prompt, image=image, num_inference_steps=10, image_guidance_scale=1).images
    
    # Save the generated image
    output_path = "/tmp/output.png"  # Use a temporary path for Vercel
    images[0].save(output_path)

    return jsonify({"message": "Image generated successfully", "image_url": output_path})

@app.route('/output', methods=['GET'])
def get_image():
    return send_file("/tmp/output.png", mimetype='image/png')

@app.route('/')
def index():
    return "Welcome to the Image Generator API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
