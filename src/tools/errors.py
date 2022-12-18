from abc import ABC
from typing import Optional


class ToolError(Exception):
    pass


class DocumentaryError(ToolError):
    def __init__(self, message_template: str = str(), document: Optional[dict] = None):
        self.message_template = message_template
        self.document = document

    @property
    def message(self) -> str:
        return (
            self.message_template.format(document=str(self.document))
            if self.document is not None and '{document}' in self.message_template
            else self.message_template
        )

    def __str__(self) -> str:
        return (
            str(self.document)
            if not self.message_template and self.document is not None
            else self.message
        )


class StatusCodeError(ToolError, ABC):
    status_code: int