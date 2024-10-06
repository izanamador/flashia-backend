import PIL
import requests
import torch
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

app = FastAPI()

# Load the model
model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(model_id, torch_dtype=torch.float16, safety_checker=None)
pipe.to("cuda")
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

url = "https://media.licdn.com/dms/image/v2/D4D03AQFzQHQUzhq8CQ/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1701027419177?e=1733356800&v=beta&t=AWUZgv2LLUTlaCzM9QaiXvOf3GqEYFVYhhJIf4ESrKM"

def download_image(url):
    image = PIL.Image.open(requests.get(url, stream=True).raw)
    image = PIL.ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    return image

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Image Generation</title>
        </head>
        <body>
            <h1>Generate an Image</h1>
            <button onclick="generateImage()">Generate</button>
            <img id="result" style="margin-top: 20px;"/>
            <script>
                async function generateImage() {
                    const response = await fetch('/generate');
                    const data = await response.json();
                    const img = document.getElementById('result');
                    img.src = data.image_url;
                }
            </script>
        </body>
    </html>
    """

@app.get("/generate")
async def generate():
    image = download_image(url)
    prompt = "turn him into a picasso portrait, cubism style"
    
    # Generate the image
    images = pipe(prompt, image=image, num_inference_steps=15, image_guidance_scale=1).images
    
    # Save the generated image
    output_path = "output.png"
    images[0].save(output_path)
    
    return {"image_url": output_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
