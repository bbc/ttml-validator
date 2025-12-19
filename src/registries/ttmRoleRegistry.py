from .jsonLoader import load_registry


role_registry_entries = \
    load_registry(file='role.json')

role_user_defined_value_prefix = "x-"
