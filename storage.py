
_storage = dict()

def get_storage():
    """Returns the storage dictionary."""
    return _storage

def set_storage(key, value):
    """Sets a value in the storage dictionary."""
    _storage[key] = value

def get_value(key):
    """Gets a value from the storage dictionary."""
    return _storage.get(key, None)

def delete_value(key):
    """Deletes a value from the storage dictionary."""
    if key in _storage:
        del _storage[key]

def clear_storage():
    """Clears the storage dictionary."""
    _storage.clear()

def storage_keys():
    """Returns a list of keys in the storage dictionary."""
    return list(_storage.keys())

def storage_values():
    """Returns a list of values in the storage dictionary."""
    return list(_storage.values())

def storage_items():
    """Returns a list of key-value pairs in the storage dictionary."""
    return list(_storage.items())