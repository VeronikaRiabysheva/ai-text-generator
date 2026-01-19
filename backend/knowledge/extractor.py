from typing import List
from parser.models import FunctionInfo, ClassInfo
from .schemas import KnowledgeEntity
import os


class KnowledgeExtractor:
    def extract(
        self,
        functions: List[FunctionInfo],
        classes: List[ClassInfo]
    ) -> List[KnowledgeEntity]:

        knowledge = []

        # Классы → знания
        for cls in classes:
            knowledge.append(
                KnowledgeEntity(
                    entity_type="class",
                    name=cls.name,
                    description=cls.docstring,
                    module=os.path.basename(cls.file),
                    relations=[m.name for m in cls.methods]
                )
            )

        # Функции → знания
        for func in functions:
            knowledge.append(
                KnowledgeEntity(
                    entity_type="function",
                    name=func.name,
                    description=func.docstring,
                    module=os.path.basename(func.file),
                    relations=[func.class_name] if func.class_name else []
                )
            )

        return knowledge
