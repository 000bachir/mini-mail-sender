def normalize_recipients(*value):
    if isinstance(value, str):
        return [value]
    else:
        return value or []
