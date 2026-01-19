from pymongo import MongoClient

class MongoConnection:
    def __init__(self, uri="mongodb://localhost:27017", db_name="code_knowledge"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, name: str):
        return self.db[name]
