import re
from typing import List

from cement import Controller, ex
from warhammer_stats import MultiAttack, Target
from warhammer_stats import Weapon as WWeapon

from db.schemas import Unit, Weapon


def parse_weapon_arg(arg_value):
    weapon_pattern = r"".join(
        [
            r"^",
            r"(?P<attacks>[^A]+)",
            r"(?:AP(?P<ap>\d))?",
            r"S(?P<strength>\d{1,2})",
            r"D(?P<damage>(?:\d{1,2})|(?:\d?D\d(?:\+\d)?))",
            r"H(?P<skill>\d)\+",
            r"$",
        ]
    )

    if (match := re.match(weapon_pattern, arg_value)) is None:
        raise ValueError(
            f":attack: arg {arg_value} does not match pattern {weapon_pattern}"
        )

    return dict(**match.groupdict())


def parse_target_arg(arg_value):
    target_pattern = r"".join(
        [
            r"^",
            r"T(?P<toughness>\d+)",
            r"W(?P<wounds>\d+)",
            r"SV(?:(?P<save>\d)\+)(?:/?(?P<invuln>\d)\+\+)?(?:/?(?P<fnp>\d)\+\+\+)?",
            r"$",
        ]
    )

    if (match := re.match(target_pattern, arg_value)) is None:
        raise ValueError(
            f":defense: arg {arg_value} does not match pattern {target_pattern}"
        )

    return dict(**match.groupdict())


class MathHammer(Controller):
    class Meta:
        label = "mathhammer"
        stacked_type = "embedded"
        stacked_on = "base"

    @ex(
        help="Attack simulator",
        arguments=[
            (
                ["-w"],
                {
                    "action": "store",
                    "nargs": "+",
                    "type": parse_weapon_arg,
                    "dest": "weapons",
                    "required": True,
                    "help": "4AP2S6D2H3+",
                },
            ),
            (
                ["-t"],
                {
                    "action": "store",
                    "type": parse_target_arg,
                    "dest": "target",
                    "required": True,
                    "help": "T11W13SV2+/4++/5+++",
                },
            ),
            (
                ["--cost", "--pts"],
                {
                    "action": "store",
                    "type": int,
                    "default": 0,
                    "help": "Cost of target",
                    "dest": "cost",
                },
            ),
        ],
    )
    def raw_attack(self):
        weapons = self._weapons(self.app.pargs.weapons)
        target = self._target(self.app.pargs.target)

        attacks = MultiAttack(weapons, target).run()
        self.app.log.info(attacks)

        if cost := self.app.pargs.cost:
            damage_per_point = round(attacks.total_damage_dist.mean() / cost, 2)
            self.app.log.info(f"{damage_per_point} damage per point")

    def _weapons(weapons_arg: List[dict]) -> List[WWeapon]:
        return [
            Weapon(
                skill=int(weapon_arg["skill"]),
                attacks=weapon_arg["attacks"],
                strength=int(weapon_arg["strength"]),
                ap=int(weapon_arg["ap"] or 0),
                damage=weapon_arg["damage"],
            ).to_stats_weapon()
            for weapon_arg in weapons_arg
        ]

    def _target(target_arg: dict) -> Target:
        Target(
            **Unit(
                name="target",
                wounds=int(target_arg["wounds"]),
                toughness=int(target_arg["toughness"]),
                leadership=0,
                oc=0,
                save=int(target_arg["save"]),
                invulnerable=int(target_arg["invuln"] or 7),
                fnp=int(target_arg["fnp"] or 7),
                keywords=[],
            ).to_target_dict()
        )
