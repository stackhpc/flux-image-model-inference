import os
import torch

from fastapi import FastAPI, Response
from pydantic import BaseModel

from demo_gr import FluxGenerator

app = FastAPI()
device = "cuda" if torch.cuda.is_available() else "cpu"
model = os.environ.get("FLUX_MODEL_NAME", "flux-schnell")
generator = FluxGenerator(model, device, offload=False)

class ImageGenInput(BaseModel):
    width: int
    height: int
    num_steps: int
    guidance: float
    seed: int
    prompt: str
    add_sampling_metadata: bool

@app.get("/model")
async def get_model():
    return {"model": model}


@app.post("/generate")
async def generate_image(input: ImageGenInput):
    # return input
    image, _, _, msg = generator.generate_image(input.width, input.height, input.num_steps, input.guidance, input.seed, input.prompt, input.add_sampling_metadata)
    if image:
        return Response(content=image.tobytes(), media_type="image/png")
    else:
        return {"error", msg}
