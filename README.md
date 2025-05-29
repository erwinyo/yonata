

# Yet One Neat
Observability tool for tracking experiments.


## Installation

```bash
pip install yonata
```

## Getting Started

```bash
import yonata

audit = yonata()
audit.benchmark_from_image_folder(
    instance: <model instance>,
    folder_path: <folder_path>
)
```

## Model Instance
In using this library there must be at least **process()** function in the model instance. Below is a general template that can be used, you can make your own modifications.

```python
# Built-in imports
import os
from dataclasses import dataclass, field

# Third party imports

# Local imports


@dataclass(frozen=False, kw_only=False, match_args=False, slots=False)
class YourClassName:
    config: dict = field(default_factory=dict)

    _model: Model = field(init=False, repr=False)
    def __post_init__(self) -> None:
        pass

    def preprocess(self, data):
        return data

    def postprocess(self, data):
        return data

    def process(self, image, raw_result: bool = False):

        if raw_result:
            return embedding

        embedding = self.postprocess(embedding)
        return embedding

```