import os
import logging
import PIL
import requests
import torch
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Set up static file serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the model
logger.info("Loading the model...")
print("Loading the model...")  # Print statement
model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(model_id, torch_dtype=torch.float16, safety_checker=None)
pipe.to("cuda")
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
logger.info("Model loaded successfully.")
print("Model loaded successfully.")  # Print statement

url = "https://media.licdn.com/dms/image/v2/D4D03AQFzQHQUzhq8CQ/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1701027419177?e=1733356800&v=beta&t=AWUZgv2LLUTlaCzM9QaiXvOf3GqEYFVYhhJIf4ESrKM"

def download_image(url):
    logger.info(f"Downloading image from URL: {url}")
    print(f"Downloading image from URL: {url}")  # Print statement
    try:
        image = PIL.Image.open(requests.get(url, stream=True).raw)
        image = PIL.ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        logger.info("Image downloaded and processed successfully.")
        print("Image downloaded and processed successfully.")  # Print statement
        return image
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        print(f"Error downloading image: {e}")  # Print statement
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Home endpoint called.")
    print("Home endpoint called.")  # Print statement
    return templates.TemplateResponse("index.html", {"request": request, "image_url": None})

@app.get("/generate")
async def generate():
    logger.info("Image generation process started.")
    print("Image generation process started.")  # Print statement
    image = download_image(url)
    
    if image is None:
        logger.error("Failed to download the image. Aborting generation.")
        print("Failed to download the image. Aborting generation.")  # Print statement
        return {"error": "Failed to download the image."}
    
    prompt = "turn him into a picasso portrait, cubism style"
    
    try:
        # Generate the image
        images = pipe(prompt, image=image, num_inference_steps=15, image_guidance_scale=1).images
        output_path = "static/output.png"  # Save to the static folder
        images[0].save(output_path)
        logger.info("Image generated successfully and saved.")
        print("Image generated successfully and saved.")  # Print statement
        return {"image_url": output_path}
    except Exception as e:
        logger.error(f"Error during image generation: {e}")
        print(f"Error during image generation: {e}")  # Print statement
        return {"error": "Image generation failed."}

@app.get("/show-image")
async def show_image():
    logger.info("Show image endpoint called.")
    print("Show image endpoint called.")  # Print statement
    return templates.TemplateResponse("index.html", {"request": Request, "image_url": "output.png"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
