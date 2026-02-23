# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/bbc/ttml-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                          |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------- | -------: | -------: | ------: | --------: |
| src/\_\_init\_\_.py                           |        0 |        0 |    100% |           |
| src/constraintSets/\_\_init\_\_.py            |        0 |        0 |    100% |           |
| src/constraintSets/bbcConstraints.py          |       64 |       33 |     48% |91-92, 101-253 |
| src/constraintSets/constraintSet.py           |       13 |        1 |     92% |        22 |
| src/constraintSets/daptConstraints.py         |       53 |        2 |     96% |  154, 218 |
| src/preParseChecks/\_\_init\_\_.py            |        0 |        0 |    100% |           |
| src/preParseChecks/preParseCheck.py           |       66 |        4 |     94% |96-102, 126-127 |
| src/preParseChecks/xmlStructureCheck.py       |       53 |        0 |    100% |           |
| src/registries/\_\_init\_\_.py                |        0 |        0 |    100% |           |
| src/registries/contentDescriptorRegistry.py   |        3 |        0 |    100% |           |
| src/registries/daptmDescTypeRegistry.py       |        3 |        0 |    100% |           |
| src/registries/jsonLoader.py                  |       13 |        1 |     92% |        30 |
| src/registries/ttmRoleRegistry.py             |        3 |        0 |    100% |           |
| src/schemas/\_\_init\_\_.py                   |        0 |        0 |    100% |           |
| src/schemas/daptSchema.py                     |        7 |        0 |    100% |           |
| src/schemas/ebuttdSchema.py                   |        4 |        0 |    100% |           |
| src/styleAttribs.py                           |      166 |        4 |     98% |44, 181, 256, 570 |
| src/timeExpression.py                         |       81 |        0 |    100% |           |
| src/ttmlValidator.py                          |      117 |       42 |     64% |22-27, 44-54, 70, 81-82, 103-105, 113-120, 147-149, 168, 170, 177, 185-265, 270 |
| src/validationLogging/\_\_init\_\_.py         |        0 |        0 |    100% |           |
| src/validationLogging/validationCodes.py      |        2 |        0 |    100% |           |
| src/validationLogging/validationLogger.py     |       50 |        0 |    100% |           |
| src/validationLogging/validationResult.py     |       23 |        0 |    100% |           |
| src/validationLogging/validationSummariser.py |       21 |        0 |    100% |           |
| src/xmlChecks/\_\_init\_\_.py                 |        0 |        0 |    100% |           |
| src/xmlChecks/actorRefsCheck.py               |       25 |        0 |    100% |           |
| src/xmlChecks/bbcTimingXmlCheck.py            |      204 |       10 |     95% |105, 242, 280, 284-287, 392, 572-574 |
| src/xmlChecks/bodyXmlCheck.py                 |       31 |        0 |    100% |           |
| src/xmlChecks/copyrightCheck.py               |       24 |        0 |    100% |           |
| src/xmlChecks/daptLangCheck.py                |       44 |        0 |    100% |           |
| src/xmlChecks/daptTimingXmlCheck.py           |      186 |       10 |     95% |228, 432-433, 443-444, 452-453, 547-549 |
| src/xmlChecks/daptUtils.py                    |       16 |        0 |    100% |           |
| src/xmlChecks/daptmDescTypeCheck.py           |       29 |        0 |    100% |           |
| src/xmlChecks/daptmRepresentsCheck.py         |       80 |        3 |     96% |68, 130-131 |
| src/xmlChecks/divXmlCheck.py                  |       33 |        0 |    100% |           |
| src/xmlChecks/headXmlCheck.py                 |       28 |        0 |    100% |           |
| src/xmlChecks/inlineStyleAttributeCheck.py    |       23 |        0 |    100% |           |
| src/xmlChecks/layoutCheck.py                  |       52 |        0 |    100% |           |
| src/xmlChecks/pXmlCheck.py                    |       27 |        0 |    100% |           |
| src/xmlChecks/pruner.py                       |       62 |        1 |     98% |        16 |
| src/xmlChecks/regionRefsCheck.py              |      149 |        9 |     94% |186, 320-328, 348-357, 389-401 |
| src/xmlChecks/spanXmlCheck.py                 |       35 |        0 |    100% |           |
| src/xmlChecks/styleRefsCheck.py               |      177 |        5 |     97% |281, 317, 362, 499-505 |
| src/xmlChecks/stylingCheck.py                 |       54 |        0 |    100% |           |
| src/xmlChecks/textCheck.py                    |       27 |        0 |    100% |           |
| src/xmlChecks/timingAttributeCheck.py         |       39 |        1 |     97% |        41 |
| src/xmlChecks/ttXmlCheck.py                   |      128 |        0 |    100% |           |
| src/xmlChecks/ttmlRoleCheck.py                |       33 |        0 |    100% |           |
| src/xmlChecks/ttmlUtils.py                    |        5 |        0 |    100% |           |
| src/xmlChecks/xmlCheck.py                     |        5 |        0 |    100% |           |
| src/xmlChecks/xmlIdCheck.py                   |       86 |        4 |     95% |97-98, 147, 172 |
| src/xmlChecks/xsdValidator.py                 |       19 |        0 |    100% |           |
| src/xmlUtils.py                               |       17 |        0 |    100% |           |
| test/\_\_init\_\_.py                          |        0 |        0 |    100% |           |
| test/test\_actorRefsCheck.py                  |       30 |        0 |    100% |           |
| test/test\_bbcTimingCheck.py                  |      185 |        0 |    100% |           |
| test/test\_bodyXmlCheck.py                    |      125 |        0 |    100% |           |
| test/test\_dapt.py                            |       56 |        2 |     96% |  100, 117 |
| test/test\_daptLangCheck.py                   |       87 |        0 |    100% |           |
| test/test\_daptTimingCheck.py                 |      196 |        0 |    100% |           |
| test/test\_daptmDescTypeCheck.py              |       30 |        0 |    100% |           |
| test/test\_daptmRepresents.py                 |       92 |        0 |    100% |           |
| test/test\_headXmlCheck.py                    |      205 |        0 |    100% |           |
| test/test\_inlineStyleAttributeCheck.py       |       28 |        0 |    100% |           |
| test/test\_preParseCheck.py                   |      101 |        7 |     93% |   165-178 |
| test/test\_pruner.py                          |       25 |        0 |    100% |           |
| test/test\_regionRefsCheck.py                 |      135 |        0 |    100% |           |
| test/test\_styleAttribs.py                    |      110 |        0 |    100% |           |
| test/test\_styleRefsCheck.py                  |      294 |        0 |    100% |           |
| test/test\_time\_expressions.py               |       49 |        0 |    100% |           |
| test/test\_ttXmlCheck.py                      |      243 |        0 |    100% |           |
| test/test\_ttmRoleCheck.py                    |       34 |        0 |    100% |           |
| test/test\_validation.py                      |       50 |        0 |    100% |           |
| test/test\_xmlCheck.py                        |       59 |        0 |    100% |           |
| test/test\_xmlIdCheck.py                      |       80 |        0 |    100% |           |
| test/test\_xmlStructureCheck.py               |       81 |        0 |    100% |           |
| test/test\_xmlUtils.py                        |       23 |        0 |    100% |           |
| **TOTAL**                                     | **4698** |  **139** | **97%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/bbc/ttml-validator/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/bbc/ttml-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/bbc/ttml-validator/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/bbc/ttml-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fbbc%2Fttml-validator%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/bbc/ttml-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.