import os
import re
from typing import ClassVar, List, Literal, Mapping, Optional, Union

import requests
from pydantic import BaseModel, model_validator
from slugify import slugify
from tinydb.table import Document as TinyDocument
from warhammer_stats import PMFCollection
from warhammer_stats import Weapon as WWeapon


class Schema(BaseModel):
    doc_id: str = None
    name: str

    @model_validator(mode="before")
    @classmethod
    def check_card_number_omitted(cls, data: Mapping) -> Mapping:
        if "doc_id" not in data:
            data["doc_id"] = slugify(data.get("name", None))
        return data

    def to_document(self) -> TinyDocument:
        self_dict = dict(self)
        doc_id = self_dict.pop("doc_id")
        return TinyDocument(self_dict, doc_id)


class Repository(Schema):
    URL_BASE: ClassVar = "https://raw.githubusercontent.com/BSData/wh40k-10e/main/"
    url: str
    sha: str

    def load(self, mode: Literal["read", "write"]) -> Union["Repository", bytes]:
        if mode == "write":
            self._write_content()
            return self

        return self._read_content()

    def _write_content(self):
        response = requests.get(self.url)
        response.raise_for_status()

        with open(self.content_file_path, mode="wb") as write_file:
            write_file.write(response.content)

    def _read_content(self) -> bytes:
        with open(self.content_file_path, mode="rb") as read_file:
            return read_file.read()

    @property
    def content_file_path(self):
        return f"db/contents/{self.doc_id}.bin"


class Weapon(BaseModel):
    slug: str = "weapon"
    name: str = "weapon"
    skill: int
    attacks: Union[int, str]
    strength: int
    ap: int
    damage: Union[int, str]

    @staticmethod
    def dice_value_to_pmf(value) -> PMFCollection:
        if isinstance(value, int) or value.isnumeric():
            return PMFCollection.static(int(value))

        if re.match(r"^\d", value) is None:
            value = f"1{value}"

        static = None
        split = list(filter(None, value.split("D")))
        if "+" in split[-1]:
            split[-1], static = split[-1].split("+")
        split = list(map(int, split))

        pmf = PMFCollection.mdn(*split)
        if static:
            pmf = pmf.plus(int(static))

        return pmf

    @property
    def pmf_shots(self) -> PMFCollection:
        return self.dice_value_to_pmf(self.attacks)

    @property
    def pmf_damage(self) -> PMFCollection:
        return self.dice_value_to_pmf(self.damage)

    def to_stats_weapon(self) -> WWeapon:
        return WWeapon(
            bs=self.skill,
            shots=self.pmf_shots,
            strength=self.strength,
            ap=self.ap,
            damage=self.pmf_damage,
            name=self.name,
        )


class Unit(Schema):
    points: int = 0
    wounds: int
    toughness: int
    leadership: int
    oc: int = 0
    save: int
    invulnerable: Optional[int] = None
    fnp: Optional[int] = None
    melee_weapons: List[Weapon] = []
    ranged_weapong: List[Weapon] = []
    keywords: List[str]

    def to_target_dict(self) -> dict:
        return dict(
            toughness=self.toughness,
            save=self.save or 7,
            invuln=self.invulnerable or 7,
            fnp=self.fnp or 7,
            wounds=self.wounds,
            name=self.name,
            cost=self.points,
        )
