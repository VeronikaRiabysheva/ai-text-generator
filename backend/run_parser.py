# from parser.code_parser import CodeParser
#
# parser = CodeParser("./parser")
# parser.parse()
#
# print("Функции:")
# for f in parser.functions:
#     print(f)
#
# print("\nКлассы:")
# for c in parser.classes:
#     print(c.name)
#
#     from knowledge.extractor import KnowledgeExtractor
#
#     extractor = KnowledgeExtractor()
#     knowledge = extractor.extract(parser.functions, parser.classes)
#
#     print("\nЗНАНИЯ:")
#     for k in knowledge:
#         print(k)
#
# from knowledge.repository import KnowledgeRepository
#
# repo = KnowledgeRepository()
# repo.save_many(knowledge)
#
# print("\nСохранено в MongoDB:")
# for item in repo.find_all():
#     print(item)


# from ai_agent.doc_generator import DocGenerator
#
# generator = DocGenerator()
# markdown = generator.generate_markdown()
#
# # Сохраняем в файл
# with open("documentation.md", "w", encoding="utf-8") as f:
#     f.write(markdown)
#
# print("Документация сгенерирована: documentation.md")
#

from ai_agent.doc_generator import DocGenerator

generator = DocGenerator()
generator.generate_markdown()
