import orjson
from fastapi.responses import JSONResponse as _JSONResponse
from typing import Any
from utils.json import orjson_default

class JSONResponse(_JSONResponse):
    """
    JSON response using the high-performance orjson library to serialize data to JSON using custom default serialization.
    """

    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_PASSTHROUGH_DATETIME, default=orjson_default
        )