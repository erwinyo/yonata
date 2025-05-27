# Built-in imports


# Third-party imports
from pydantic import BaseModel
from typing import List

# Local imports


class Baseline(BaseModel):
    metadata: dict


class MultimodalOpenAIOutput(Baseline):
    response: dict
    element_count: int
    diff: dict
    diff_count: int
    diff_percentage: float
