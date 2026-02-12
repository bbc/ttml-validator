# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from src.validationLogging.validationLogger import ValidationLogger
from xml.etree.ElementTree import Element


class XmlCheck:

    def run(
            self,
            input: Element,
            context: dict,
            validation_results: ValidationLogger) -> bool:
        """Runs the check.

        Must be implemented in a derived class.

        Args:
            input: The parsed XML element to check
            context: A context dictionary used across validation
            validation_results: Object in which to store any validation results

        Returns:
            True if the input element passes the check, False otherwise 
        """
        raise NotImplementedError()
