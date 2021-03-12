"""Exceptions specific to sqlean"""

from typing import Optional


class ConfigInitializedMoreThanOnceError(RuntimeError):
    """Run-time error if the Config singleton is initialised a second time"""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            self.message = "The Config class can only be initialised once."
        super().__init__(self.message)
