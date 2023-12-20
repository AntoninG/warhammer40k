from typing import Callable

from tinydb.storages import Storage
from tinydb.table import Document as TinyDocument
from tinydb.table import Table as TinyTable

from .schemas import Repository, Schema


def document_output_class(schema: Schema) -> Callable:
    def output(doc: TinyDocument, doc_id: str) -> Schema:
        return schema(**doc, doc_id=doc_id)

    return output


class Table(TinyTable):
    schema: Schema
    document_id_class = str

    def __init__(self, storage: Storage, name: str, cache_size: int = ...):
        super().__init__(storage, name, cache_size)
        self.document_class = document_output_class(self.schema)


class Repositories(Table):
    schema = Repository
