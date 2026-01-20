# backend/code_parser.py
import ast
from pathlib import Path
from typing import List, Optional


class FunctionInfo:
    def __init__(self, name: str):
        self.name: str = name
        self.args: List[str] = []
        self.defaults: List[str] = []
        self.docstring: Optional[str] = None
        self.decorators: List[str] = []
        self.is_async: bool = False
        self.comments: List[str] = []


class ClassInfo:
    def __init__(self, name: str):
        self.name: str = name
        self.docstring: Optional[str] = None
        self.decorators: List[str] = []
        self.methods: List[FunctionInfo] = []
        self.inner_classes: List['ClassInfo'] = []
        self.comments: List[str] = []


class CodeParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.dependencies: List[str] = []

    def parse_file(self):
        """Парсим один файл и собираем всё"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                source = f.read()
                tree = ast.parse(source)
                self._comments = self._extract_comments(source)

            self.visit(tree)
        except Exception as e:
            print(f"Ошибка при разборе {self.file_path}: {e}")

    def _extract_comments(self, source: str) -> List[str]:
        """Собираем все комментарии в файле"""
        import tokenize
        from io import StringIO

        comments = []
        try:
            tokens = tokenize.generate_tokens(StringIO(source).readline)
            for toknum, tokval, _, _, _ in tokens:
                if toknum == tokenize.COMMENT:
                    comments.append(tokval.strip("# ").strip())
        except Exception:
            pass
        return comments

    # ----------------- AST Visitors -----------------
    def visit(self, node):
        """Рекурсивный обход AST"""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visitor(node)

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Import(self, node):
        for n in node.names:
            self.dependencies.append(n.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        for n in node.names:
            self.dependencies.append(f"{module}.{n.name}" if module else n.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        fn = self._create_function_info(node, is_async=False)
        self.functions.append(fn)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        fn = self._create_function_info(node, is_async=True)
        self.functions.append(fn)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        cls = self._create_class_info(node)
        self.classes.append(cls)
        self.generic_visit(node)

    # ----------------- Вспомогательные функции -----------------
    def _create_function_info(self, node, is_async=False) -> FunctionInfo:
        fn = FunctionInfo(node.name)
        fn.args = [arg.arg for arg in node.args.args]
        fn.defaults = [ast.unparse(d) for d in node.args.defaults] if node.args.defaults else []
        fn.docstring = ast.get_docstring(node)
        fn.decorators = [ast.unparse(d) for d in node.decorator_list] if node.decorator_list else []
        fn.is_async = is_async

        # комментарии внутри функции
        try:
            src = ast.get_source_segment(open(self.file_path, "r", encoding="utf-8").read(), node)
            fn.comments = [c for c in self._comments if c in src]
        except Exception:
            fn.comments = []

        return fn

    def _create_class_info(self, node) -> ClassInfo:
        cls = ClassInfo(node.name)
        cls.docstring = ast.get_docstring(node)
        cls.decorators = [ast.unparse(d) for d in node.decorator_list] if node.decorator_list else []

        for n in node.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = self._create_function_info(n, is_async=isinstance(n, ast.AsyncFunctionDef))
                cls.methods.append(fn)
            elif isinstance(n, ast.ClassDef):
                inner_cls = self._create_class_info(n)
                cls.inner_classes.append(inner_cls)
            elif isinstance(n, ast.Expr):
                if isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                    cls.comments.append(n.value.value)

        return cls
