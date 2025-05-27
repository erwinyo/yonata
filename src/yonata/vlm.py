# Built-in imports
import json

# Third-party imports

# Local imports


def _do_multimodal_with_openai(
    base64_image, system_prompt, prompt, schema, model, model_name, temperature, top_p
) -> dict:
    response = model.responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "multimodal_output",
                "schema": schema,
                "strict": True,
            }
        },
        temperature=temperature,
        top_p=top_p,
    )

    return response
