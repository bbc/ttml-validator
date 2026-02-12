# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from .jsonLoader import load_registry


descType_registry_entries = \
    load_registry(file='descType.json')

descType_user_defined_value_prefix = "x-"
