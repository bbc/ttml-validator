from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import xmlIdAttr
from .xmlCheck import XmlCheck

timing_attr_keys = set([
    'begin',
    'end',
    'dur'
])


def getTimingAttributes(
        el: Element
) -> set:
    attr_key_set = set(el.keys())
    return attr_key_set.intersection(timing_attr_keys)


def pushParentTimingAttributes(
        timing_attributes: set,
        context: dict
) -> None:
    parent_timing_stack = context.get('parent_timing', [])
    parent_timing_stack.append(timing_attributes)
    context['parent_timing'] = parent_timing_stack

    return


def getParentTimingAttributes(
        context: dict
) -> set:
    parent_timing_stack = context.get('parent_timing', [])
    if len(parent_timing_stack) == 0:
        return set()
    return parent_timing_stack[-1]


def popParentTimingAttributes(
        context: dict
) -> set:
    parent_timing_stack = context.get('parent_timing', [])
    return parent_timing_stack.pop()


class noTimingAttributeCheck(XmlCheck):
    """
    Checks there are no timing attributes on the input element
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True

        timing_attributes = list(sorted(getTimingAttributes(input)))
        if len(timing_attributes) > 0:
            valid = False
            validation_results.error(
                location='{} element xml:id {}'
                         .format(
                             input.tag,
                             input.get(xmlIdAttr, 'omitted')),
                message='Prohibited timing attributes {} present'
                        .format(timing_attributes),
                code=ValidationCode.ebuttd_timing_attribute_constraint
            )

        return valid


class noNestedTimedElementsCheck(XmlCheck):
    """
    Checks for nested elements that have timing attributes
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True

        timing_attributes = getTimingAttributes(input)
        parent_timing_attributes = \
            getParentTimingAttributes(context=context)

        if len(timing_attributes) > 0 \
                and len(parent_timing_attributes) > 0:
            valid = False
            # TODO: get the parent element details to improve the location
            # validation_results.error(
            #     location='{}@xml:id {}/{} element'.format(
            #         parent_el.tag,
            #         parent_el.get(xmlIdAttr, 'omitted'),
            #         input.tag),
            validation_results.error(
                location='{} element'.format(
                    input.tag),
                message='Nested elements with timing attributes prohibited',
                code=ValidationCode.ebuttd_nested_timing_constraint
            )

        return valid
