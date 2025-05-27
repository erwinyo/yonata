def _count_elements(obj):
    count = 0
    if isinstance(obj, dict):
        for value in obj.values():
            count += 1  # Count the current key-value pair
            count += _count_elements(value)
    elif isinstance(obj, list):
        for item in obj:
            count += 1  # Count the list item itself
            count += _count_elements(item)
    return count
