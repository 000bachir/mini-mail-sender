def normalize_recipients(value) -> list:
    if isinstance(value, str):
        return [value]
    elif isinstance(value, list):
        return value
    return []
