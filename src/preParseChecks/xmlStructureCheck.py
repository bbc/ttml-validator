from .preParseCheck import PreParseCheck
from ..validationLogging.validationLogger import ValidationLogger
from ..validationLogging.validationCodes import ValidationCode
from xml.parsers.expat import ParserCreate, ExpatError, errors
import logging


class XmlStructureCheck(PreParseCheck):
    """
    Check for entity declarations and non-UTF-8 declared encodings.

    This is a PreParseCheck because when we parse the XML using ElementTree
    later it processes all the declarations and replaces the entity
    references and there's no way to stop that.

    Only expat seems to allow the entity declarations to be observed,
    so using it directly even though the documentation says that doing so
    is deprecated (although it doesn't offer an alternative!).
    """

    def run(
            self,
            input: bytes,
            validation_results: ValidationLogger) -> tuple[bool, bytes]:
        encodingDecl = None
        entityDeclarationsFound = False
        xmlDeclFound = False

        def entityDeclHandler(
                entityName: str,
                is_parameter_entity: bool,
                value: str | None,
                base: str | None,
                systemId: str,
                publicId: str | None,
                notationName: str | None) -> None:
            logging.debug('Found an entity declaration. Name: "{}"'
                          .format(entityName))
            nonlocal entityDeclarationsFound
            entityDeclarationsFound = True
            return

        def xmlDeclHandler(
                version: str,
                encoding: str | None,
                standalone: int) -> None:
            logging.debug(
                'XML Declaration version {} encoding {} standalone {}'
                .format(version, encoding, standalone))
            nonlocal encodingDecl, xmlDeclFound
            encodingDecl = encoding
            xmlDeclFound = True
            return

        valid = True

        parser = ParserCreate()
        parser.EntityDeclHandler = entityDeclHandler
        parser.XmlDeclHandler = xmlDeclHandler

        try:
            parser.Parse(input)
        except ExpatError as xe:
            valid = False
            validation_results.error(
                location='XML Document line {} position {}'
                         .format(xe.lineno, xe.offset),
                message=errors.messages[xe.code],
                code=ValidationCode.xml_document_validity
            )

        if encodingDecl is not None and encodingDecl.upper() != 'UTF-8':
            valid = False
            validation_results.error(
                location='XML prolog',
                message='Non-UTF-8 encoding declaration: {}, UTF-8 required'
                        .format(encodingDecl),
                code=ValidationCode.xml_encoding_decl
            )
        elif xmlDeclFound and encodingDecl is not None:
            validation_results.good(
                location='XML prolog',
                message='XML Prolog declares UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            )
        elif xmlDeclFound and encodingDecl is None:
            validation_results.warn(
                location='XML prolog',
                message='XML Prolog found with no encoding declaration, '
                        'assuming UTF-8',
                code=ValidationCode.xml_encoding_decl
            )
        else:
            validation_results.warn(
                location='XML prolog',
                message='No XML Prolog present, assuming XML document '
                        'with UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            )

        if entityDeclarationsFound:
            valid = False
            validation_results.error(
                location='XML Document Type',
                message='XML Entity declaration found - '
                        'these are not permitted',
                code=ValidationCode.xml_entity_decl
            )
        else:
            validation_results.good(
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )

        return (valid, input)
