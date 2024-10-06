import PIL
import requests
import torch
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

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
image = download_image(url)

prompt = "turn him into a picasso portrait, cubism style"
images = pipe(prompt, image=image, num_inference_steps=15, image_guidance_scale=1).images
images[0]
