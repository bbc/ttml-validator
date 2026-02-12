# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import xmlschema

schema_path = os.path.join(
    os.path.dirname(__file__), 'xsd/ebu-tt-d/ebutt_d.xsd')
EBUTTDSchema = xmlschema.XMLSchema(schema_path)
