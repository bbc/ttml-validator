# SPDX-FileCopyrightText: Copyright © 2026 BBC
#
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABCMeta, abstractmethod
from src.preParseChecks.preParseCheck import PreParseCheck
from src.xmlChecks.xmlCheck import XmlCheck
from src.validationLogging.validationLogger import ValidationLogger


class ConstraintSet(metaclass=ABCMeta):
    _preParseChecks: list[PreParseCheck] = []
    _xmlChecks: list[XmlCheck] = []

    def preParseChecks(self) -> list[PreParseCheck]:
        return self._preParseChecks

    def xmlChecks(self) -> list[XmlCheck]:
        return self._xmlChecks

    @staticmethod
    @abstractmethod
    def summarise(validation_results: ValidationLogger) -> tuple[int, int]:
        raise NotImplementedError
