from ..validationLogging.validationCodes import ValidationCode
from ..validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from ..xmlUtils import make_qname
from .daptUtils import isScriptEvent, isText, ns_daptm
from .ttmlUtils import ns_ttml
from .xmlCheck import XmlCheck
from ..registries.contentDescriptorRegistry import \
    content_descriptor_registry_entries, \
    content_descriptor_user_defined_value_prefix


def _tokenise_content_descriptor(descriptor: str) -> list[str]:
    return descriptor.split('.')


def _is_content_descriptor_subtype(subtype: str, parent: str) -> bool:
    tokenised_subtype = _tokenise_content_descriptor(subtype)
    tokenised_parent = _tokenise_content_descriptor(parent)
    return tokenised_subtype[0:len(tokenised_parent)] == tokenised_parent


tokenised_content_descriptor_registry_entries = [
    _tokenise_content_descriptor(cdv)
    for cdv in content_descriptor_registry_entries
]


class daptmRepresentsCheck(XmlCheck):
    """
    Checks values of dapt:scriptRepresents and daptm:represents attributes
    """

    def __init__(self) -> None:
        super().__init__()

    def _is_valid_content_descriptor(self,
                                     descriptor: str) -> bool:
        valid = True

        # Check if the content descriptor is valid
        descriptor_tokens = _tokenise_content_descriptor(
            descriptor=descriptor)

        # check everything up to and excluding the first token
        # beginning with the user defined value prefix
        non_user_defined_tokens = []
        user_defined_token_found = False
        for token in descriptor_tokens:
            if token.startswith(content_descriptor_user_defined_value_prefix):
                user_defined_token_found = True
                break
            else:
                non_user_defined_tokens.append(token)

        if len(non_user_defined_tokens) > 0 \
           and non_user_defined_tokens \
           not in tokenised_content_descriptor_registry_entries:
            valid = False

        if len(descriptor_tokens) == 0 or \
           (len(non_user_defined_tokens) == 0
           and not user_defined_token_found):
            valid = False

        return valid

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        tt_ns = \
            context.get('root_ns', ns_ttml)
        scriptRepresents_attr_tag = make_qname(ns_daptm, 'scriptRepresents')
        represents_attr_tag = make_qname(ns_daptm, 'represents')
        permitted_represents_el_tags = [
            make_qname(namespace=tt_ns, name=el_name)
            for el_name in ['tt', 'body', 'div', 'p', 'span']
            ]
        required_computed_represents_el_tags = [
            make_qname(namespace=tt_ns, name=el_name)
            for el_name in ['div', 'p', 'span']
        ]
        valid = True

        # Get tt/daptm:scriptRepresents value which MUST be present
        scriptRepresents_val = input.get(scriptRepresents_attr_tag)
        scriptRepresents_vals = []
        if scriptRepresents_val is None:
            valid = False
            validation_results.error(
                location='{} element'.format(input.tag),
                message='Required daptm:scriptRepresents attribute is missing',
                code=ValidationCode.dapt_metadata_scriptRepresents
            )
        else:
            # Split on white space, check each value is valid, store
            scriptRepresents_string_vals = scriptRepresents_val.split()
            for val in scriptRepresents_string_vals:
                if self._is_valid_content_descriptor(descriptor=val):
                    # store it
                    scriptRepresents_vals.append(val)
                else:
                    valid = False
                    validation_results.error(
                        location='{} element daptm:scriptRepresents attribute'
                                 .format(input.tag),
                        message='Value {} is not a valid content descriptor'
                                .format(val),
                        code=ValidationCode.dapt_metadata_scriptRepresents
                    )

        # Get elements with represents attribute
        # For each one:
        #   check it is present on an element where it's allowed
        #   check it is a valid value
        #   check it is a sub-type of a value in scriptRepresents

        els = input.findall(
            './/{}[@{}]'.format('*', represents_attr_tag)
        )

        for el in els:
            if el.tag not in permitted_represents_el_tags:
                valid = False
                validation_results.error(
                    location='{} element'.format(el.tag),
                    message='daptm:represents attribute not permitted '
                            'on this element',
                    code=ValidationCode.dapt_metadata_represents
                )

            represents_val = el.get(represents_attr_tag, '')
            if not self._is_valid_content_descriptor(represents_val):
                valid = False
                validation_results.error(
                    location='{} element daptm:represents attribute'
                             .format(el.tag),
                    message='Invalid content descriptor "{}"'
                            .format(represents_val),
                    code=ValidationCode.dapt_metadata_content_descriptor
                )

            is_subtype_of_scriptRepresents = False
            for parent in scriptRepresents_vals:
                is_subtype_of_scriptRepresents |= \
                    _is_content_descriptor_subtype(
                        subtype=represents_val,
                        parent=parent)
                if is_subtype_of_scriptRepresents:
                    break

            if not is_subtype_of_scriptRepresents:
                valid = False
                validation_results.error(
                    location='{} element daptm:represents attribute'
                             .format(el.tag),
                    message='Content descriptor "{}" is not a subtype '
                            'of scriptRepresents values {}'
                            .format(represents_val, scriptRepresents_vals),
                    code=ValidationCode.dapt_metadata_represents
                )

        # Iterate through the tree to derive the computed represents.
        # For each element that requires a valid computed represents attribute:
        # check the computed represents attribute is valid - this will
        # catch empty computed represents attributes on the relevant
        # elements
        valid &= self.recursively_compute_child_represents(
            input=input,
            parent_computed_represents='',
            represents_attr_tag=represents_attr_tag,
            permitted_represents_el_tags=permitted_represents_el_tags,
            required_computed_represents_el_tags=required_computed_represents_el_tags,
            validation_results=validation_results
        )

        return valid

    def recursively_compute_child_represents(
            self,
            input: Element,
            parent_computed_represents: str,
            represents_attr_tag: str,
            permitted_represents_el_tags: list[str],
            required_computed_represents_el_tags: list[str],
            validation_results: ValidationLogger,
            ) -> bool:
        valid = True

        this_computed_represents = input.get(represents_attr_tag, '') \
            if represents_attr_tag in input.keys() \
            else parent_computed_represents

        if (isScriptEvent(el=input) or isText(el=input)) \
           and not self._is_valid_content_descriptor(this_computed_represents):
            valid = False
            validation_results.error(
                location='{} element daptm:represents attribute'
                         .format(input.tag),
                message='Computed value "{}" is not valid'
                        .format(this_computed_represents),
                code=ValidationCode.dapt_metadata_represents
            )

        children = [el for el in input
                    if el.tag in permitted_represents_el_tags]
        for child in children:
            valid &= self.recursively_compute_child_represents(
                input=child,
                parent_computed_represents=this_computed_represents,
                represents_attr_tag=represents_attr_tag,
                permitted_represents_el_tags=permitted_represents_el_tags,
                required_computed_represents_el_tags=required_computed_represents_el_tags,
                validation_results=validation_results
            )

        return valid
