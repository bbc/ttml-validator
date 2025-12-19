import json
import os
from typing import List, Any


def load_registry(file: str) -> List[Any]:

    registry_path = os.path.join(
            os.path.dirname(__file__), file)

    registry_entries = []
    with open(registry_path, mode='rt') as registry_file:
        registry_data = json.load(registry_file)

        keys = [
            column["rowKey"]
            for column in registry_data["columns"]
            if column.get("isKey", False)]

        if len(keys) == 1:
            registry_entries = [
                value[keys[0]]
                for value in registry_data["values"]
            ]
        else:
            registry_entries = [
                (value[key] for key in keys)
                for value in registry_data["values"]
            ]

    return registry_entries
