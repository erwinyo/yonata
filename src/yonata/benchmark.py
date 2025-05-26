# Built-in package
import time
import json

# Third-party package
import cv2
from openai import OpenAI
from deepdiff import DeepDiff

# Local package
from .files import list_files_inside_a_folder
from .vlm import do_multimodal_with_openai
from .variables import count_elements
from .dantic import MultimodalOpenAIOutput
from .constant import IMAGE_EXTENSIONS

def benchmark_from_image_folder(
    instance: object,
    folder_path: str,
):
    list_of_files = list_files_inside_a_folder(folder_path, extensions=IMAGE_EXTENSIONS)
    # if len(list_of_files) != len(expected_outputs):
    #     raise ValueError(
    #         f"Number of files in folder ({len(list_of_files)}) does not match the number of expected outputs ({len(expected_outputs)})."
    #     )

    results = []
    for file_path in list_of_files: 
        start = time.time()
        image = cv2.imread(file_path)
        result = instance.process(image)
        end = time.time()

        time_taken = (end - start) * 1000  # Convert to milliseconds
        results.append({
            "file_path": file_path,
            "result": result,
            "time_taken": time_taken,
        })
    return results
    



    








# def multimodal_openai(
#     base64_image: str,
#     model: OpenAI,
#     model_name: str,
#     temperature: float,
#     system_prompt: str,
#     prompt: tuple,
#     schema: dict,
#     top_p: float,
#     expected_output: dict
# ) -> dict:
#     response = do_multimodal_with_openai(
#         base64_image=base64_image,
#         system_prompt=system_prompt,
#         prompt=prompt,
#         schema=schema,
#         model=model,
#         model_name=model_name,
#         temperature=temperature,
#         top_p=top_p
#     )
#     response = json.loads(response.output_text)
    
    
#     element_count = count_elements(response)
#     diff = DeepDiff(
#         expected_output,
#         response,
#         ignore_order=True,
#         significant_digits=2
#     )

#     # Count the number of differences (e.g. {'type_changes': 1, 'values_changed': 3})
#     res = {}
#     for d in diff.keys():
#         res[d] = len(diff[d].keys())
#     diff_count = sum(res.values())

#     diff_percentage = (diff_count / element_count) * 100

#     return MultimodalOpenAIOutput(
#         metadata={
#             "model_name": model_name,
#             "temperature": temperature,
#             "top_p": top_p,
#             "prompt": prompt
#         },
#         response=response,
#         element_count=element_count,
#         diff=diff,
#         diff_count=diff_count,
#         diff_percentage=diff_percentage
#     )