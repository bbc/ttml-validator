from .jsonLoader import load_registry


content_descriptor_registry_entries = \
    load_registry(file='content-descriptor.json')

content_descriptor_user_defined_value_prefix = "x-"
