# Built-in/Generic Imports
import os
import json
from pathlib import Path

# Third-party package
from openai import OpenAI
from deepdiff import DeepDiff

# Local package
from yonata.benchmark import multimodal_openai

import base64

def test_invoice_ocr_multimodal_openai():
    ROOT_PATH = "tests/test_benchmark/test_invoice_ocr_multimodal_openai"
    # Define the parameters for the benchmark
    model = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    model_name="gpt-4o-mini"    
    temperature = 0.0
    prompt = Path(f"{ROOT_PATH}/prompt.txt").read_text()
    system_prompt = "You are a helpful assistant that extracts information from invoices."
    schema = json.load(Path(f"{ROOT_PATH}/schema.json").open())

    top_p = 1.0     # no filtering (same as not using nucleus sampling).

    # Prepare the base64 image
    filename = "im3.jpg"
    with open(f"{ROOT_PATH}/{filename}", 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    expected_output = json.load(Path(f"{ROOT_PATH}/expected_output.json").open())[filename]

    # Call the benchmark function
    response = multimodal_openai(
        base64_image=base64_image,
        model=model,
        model_name=model_name,
        temperature=temperature,
        system_prompt=system_prompt,
        prompt=prompt,
        schema=schema,
        top_p=top_p,
        expected_output=expected_output
    )
    json_response = json.loads(response.output_text)

    diff = DeepDiff(
        json_response,
        expected_output,
        significant_digits=2
    )

    assert diff == {}, f"Response does not match expected output. Differences: {diff}"