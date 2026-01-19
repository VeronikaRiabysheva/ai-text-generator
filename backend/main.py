# backend/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ai_agent.doc_generator import DocGenerator
from parser.code_parser import CodeParser

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

generator = DocGenerator(device="cpu")

# ----------------- Простая генерация текста на Python -----------------
# backend/main.py
def generate_simple_description(file_path: str) -> str:
    parser = CodeParser(file_path)
    parser.parse_file()

    desc = f"File: {file_path}\n"

    if parser.classes:
        desc += "\nClasses:\n"
        for cls in parser.classes:
            desc += f" - {cls.name}\n"
            if cls.docstring:
                desc += f"   Docstring: {cls.docstring}\n"
            if cls.decorators:
                desc += f"   Decorators: {', '.join(cls.decorators)}\n"
            for m in cls.methods:
                async_str = "async " if m.is_async else ""
                desc += f"   - {async_str}{m.name}({', '.join(m.args)})\n"
                if m.docstring:
                    desc += f"     Docstring: {m.docstring}\n"
                if m.decorators:
                    desc += f"     Decorators: {', '.join(m.decorators)}\n"
                for c in m.comments:
                    desc += f"     Comment: {c}\n"
            for ic in cls.inner_classes:
                desc += f"   Inner class: {ic.name}\n"
                if ic.docstring:
                    desc += f"     Docstring: {ic.docstring}\n"
                if ic.decorators:
                    desc += f"     Decorators: {', '.join(ic.decorators)}\n"
            for c in cls.comments:
                desc += f"   Class comment: {c}\n"

    if parser.functions:
        desc += "\nFunctions:\n"
        for fn in parser.functions:
            async_str = "async " if fn.is_async else ""
            desc += f" - {async_str}{fn.name}({', '.join(fn.args)})\n"
            if fn.docstring:
                desc += f"   Docstring: {fn.docstring}\n"
            if fn.decorators:
                desc += f"   Decorators: {', '.join(fn.decorators)}\n"
            for c in fn.comments:
                desc += f"   Comment: {c}\n"

    if parser.dependencies:
        desc += "\nDependencies:\n"
        for dep in parser.dependencies:
            desc += f" - {dep}\n"

    return desc


@app.post("/generate")
async def generate(files: list[UploadFile] = File(...)):
    results = []

    for file in files:
        temp_path = f"temp_{file.filename}"
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # ИИ генерация
        entity = {"name": file.filename, "classes": [], "functions": [], "dependencies": []}
        ai_desc = generator.generate_description(entity)

        # Чистый Python
        py_desc = generate_simple_description(temp_path)

        results.append({
            "file": file.filename,
            "ai_description": ai_desc,
            "python_description": py_desc
        })

    return {"results": results}
