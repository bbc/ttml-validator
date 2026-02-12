# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from xml.etree.ElementTree import Element
from .ttmlUtils import ns_ttml
from src.xmlUtils import make_qname


ns_daptm = "http://www.w3.org/ns/ttml/profile/dapt#metadata"
ns_dapt_extension = 'http://www.w3.org/ns/ttml/profile/dapt/extension/'


def isScriptEvent(el: Element, tt_ns: str = ns_ttml) -> bool:
    rv = False
    div_tag = make_qname(namespace=tt_ns, name='div')

    if el.tag == div_tag:
        child_divs = [c for c in el if c.tag == div_tag]
        if len(child_divs) == 0:
            rv = True

    return rv


def isText(el: Element, tt_ns: str = ns_ttml) -> bool:
    ok_tags = [
        make_qname(namespace=tt_ns, name='p'),
        make_qname(namespace=tt_ns, name='span'),
    ]

    return el.tag in ok_tags
