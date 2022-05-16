from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from common.log_out import log_err
from common.config import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_USR, MONGO_PWD


class MongoPipeline:
    def __init__(self, COLLECTION):
        if MONGO_USR and MONGO_PWD:
            client = MongoClient(f'mongodb://{MONGO_USR}:{MONGO_PWD}@{MONGO_HOST}:{MONGO_PORT}')
        else:
            client = MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}')
        self.coll = client[MONGO_DB][COLLECTION]

    def insert_item(self, item):
        status = False
        if not item:return False
        elif isinstance(item, list):
            for _i in item:
                try:
                    self.coll.insert_one(_i)
                    print(_i)
                except DuplicateKeyError:
                    status = True
                except Exception as error:
                    log_err(error)
                    status = True
        elif isinstance(item, dict):
            try:
                self.coll.insert_one(item)
                print(item)
            except DuplicateKeyError:
                status = True
                pass
            except Exception as error:
                log_err(error)
                status = True
        else:
            status = False
        return status

    @staticmethod
    def field_query(model, data):
        new_data = {}
        for key in model.keys():
            new_data.update({
                key: data.get(key)
            })
        return new_data

    def update_item(self, query, item):
        if not item: return
        if isinstance(item, list):
            for _i in item:
                try:
                    self.coll.update_one(self.field_query(query, _i), {'$set': _i}, upsert=True)
                except DuplicateKeyError:
                    pass
                except Exception as error:
                    log_err(error)
        elif isinstance(item, dict):
            try:
                self.coll.update_one(self.field_query(query, item), {'$set': item}, upsert=True)
            except Exception as error:
                log_err(error)

    def find(self, query):
        return self.coll.find(query)

    def find_one(self, query):
        return self.coll.find_one(query)

    def count(self, query):
        return self.coll.count_documents(query)
