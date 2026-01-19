import ast
from typing import List
from .models import FunctionInfo, ClassInfo


class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self._current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        args = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)

        func_info = FunctionInfo(
            name=node.name,
            args=args,
            docstring=docstring,
            file=self.file_path,
            class_name=self._current_class
        )

        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        docstring = ast.get_docstring(node)
        previous_class = self._current_class
        self._current_class = node.name

        methods_before = len(self.functions)
        self.generic_visit(node)
        methods = self.functions[methods_before:]

        class_info = ClassInfo(
            name=node.name,
            methods=methods,
            docstring=docstring,
            file=self.file_path
        )

        self.classes.append(class_info)
        self._current_class = previous_class
