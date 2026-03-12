import replicate

def generate_event_image(prompt: str):

    output = replicate.run(
        "stability-ai/sdxl",
        input={"prompt": prompt}
    )

    return {
        "prompt": prompt,
        "image_url": output[0]
    }