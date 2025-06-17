import unittest
from src.preParseChecks.xmlStructureCheck import XmlStructureCheck
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN
from src.validationLogging.validationCodes import ValidationCode


class testXmlStructureCheck(unittest.TestCase):

    def test_well_formed(self):
        stimulus = b'''<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Something</p>
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='XML prolog',
                message='XML Prolog declares UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=GOOD,
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )
        ])

    def test_no_prolog(self):
        stimulus = b'''<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Something</p>
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=WARN,
                location='XML prolog',
                message='No XML Prolog present, assuming XML document '
                        'with UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=GOOD,
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )
        ])

    def test_no_encoding_decl(self):
        stimulus = b'''<?xml version="1.0"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Something</p>
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=WARN,
                location='XML prolog',
                message='XML Prolog found with no encoding declaration, '
                        'assuming UTF-8',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=GOOD,
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )
        ])

    def test_well_formed_lower_case_encoding_decl(self):
        stimulus = b'''<?xml version="1.0" encoding="utf-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Something</p>
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertTrue(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='XML prolog',
                message='XML Prolog declares UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=GOOD,
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )
        ])

    def test_wrong_encoding_decl(self):
        stimulus = b'''<?xml version="1.0" encoding="ISO-8859-1"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Something</p>
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='XML prolog',
                message='Non-UTF-8 encoding declaration: ISO-8859-1, '
                        'UTF-8 required',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=GOOD,
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )
        ])

    def test_entity_decl_present(self):
        stimulus = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tt [
<!ENTITY entity "entity declarations are not permitted">
]>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Something</p>
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=GOOD,
                location='XML prolog',
                message='XML Prolog declares UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=ERROR,
                location='XML Document Type',
                message='XML Entity declaration found - '
                        'these are not permitted',
                code=ValidationCode.xml_entity_decl
            )
        ])

    def test_badly_formed(self):
        stimulus = b'''<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:cellResolution="40 24"
    xml:lang="en">
    <body>
        <div xml:id="d1">
            <p>Missing end tag
        </div>
    </body>
</tt>
'''
        xmlStructureCheck = XmlStructureCheck()
        vr = ValidationLogger()

        valid, result = xmlStructureCheck.run(
            input=stimulus,
            validation_results=vr
        )

        self.assertEqual(stimulus, result)
        self.assertFalse(valid)
        self.assertListEqual(vr, [
            ValidationResult(
                status=ERROR,
                location='XML Document line 10 position 10',
                message='mismatched tag',
                code=ValidationCode.xml_document_validity),
            ValidationResult(
                status=GOOD,
                location='XML prolog',
                message='XML Prolog declares UTF-8 encoding',
                code=ValidationCode.xml_encoding_decl
            ),
            ValidationResult(
                status=GOOD,
                location='XML Document Type',
                message='No XML Entity declarations found',
                code=ValidationCode.xml_entity_decl
            )
        ])
