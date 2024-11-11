import io
import os
import httpx
import uuid

import gradio as gr
from flux.util import configs
from PIL import Image, ExifTags
from typing import List

HELM_RELEASE_NAME = os.environ.get("HELM_RELEASE_NAME")
HELM_RELEASE_NAMESPACE = os.environ.get("HELM_RELEASE_NAMESPACE")
# if not (HELM_RELEASE_NAME and HELM_RELEASE_NAMESPACE):
#     raise Exception("This script is can currently only be run within the flux-image-gen Helm chart")

def save_image(model_name: str, prompt: str, seed: str, add_sampling_metadata: bool, image: Image.Image):
    filename = f"output/gradio/{uuid.uuid4()}.jpg"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    exif_data = Image.Exif()
    exif_data[ExifTags.Base.Software] = "AI generated;img2img;flux"
    exif_data[ExifTags.Base.Make] = "Black Forest Labs"
    exif_data[ExifTags.Base.Model] = model_name
    if add_sampling_metadata:
        exif_data[ExifTags.Base.ImageDescription] = prompt
    image.save(filename, format="jpeg", exif=exif_data, quality=95, subsampling=0)
    return filename

async def generate_image(model, width, height, num_steps, guidance, seed, prompt, add_sampling_metadata):

    url = f"http://{HELM_RELEASE_NAME}-{model}-api.{HELM_RELEASE_NAMESPACE}.svc:8000/generate"
    data = {
        'width': width,
        'height': height,
        'num_steps': num_steps,
        'guidance': guidance,
        'seed': seed,
        'prompt': prompt,
        'add_sampling_metadata': add_sampling_metadata
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        seed = response.headers.get("x-seed-header", "unknown")
        filename = save_image(model, prompt, seed, add_sampling_metadata, image)

        return image, seed, filename, None

def create_demo(
        models: List[str],
        example_prompt,
    ):

    with gr.Blocks() as demo:
        gr.Markdown("# Flux Image Generation Demo")

        with gr.Row():
            with gr.Column():
                model = gr.Dropdown(models, value=models[0], label="Model", interactive=len(models) > 1)
                prompt = gr.Textbox(label="Prompt", value=example_prompt)

                with gr.Accordion("Advanced Options", open=False):
                    width = gr.Slider(128, 8192, 1360, step=16, label="Width")
                    height = gr.Slider(128, 8192, 768, step=16, label="Height")
                    num_steps = gr.Slider(1, 50, 4 if model.value == "flux-schnell" else 50, step=1, label="Number of steps")
                    guidance = gr.Slider(1.0, 10.0, 3.5, step=0.1, label="Guidance", interactive=not model.value == "flux-schnell")
                    seed = gr.Textbox("-1", label="Seed (-1 for random)")
                    add_sampling_metadata = gr.Checkbox(label="Add sampling parameters to metadata?", value=True)

                generate_btn = gr.Button("Generate")

            with gr.Column():
                output_image = gr.Image(label="Generated Image")
                seed_output = gr.Textbox(label="Used Seed")
                warning_text = gr.Textbox(label="Warning", visible=False)
                download_btn = gr.File(label="Download full-resolution")

        generate_btn.click(
            fn=generate_image,
            inputs=[model, width, height, num_steps, guidance, seed, prompt, add_sampling_metadata],
            outputs=[output_image, seed_output, download_btn, warning_text],
        )

    return demo

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Flux")
    parser.add_argument("--models", type=str, default="flux-schnell", help=f"Comma separated list of models to make available from {list(configs.keys())}")
    parser.add_argument("--example-prompt", type=str, default="a photo of a forest with mist swirling around the tree trunks. The word \"FLUX\" is painted over it in big, red brush strokes with visible texture", help="The example prompt to show in the UI on first load")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="The host name for your Gradio server to listen on")
    # Should work once this fix is accepted https://github.com/gradio-app/gradio/pull/9822
    # parser.add_argument("--web-root-path", type=str, default=None, help="The root path for the app on your web server (useful for running behind a reverse proxy)")
    args = parser.parse_args()
    print("Running with config:", args)

    demo = create_demo(args.models.split(","), args.example_prompt)
    demo.launch(
        server_name=args.host,
        # root_path=args.web_root_path
    )
