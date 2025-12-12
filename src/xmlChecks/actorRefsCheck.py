from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element
from src.xmlUtils import xmlIdAttr, make_qname
from .xmlCheck import XmlCheck
from .ttmlUtils import ns_ttml


class actorRefsCheck(XmlCheck):
    """
    Checks that an actor element's ttm:agent does not reference
    an ancestor agent of the element.
    """

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        valid = True

        # Qualify the attribute and element names
        tt_ns = \
            context.get('root_ns', ns_ttml)
        metadata_ns = tt_ns + '#metadata'
        ttm_agent_el_tag = make_qname(metadata_ns, 'agent')
        ttm_actor_el_tag = make_qname(metadata_ns, 'actor')

        # Find all descendant ttm:agent elements
        agents = input.findall('.//{}'.format(ttm_agent_el_tag))

        # For each ttm:agent element, find its descendant ttm:actor elements
        # whose agent attribute is that parent ttm:agent's xml:id
        for agent in agents:
            agent_id = agent.get(xmlIdAttr)
            if agent_id is not None:
                xpath_str = './/{}[@{}=\'{}\']'.format(
                    ttm_actor_el_tag,
                    'agent',
                    agent_id
                )
                actors = agent.findall(xpath_str)
                for actor in actors:
                    validation_results.error(
                        location='ttm:agent element with xml:id={}'.format(
                            agent_id),
                        message='ttm:actor element found with agent pointing '
                                'to ancestor ttm:agent element',
                        code=ValidationCode.ttml_metadata_actor_reference
                    )
                    valid = False

        if valid:
            validation_results.good(
                location='{} element'.format(input.tag),
                message='No ttm:actor elements found referencing'
                        ' ancestor ttm:agent',
                code=ValidationCode.ttml_metadata_actor_reference
            )

        return valid
