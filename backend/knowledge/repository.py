from typing import List
from .schemas import KnowledgeEntity
from storage.mongo import MongoConnection

class KnowledgeRepository:
    def __init__(self):
        self.collection = MongoConnection().get_collection("entities")

    def save_many(self, entities: List[KnowledgeEntity]):
        docs = [entity.__dict__ for entity in entities]
        if docs:
            self.collection.insert_many(docs)

    def find_all(self):
        return list(self.collection.find({}, {"_id": 0}))
