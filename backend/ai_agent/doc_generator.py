from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import ast

class DocGenerator:
    def __init__(self, device="cpu"):
        self.device = device
        print("Loading model: Salesforce/codegen-350M-mono")

        self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
        self.model = AutoModelForCausalLM.from_pretrained(
            "Salesforce/codegen-350M-mono",
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        ).to(self.device)

        self.model.eval()
        print("Model loaded")

    def _build_prompt(self, entity: dict) -> str:
        classes_block = "\n".join(
            f"- {cls['name']} ({', '.join(cls['methods'])})"
            for cls in entity.get("classes", [])
        ) or "None"

        functions_block = "\n".join(
            f"- {fn}" for fn in entity.get("functions", [])
        ) or "None"

        deps_block = ", ".join(entity.get("dependencies", [])) or "None"

        return f"""
# Python file documentation
File name: {entity['name']}

Purpose: {entity.get('purpose', 'Not specified')}

Classes:
{classes_block}

Functions:
{functions_block}

Dependencies:
{deps_block}

Write a concise technical description of this file in clear English.
"""

    def generate_description(self, entity: dict) -> str:
        prompt = self._build_prompt(entity)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.2,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return text.replace(prompt, "").strip()

    def generate_markdown(self, entities: list[dict]) -> str:
        md = "# 📄 Auto-generated Documentation\n\n"
        for e in entities:
            desc = self.generate_description(e)
            md += f"## `{e['name']}`\n\n{desc}\n\n---\n\n"
        return md

# AST-парсер
def parse_python_file(content: str):
    tree = ast.parse(content)
    classes, functions, dependencies = [], [], []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes.append({"name": node.name, "methods": methods})
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for alias in n.names:
                dependencies.append(alias.name)
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                dependencies.append(n.module)

    return {
        "name": None,
        "classes": classes,
        "functions": functions,
        "dependencies": list(set(dependencies)),
        "purpose": "Not specified"
    }
