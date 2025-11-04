import os
import xmlschema

schema_path = os.path.join(
        os.path.dirname(__file__), 'xsd/dapt/dapt.xsd')
metadata_items_schema_path = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        'xsd/dapt/ttml2-metadata-items.xsd')
)

schema_paths = [schema_path, metadata_items_schema_path]
DAPTSchema = xmlschema.XMLSchema(
    source=schema_paths,
    build=False
)
DAPTSchema.build()
