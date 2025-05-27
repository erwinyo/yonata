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
