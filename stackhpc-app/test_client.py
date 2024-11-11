from gradio_client import Client

client = Client("http://localhost:7860/")
web_page, seed, file_name, err = client.predict(
		model="flux-schnell",
		width=1360,
		height=768,
		num_steps=4,
		guidance=3.5,
		seed="-1",
		prompt="Yoda riding a skateboard",
		add_sampling_metadata=True,
		api_name="/generate_image"
)
print('Result saved to:', file_name)
