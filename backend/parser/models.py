from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    docstring: Optional[str]
    file: str
    class_name: Optional[str] = None


@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo]
    docstring: Optional[str]
    file: str
