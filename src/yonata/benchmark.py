# Built-in package
import time

# Third-party package
from openai import OpenAI
from deepdiff import DeepDiff

# Local package
from .vlm import do_multimodal_with_openai
from .variables import count_elements
from .dantic import MultimodalOpenAIOutput

def multimodal_openai(
    base64_image: str,
    model: OpenAI,
    model_name: str,
    temperature: float,
    system_prompt: str,
    prompt: tuple,
    schema: dict,
    top_p: float,
    expected_output: dict
) -> dict:
    response = do_multimodal_with_openai(
        base64_image=base64_image,
        system_prompt=system_prompt,
        prompt=prompt,
        schema=schema,
        model=model,
        model_name=model_name,
        temperature=temperature,
        top_p=top_p
    )

    element_count = count_elements(response)
    diff = DeepDiff(
        expected_output,
        response,
        ignore_order=True,
        significant_digits=2
    )

    # Count the number of differences (e.g. {'type_changes': 1, 'values_changed': 3})
    res = {}
    for d in diff.keys():
        res[d] = len(diff[d].keys())
    diff_count = sum(res.values())

    diff_percentage = (diff_count / element_count) * 100

    return MultimodalOpenAIOutput(
        metadata={
            "model_name": model_name,
            "temperature": temperature,
            "top_p": top_p,
            "prompt": prompt
        },
        response=response,
        element_count=element_count,
        diff=diff,
        diff_count=diff_count,
        diff_percentage=diff_percentage
    )