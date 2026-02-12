# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
from src.xmlChecks.pruner import Pruner
from src.validationLogging.validationLogger import ValidationLogger, ValidationResult, ValidationCode, INFO

import xml.etree.ElementTree as ElementTree


class testPruner(unittest.TestCase):

    maxDiff = None

    recognised_namespaces = set([
        'http://www.w3.org/XML/1998/namespace', # xml
        'http://www.w3.org/ns/ttml', # tt
        'http://www.w3.org/ns/ttml#parameter', # ttp
        'http://www.w3.org/ns/ttml#audio', # tta
        'http://www.w3.org/ns/ttml#metadata', # ttm
        'http://www.w3.org/ns/ttml/feature/',
        'http://www.w3.org/ns/ttml/profile/dapt#metadata', # daptm
        'http://www.w3.org/ns/ttml/profile/dapt/extension/',
        'urn:ebu:tt:metadata', # ebuttm
    ])

    # We will not prune attributes in no namespace if they are
    # defined on any element in TTML or DAPT, even if they are
    # not defined on the specific element on which they occur.
    known_no_ns_attributes = set([
        'agent',
        'animate',
        'begin',
        'calcMode',
        'clipBegin',
        'clipEnd',
        'condition',
        'dur',
        'encoding',
        'end',
        'family',
        'fill',
        'format',
        'keySplines',
        'keyTimes',
        'length',
        'name',
        'range',
        'region',
        'repeatCount',
        'src',
        'style',
        'timeContainer',
        'type',
        'weight',
    ])

    def test_pruner(self):
        pruner = Pruner(
            no_prune_namespaces=self.recognised_namespaces,
            no_prune_no_namespace_attributes=self.known_no_ns_attributes)

        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:tta="http://www.w3.org/ns/ttml#audio"
    xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata"
    xmlns:ebuttm="urn:ebu:tt:metadata"
    ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/dapt1.0/content"
    daptm:scriptRepresents="audio"
    daptm:scriptType="originalTranscript"
    xml:lang="en">
    <head>
        <metadata xmlns:otherns="urn:some:other:namespace">
            <ttm:agent xmlns:nttm="http://www.netflix.com/ns/ttml#metadata" 
                nttm:voice="en-US-Wavenet-B" foo="bar" otherns:test="x" type="person" xml:id="actor_A" id="huh">
                <ttm:name type="full">Matthias Schoenaerts</ttm:name>
            </ttm:agent>
            <ttm:agent type="character" xml:id="character_2">
                <ttm:name type="alias">BOOKER</ttm:name>
                <ttm:actor agent="actor_A"/>
            </ttm:agent>
            <otherns:x/>
            <otherns:y/>
        </metadata>
    </head>
    <body>
        <div xml:id="se1" begin="3s" end="10s" ttm:agent="character_2" daptm:represents="audio.dialogue" daptm:onScreen="ON">
            <ttm:desc daptm:descType="scene">high mountain valley</ttm:desc>
            <metadata></metadata>
            <p daptm:langSrc="en"><span>Look at this beautiful valley.</span></p>
        </div>
    </body>
</tt>
"""
        input_etree = ElementTree.fromstring(input_xml)
        vr = ValidationLogger()
        context = {}
        valid = pruner.run(
            input=input_etree,
            context=context,
            validation_results=vr)
        self.assertListEqual(vr, [
            ValidationResult(
                status=INFO,
                location='Document',
                message='Pruned 0 elements and 1 attributes '
                        '("voice" 1 time) in namespace '
                        '"http://www.netflix.com/ns/ttml#metadata"',
                code=ValidationCode.xml_prune
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='Pruned 0 elements and 2 attributes ("foo" 1 time, "id" 1 time) in namespace ""',
                code=ValidationCode.xml_prune
            ),
            ValidationResult(
                status=INFO,
                location='Document',
                message='Pruned 2 elements ("x" 1 time, "y" 1 time) and 1 attributes ("test" 1 time) in namespace '
                        '"urn:some:other:namespace"',
                code=ValidationCode.xml_prune
            )
        ])
        self.assertTrue(valid)
        # To get the output namespaces to look the way we want, register them explicitly
        ElementTree.register_namespace('', 'http://www.w3.org/ns/ttml')
        ElementTree.register_namespace('ttp', 'http://www.w3.org/ns/ttml#parameter')
        ElementTree.register_namespace('ttm', 'http://www.w3.org/ns/ttml#metadata')
        ElementTree.register_namespace('daptm', 'http://www.w3.org/ns/ttml/profile/dapt#metadata')
        ElementTree.register_namespace('ebuttm', 'urn:ebu:tt:metadata')

        output_str = ElementTree \
            .tostring(input_etree,
                      encoding='UTF-8',
                      xml_declaration=True) \
            .decode('utf-8')
        # ElementTree.tostring() actually makes bytes!

        # The format of output that ElementTree makes is a bit weird, but short of
        # reparsing it and processing it as XML again, this is probably the easiest thing
        # to do. It may be a bit brittle...
        expected_output_str = """<?xml version='1.0' encoding='UTF-8'?>
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:daptm="http://www.w3.org/ns/ttml/profile/dapt#metadata" xmlns:ttm="http://www.w3.org/ns/ttml#metadata" xmlns:ttp="http://www.w3.org/ns/ttml#parameter" ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/dapt1.0/content" daptm:scriptRepresents="audio" daptm:scriptType="originalTranscript" xml:lang="en">
    <head>
        <metadata>
            <ttm:agent type="person" xml:id="actor_A">
                <ttm:name type="full">Matthias Schoenaerts</ttm:name>
            </ttm:agent>
            <ttm:agent type="character" xml:id="character_2">
                <ttm:name type="alias">BOOKER</ttm:name>
                <ttm:actor agent="actor_A" />
            </ttm:agent>
            </metadata>
    </head>
    <body>
        <div xml:id="se1" begin="3s" end="10s" ttm:agent="character_2" daptm:represents="audio.dialogue" daptm:onScreen="ON">
            <ttm:desc daptm:descType="scene">high mountain valley</ttm:desc>
            <metadata />
            <p daptm:langSrc="en"><span>Look at this beautiful valley.</span></p>
        </div>
    </body>
</tt>"""
        self.assertEqual(output_str, expected_output_str)
