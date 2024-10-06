import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Home endpoint called.")
    print("Home endpoint called.")  # Print statement
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/generate")
async def generate():
    logger.info("Generate button pressed.")
    print("Generate button pressed.")  # Print statement
    return {"message": "Image generation started."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
