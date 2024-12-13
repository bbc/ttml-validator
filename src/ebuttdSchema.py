import os
import xmlschema

schema_path = os.path.join(os.path.dirname(__file__), 'xsd/ebutt_d.xsd')
EBUTTDSchema = xmlschema.XMLSchema(schema_path)
