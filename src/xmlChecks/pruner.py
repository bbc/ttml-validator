# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from .xmlCheck import XmlCheck
from xml.etree.ElementTree import Element
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationCodes import ValidationCode


def get_namespace(tag: str) -> str:
    if (len(tag) == 0 or tag[0] != '{'):
        return ''

    if '}' not in tag:
        raise ValueError('No closing brace found')

    return tag.split('{', 1)[1].split('}', 1)[0]


def get_unqualified_name(tag: str) -> str:
    if '}' not in tag:
        return tag

    return tag.split('}', 1)[1]


class Pruner(XmlCheck):

    def __init__(
            self,
            no_prune_namespaces: set[str] = set(),
            no_prune_no_namespace_attributes: set[str] = set()
    ) -> None:
        self._no_prune_namespaces = no_prune_namespaces
        self._no_prune_no_namespace_attributes = \
            no_prune_no_namespace_attributes

    def run(
        self,
        input: Element,
        context: dict,
        validation_results: ValidationLogger
    ) -> bool:

        # pruned:
        # dict('namespace':
        #    'els': dict($tag: count),
        #    'attrs': dict($name: count))
        pruned = {}
        self.prune_unrecognised_vocabulary(el=input, pruned=pruned)
        # print(pruned)

        for ns, dicts in pruned.items():
            els_dict = dicts.get('els', {})
            attrs_dict = dicts.get('attrs', {})
            msg_str = \
                'Pruned {} elements {}and {} attributes {}in namespace "{}"' \
                .format(
                    len(els_dict),
                    '(' +
                    ', '.join(
                        ['"{}" {} time{}'.format(k, v, 's' if v > 1 else '')
                            for k, v in els_dict.items()]) +
                    ') ' if len(els_dict) > 0 else '',
                    len(attrs_dict),
                    '(' +
                    ', '.join(
                        ['"{}" {} time{}'.format(k, v, 's' if v > 1 else '')
                            for k, v in attrs_dict.items()]) +
                    ') ' if len(attrs_dict) > 0 else '',
                    ns)
            validation_results.info(
                location='Document',
                message=msg_str,
                code=ValidationCode.xml_prune
            )
        return True

    def prune_unrecognised_vocabulary(self, el: Element, pruned: dict):
        to_remove = []
        for child in el:
            child_ns = get_namespace(child.tag)
            if child_ns not in self._no_prune_namespaces:
                # logging.debug('pruning element {}'.format(child.tag))
                to_remove.append(child)
                self.log_pruned_el(
                    pruned=pruned,
                    ns=child_ns,
                    tag=get_unqualified_name(child.tag))
            else:
                self.prune_unrecognised_vocabulary(el=child, pruned=pruned)

        for e in to_remove:
            el.remove(e)

        for attr_key in el.keys():
            attr_ns = get_namespace(attr_key)

            attr_name = get_unqualified_name(attr_key)
            if (attr_ns and attr_ns not in self._no_prune_namespaces) \
               or \
               (not attr_ns and
                    attr_name not in self._no_prune_no_namespace_attributes):
                # logging.debug('pruning {}@{}'.format(el.tag, attr_key))
                self.log_pruned_attr(
                    pruned=pruned,
                    ns=attr_ns,
                    attr_name=attr_name)
                el.attrib.pop(attr_key)

        return el

    def log_pruned_el(self, pruned: dict, ns: str, tag: str):
        # print('pruning element {} {}'.format(ns, tag))
        ns_dict = pruned.get(ns, {})
        els_dict = ns_dict.get('els', {})
        tag_count = els_dict.get(tag, 0)
        tag_count += 1
        els_dict[tag] = tag_count
        ns_dict['els'] = els_dict
        pruned[ns] = ns_dict
        return

    def log_pruned_attr(self, pruned: dict, ns: str, attr_name: str):
        # print('pruning attr {} {}'.format(ns, attr_name))
        ns_dict = pruned.get(ns, {})
        attr_dict = ns_dict.get('attrs', {})
        attr_count = attr_dict.get(attr_name, 0)
        attr_count += 1
        attr_dict[attr_name] = attr_count
        ns_dict['attrs'] = attr_dict
        pruned[ns] = ns_dict
        return
