from tinydb import TinyDB

from .tables import Repositories, Table


class DB(TinyDB):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.table(Repositories)

    def table(self, *args, **kwargs) -> Table:
        first_arg = args[0]
        if isinstance(first_arg, str):
            name, table_class = first_arg, self.table_class
        else:
            name, table_class = first_arg.__name__.lower(), first_arg

        if name in self._tables:
            return self._tables[name]

        table = table_class(self.storage, name, **kwargs)
        self._tables[name] = table

        return table
