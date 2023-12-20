import json
import re
from typing import List

from cement import Controller, ex
from slugify import slugify

from db.schemas import Repository
from db.tables import Repositories
from warhammer40k.ext.tree import Codex as CodexTree


def _search_list(values: List[str], search: str) -> List[str]:
    return list(
        filter(
            lambda value: (
                re.match(
                    r"(?:" + "|".join(search.lower().split(" ")) + r")", value.lower()
                )
                is not None
            ),
            values,
        )
    )


class Codex(Controller):
    class Meta:
        label = "codex"
        stacked_type = "embedded"
        stacked_on = "base"

    @ex(
        help="List codexes",
        arguments=[
            (["--search", "-s"], {"action": "store", "type": str, "default": None}),
        ],
    )
    def codexes(self):
        search = self.app.pargs.search
        table: Repositories = self.app.repositories
        repositories = list(map(lambda repository: repository.name, table.all()))
        repositories.sort()

        if search:
            repositories = _search_list(repositories, search)

        self.app.log.info(json.dumps(repositories, indent=2))

    @ex(
        help="Search codex and display units within",
        arguments=[
            (["codex"], {"action": "store", "type": str}),
            (["--search", "-s"], {"action": "store", "type": str, "default": None}),
        ],
    )
    def units(self):
        codex_name = self.app.pargs.codex
        search = self.app.pargs.search
        table = self.app.repositories

        repository: Repository = table.get(doc_id=slugify(codex_name))
        if not repository:
            raise ValueError(f"Unknown codex {codex}")

        codex = CodexTree.from_binary(repository.load("read"))
        units = codex.unit_names()
        units.sort()

        if search:
            units = _search_list(units, search)

        self.app.log.info(json.dumps(units, indent=2))
