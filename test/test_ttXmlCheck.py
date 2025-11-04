import unittest
import src.xmlChecks.ttXmlCheck as ttXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationLogging.validationCodes import ValidationCode
from src.validationLogging.validationLogger import ValidationLogger
from src.validationLogging.validationResult import ValidationResult, \
    ERROR, GOOD, WARN, INFO


class testTtXmlCheck(unittest.TestCase):
    maxDiff = None

    def test_ttTagAndNamespaceCheck_no_prefix(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml" ttp:timeBase="media">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        ttTagAndNamespaceCheck = ttXmlCheck.ttTagAndNamespaceCheck()
        vr = ValidationLogger()
        context = {}
        valid = ttTagAndNamespaceCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt',
                message='Root element has expected namespace '
                        '"http://www.w3.org/ns/ttml"',
                code=ValidationCode.xml_tt_namespace
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt',
                message='Root element has expected tag <tt>',
                code=ValidationCode.xml_root_element
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_ttTagAndNamespaceCheck_with_prefix(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<fred:tt xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:fred="http://www.w3.org/ns/ttml" ttp:timeBase="media">
</fred:tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        ttTagAndNamespaceCheck = ttXmlCheck.ttTagAndNamespaceCheck()
        vr = ValidationLogger()
        context = {}
        valid = ttTagAndNamespaceCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt',
                message='Root element has expected namespace '
                        '"http://www.w3.org/ns/ttml"',
                code=ValidationCode.xml_tt_namespace
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt',
                message='Root element has expected tag <tt>',
                code=ValidationCode.xml_root_element
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_ttTagAndNamespaceCheck_wrong_ns_with_prefix(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<wrong:tt xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:wrong="http://www.w3.org/ns/ttaf" ttp:timeBase="media">
</wrong:tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        ttTagAndNamespaceCheck = ttXmlCheck.ttTagAndNamespaceCheck()
        vr = ValidationLogger()
        context = {}
        valid = ttTagAndNamespaceCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttaf}tt',
                message='Root element has unexpected namespace '
                        '"http://www.w3.org/ns/ttaf"',
                code=ValidationCode.xml_tt_namespace
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}tt',
                message='Root element has expected tag <tt>',
                code=ValidationCode.xml_root_element
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_ttTagAndNamespaceCheck_wrong_tag_no_prefix(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<wott xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttaf" ttp:timeBase="media">
</wott>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        ttTagAndNamespaceCheck = ttXmlCheck.ttTagAndNamespaceCheck()
        vr = ValidationLogger()
        context = {}
        valid = ttTagAndNamespaceCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttaf}wott',
                message='Root element has unexpected namespace '
                        '"http://www.w3.org/ns/ttaf"',
                code=ValidationCode.xml_tt_namespace
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttaf}wott',
                message='Root element has unexpected tag <wott>',
                code=ValidationCode.xml_root_element
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timeBaseCheck_timebase_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml" ttp:timeBase="media">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timeBaseCheck = ttXmlCheck.timeBaseCheck(
            timeBase_acceptlist=['media'],
            timeBase_required=True)
        vr = ValidationLogger()
        context = {}
        valid = timeBaseCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'timeBase attribute',
                message='timeBase checked',
                code=ValidationCode.ebuttd_parameter_timeBase
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timeBaseCheck_timebase_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timeBaseCheck = ttXmlCheck.timeBaseCheck(
            timeBase_acceptlist=['media'],
            timeBase_required=True)
        vr = ValidationLogger()
        context = {}
        valid = timeBaseCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'timeBase attribute',
                message='Required timeBase attribute absent',
                code=ValidationCode.ebuttd_parameter_timeBase
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timeBaseCheck_timebase_missing_wrong_ns(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttaf" ttp:timeBase="media">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timeBaseCheck = ttXmlCheck.timeBaseCheck(
            timeBase_acceptlist=['media'],
            timeBase_required=True)
        vr = ValidationLogger()
        context = {}
        context['root_ns'] = 'http://www.w3.org/ns/ttaf'
        valid = timeBaseCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttaf}tt '
                         '{http://www.w3.org/ns/ttaf#parameter}'
                         'timeBase attribute',
                message='Required timeBase attribute absent',
                code=ValidationCode.ebuttd_parameter_timeBase
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_timeBaseCheck_timebase_illegal_value(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB" xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml" ttp:timeBase="smpte">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        timeBaseCheck = ttXmlCheck.timeBaseCheck(
            timeBase_acceptlist=['media'],
            timeBase_required=True)
        vr = ValidationLogger()
        context = {}
        valid = timeBaseCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'timeBase attribute',
                message="timeBase smpte not in the allowed set ['media']",
                code=ValidationCode.ebuttd_parameter_timeBase
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_activeArea_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ittp="http://www.w3.org/ns/ttml/profile/imsc1#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ittp:activeArea="10.0% 10.0% 80.5% 88.5%">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        activeAreaCheck = ttXmlCheck.activeAreaCheck(
            activeArea_required=True)
        vr = ValidationLogger()
        context = {}
        valid = activeAreaCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml/profile/imsc1#parameter}'
                         'activeArea attribute',
                message='activeArea checked',
                code=ValidationCode.imsc_parameter_activeArea
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_activeArea_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        activeAreaCheck_required = ttXmlCheck.activeAreaCheck(
            activeArea_required=True)
        vr = ValidationLogger()
        context = {}
        valid = activeAreaCheck_required.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml/profile/imsc1#parameter}'
                         'activeArea attribute',
                message='Required activeArea attribute absent',
                code=ValidationCode.imsc_parameter_activeArea
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

        activeAreaCheck_optional = ttXmlCheck.activeAreaCheck(
            activeArea_required=False)
        vr = ValidationLogger()
        context = {}
        valid = activeAreaCheck_optional.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml/profile/imsc1#parameter}'
                         'activeArea attribute',
                message='activeArea attribute absent',
                code=ValidationCode.imsc_parameter_activeArea
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_activeArea_bad_syntax(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ittp="http://www.w3.org/ns/ttml/profile/imsc1#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ittp:activeArea="10% 10% 80% 80% abc">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        activeAreaCheck = ttXmlCheck.activeAreaCheck()
        vr = ValidationLogger()
        context = {}
        valid = activeAreaCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml/profile/imsc1#parameter}'
                         'activeArea attribute',
                message='activeArea 10% 10% 80% 80% abc does not '
                        'match syntax requirements',
                code=ValidationCode.imsc_parameter_activeArea
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_activeArea_bad_semantic(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ittp="http://www.w3.org/ns/ttml/profile/imsc1#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ittp:activeArea="10% 10% 110% 80%">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        activeAreaCheck = ttXmlCheck.activeAreaCheck()
        vr = ValidationLogger()
        context = {}
        valid = activeAreaCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml/profile/imsc1#parameter}'
                         'activeArea attribute',
                message='activeArea 10% 10% 110% 80% has '
                        'at least one component >100%',
                code=ValidationCode.imsc_parameter_activeArea
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_cellResolution_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ttp:cellResolution="40 24">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck(
            cellResolution_required=True)
        vr = ValidationLogger()
        context = {}
        valid = cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='cellResolution checked',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_cellResolution_ok_wrong_ns(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttaf#parameter"
    xmlns="http://www.w3.org/ns/ttaf"
    ttp:cellResolution="40 24">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck(
            cellResolution_required=True)
        vr = ValidationLogger()
        context = {
            'root_ns': 'http://www.w3.org/ns/ttaf'
        }
        valid = cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttaf}tt '
                         '{http://www.w3.org/ns/ttaf#parameter}'
                         'cellResolution attribute',
                message='cellResolution checked',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_cellResolution_missing(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        cellResolutionCheck_required = ttXmlCheck.cellResolutionCheck(
            cellResolution_required=True)
        vr = ValidationLogger()
        context = {}
        valid = cellResolutionCheck_required.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='Required cellResolution attribute absent',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
            ValidationResult(
                status=INFO,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='using default cellResolution value 32 15',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

        cellResolutionCheck_optional = ttXmlCheck.cellResolutionCheck(
            cellResolution_required=False)
        vr = ValidationLogger()
        context = {}
        valid = cellResolutionCheck_optional.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=WARN,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='cellResolution attribute absent',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
            ValidationResult(
                status=INFO,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='using default cellResolution value 32 15',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='cellResolution checked',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_cellResolution_bad_syntax(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ttp:cellResolution="40c 24c">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
        context = {}
        valid = cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='cellResolution 40c 24c does not '
                        'match syntax requirements',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_cellResolution_bad_semantic(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ttp:cellResolution="0 24">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        cellResolutionCheck = ttXmlCheck.cellResolutionCheck()
        vr = ValidationLogger()
        context = {}
        valid = cellResolutionCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='cellResolution 0 24 has '
                        'at least one component == 0',
                code=ValidationCode.ttml_parameter_cellResolution
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_contentProfiles_ok(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ttp:contentProfiles="urn:cp:1 urn:cp:2">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        contentProfilesCheck = ttXmlCheck.contentProfilesCheck(
            contentProfiles_atleastonelist=[
                "urn:cp:1",
            ],
            contentProfiles_denylist=[
                "urn:cp:3",
            ],
            contentProfiles_required=True)
        vr = ValidationLogger()
        context = {}
        valid = contentProfilesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'contentProfiles attribute',
                message='contentProfiles checked',
                code=ValidationCode.ttml_parameter_contentProfiles
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_contentProfiles_missing_at_least_one(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ttp:contentProfiles="urn:cp:1 urn:cp:2">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        contentProfilesCheck = ttXmlCheck.contentProfilesCheck(
            contentProfiles_atleastonelist=[
                "urn:cp:3",
            ],
            contentProfiles_denylist=[
                "urn:cp:4",
            ],
            contentProfiles_required=False)
        vr = ValidationLogger()
        context = {}
        valid = contentProfilesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'contentProfiles attribute',
                message="At least one of the contentProfiles ['urn:cp:3'] "
                        "must be present, all are missing from the "
                        "contentProfile attribute urn:cp:1 urn:cp:2",
                code=ValidationCode.ttml_parameter_contentProfiles
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_contentProfiles_includes_prohibited(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml"
    ttp:contentProfiles="urn:cp:4 urn:cp:2">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        contentProfilesCheck = ttXmlCheck.contentProfilesCheck(
            contentProfiles_atleastonelist=[
                "urn:cp:2",
            ],
            contentProfiles_denylist=[
                "urn:cp:4",
            ],
            contentProfiles_required=False)
        vr = ValidationLogger()
        context = {}
        valid = contentProfilesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'contentProfiles attribute',
                message="contentProfile urn:cp:4 present but "
                        "in the prohibited set "
                        "['urn:cp:4']",
                code=ValidationCode.ttml_parameter_contentProfiles
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_contentProfiles_required_absent(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        contentProfilesCheck = ttXmlCheck.contentProfilesCheck(
            contentProfiles_atleastonelist=[],
            contentProfiles_denylist=[],
            contentProfiles_required=True)
        vr = ValidationLogger()
        context = {}
        valid = contentProfilesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'contentProfiles attribute',
                message="Required contentProfiles attribute "
                        "absent",
                code=ValidationCode.ttml_parameter_contentProfiles
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_contentProfiles_optional_absent(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns="http://www.w3.org/ns/ttml">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        contentProfilesCheck = ttXmlCheck.contentProfilesCheck(
            contentProfiles_atleastonelist=[],
            contentProfiles_denylist=[],
            contentProfiles_required=False)
        vr = ValidationLogger()
        context = {}
        valid = contentProfilesCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_results = [
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'contentProfiles attribute',
                message="contentProfiles checked",
                code=ValidationCode.ttml_parameter_contentProfiles
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
