"""Exceptions specific to sqlean"""

from typing import Optional


class ConfigError(RuntimeError):
    """Run-time error with sqlean.configuration.Config"""

    def __init__(self, message: Optional[str] = None):
        message = message or "Config was used incorrectly"
        super().__init__(message)


class NodeListError(RuntimeError):
    """Run-time error with sqlean.node.NodeList"""

    def __init__(self, message: Optional[str] = None):
        message = message or "NodeList was used incorrectly"
        super().__init__(message)
