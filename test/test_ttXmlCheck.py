import unittest
import src.xmlChecks.ttXmlCheck as ttXmlCheck
import xml.etree.ElementTree as ElementTree
from src.validationResult import ValidationResult, ERROR, GOOD, WARN, INFO


class testTtXmlCheck(unittest.TestCase):
    maxDiff = None

    def test_xmlIdCheck_no_duplicates(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body>
<div xml:id="d1"><p xml:id="p1"><span xml:id="s1">s1</span></p></div>
<div xml:id="d2"><p xml:id="p2"><span xml:id="s2">s2</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicateCheck = ttXmlCheck.duplicateXmlIdCheck()
        vr = []
        context = {}
        valid = duplicateCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertTrue(valid)
        expected_validation_result = ValidationResult(
            status=GOOD,
            location='',
            message='xml:id values are unique'
        )
        self.assertListEqual(vr, [expected_validation_result])

    def test_xmlIdCheck_duplicates(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    xmlns:ebutts="urn:ebu:tt:style"
    ttp:cellResolution="32 15" ttp:timeBase="media">
<body>
<div xml:id="d1"><p xml:id="p1"><span xml:id="s1">s1</span></p></div>
<div xml:id="d1"><p xml:id="p1"><span xml:id="s2">s2</span></p></div>
</body>
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        duplicateCheck = ttXmlCheck.duplicateXmlIdCheck()
        vr = []
        context = {}
        valid = duplicateCheck.run(
            input=input_elementtree,
            context=context,
            validation_results=vr
        )
        self.assertFalse(valid)
        expected_validation_results = [
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}div, '
                         '{http://www.w3.org/ns/ttml}div',
                message='Duplicate xml:id found with value d1'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttml}p, '
                         '{http://www.w3.org/ns/ttml}p',
                message='Duplicate xml:id found with value p1'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

    def test_ttTagAndNamespaceCheck_no_prefix(self):
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-GB" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:tt="http://www.w3.org/ns/ttml" ttp:timeBase="media">
</tt>
"""
        input_elementtree = ElementTree.fromstring(input_xml)
        ttTagAndNamespaceCheck = ttXmlCheck.ttTagAndNamespaceCheck()
        vr = []
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
                location='Root element',
                message='Document root has correct tag and namespace'
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
        vr = []
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
                location='Root element',
                message='Document root has correct tag and namespace'
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
        vr = []
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
                message='Element has unexpected namespace '
                        '"http://www.w3.org/ns/ttaf"'
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
        vr = []
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
                message='Element has unexpected namespace '
                        '"http://www.w3.org/ns/ttaf"'
            ),
            ValidationResult(
                status=ERROR,
                location='{http://www.w3.org/ns/ttaf}wott',
                message='Element has unexpected tag <wott>'
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
            timeBase_whitelist=['media'],
            timeBase_required=True)
        vr = []
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
                message='timeBase checked'
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
            timeBase_whitelist=['media'],
            timeBase_required=True)
        vr = []
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
                message='Required timeBase attribute absent'
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
            timeBase_whitelist=['media'],
            timeBase_required=True)
        vr = []
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
                message='Required timeBase attribute absent'
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
            timeBase_whitelist=['media'],
            timeBase_required=True)
        vr = []
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
                message="timeBase smpte not in the allowed set ['media']"
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
        vr = []
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
                message='activeArea checked'
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
        vr = []
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
                message='Required activeArea attribute absent'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

        activeAreaCheck_optional = ttXmlCheck.activeAreaCheck(
            activeArea_required=False)
        vr = []
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
                message='activeArea attribute absent'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml/profile/imsc1#parameter}'
                         'activeArea attribute',
                message='activeArea checked'
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
        vr = []
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
                        'match syntax requirements'
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
        vr = []
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
                        'at least one component >100%'
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
        vr = []
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
                message='cellResolution checked'
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
        vr = []
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
                message='cellResolution checked'
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
        vr = []
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
                message='Required cellResolution attribute absent'
            ),
            ValidationResult(
                status=INFO,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='using default cellResolution value 32 15'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)

        cellResolutionCheck_optional = ttXmlCheck.cellResolutionCheck(
            cellResolution_required=False)
        vr = []
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
                message='cellResolution attribute absent'
            ),
            ValidationResult(
                status=INFO,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='using default cellResolution value 32 15'
            ),
            ValidationResult(
                status=GOOD,
                location='{http://www.w3.org/ns/ttml}tt '
                         '{http://www.w3.org/ns/ttml#parameter}'
                         'cellResolution attribute',
                message='cellResolution checked'
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
        vr = []
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
                        'match syntax requirements'
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
        vr = []
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
                        'at least one component == 0'
            ),
        ]
        self.assertListEqual(vr, expected_validation_results)
