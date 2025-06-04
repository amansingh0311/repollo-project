import orjson
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID


def timedelta_isoformat(td: timedelta) -> str:
    """
    ISO 8601 encoding for timedeltas.
    """
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return f'P{td.days}DT{h:d}H{m:d}M{s:d}.{td.microseconds:06d}S'


def orjson_default(obj):
    if callable(obj):
        return obj()
    elif isinstance(obj, datetime):
        return int(obj.timestamp())
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        return obj.total_seconds  # timedelta_isoformat(obj)
    elif isinstance(obj, time):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        if obj.as_tuple().exponent >= 0:
            return int(obj)
        else:
            return float(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError


def orjson_dumps(v, default=orjson_default, **kwargs):
    # returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(
        v,
        default=default,
        option=orjson.OPT_PASSTHROUGH_DATETIME | orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        **kwargs,
    ).decode('UTF-8')

def orjson_loads(v, **kwargs):
    return orjson.loads(v, **kwargs)
