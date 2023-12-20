from typing import ClassVar, List
from xml.etree.ElementTree import Element, fromstring


class Codex:
    DEFAULT_NAMESPACE: ClassVar[
        str
    ] = b' xmlns="http://www.battlescribe.net/schema/catalogueSchema"'

    def __init__(self, root: Element) -> None:
        self.root = root

    def __getattr__(self, attr) -> callable:
        if hasattr(self.root, attr):
            root_attr = getattr(self.root, attr)
            if callable(root_attr):
                return root_attr

        raise AttributeError(f"{attr} does not exists in {self}")

    def unit_names(self) -> List[str]:
        
        return list(
            map(
                lambda unit: unit.get("name"),
                self.find("categoryEntries").findall("categoryEntry"),
            )
        )

    @classmethod
    def from_binary(cls, binary: bytes) -> "Codex":
        return cls(root=fromstring(binary.replace(cls.DEFAULT_NAMESPACE, b"")))
