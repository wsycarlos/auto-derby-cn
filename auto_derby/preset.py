# -*- coding=UTF-8 -*-
# pyright: strict

from typing import Dict, Tuple

from .constants import TrainingType
from .single_mode import Context, Race
from .single_mode.race import RaceFilters
from .urarawin import UraraWin

import json

from . import app, data


class Preset:

    name: str = ""

    race_values: Dict[str, int]

    type_values: Tuple[int, int, int, int, int]

    def __init__(self, name: str, types: Tuple[int, int, int, int, int], races: Dict[str, int])-> None:
        self.name = name
        self.type_values = types
        self.race_values = races
    
    def score(self, old_score: float, match_name: str, ctx: Context) -> float:
        _value = self.race_values.get(match_name, 0)
        return old_score + _value
        
    def value(self) -> Dict[TrainingType, int]:
        return {
            TrainingType.SPEED: self.type_values[0],
            TrainingType.STAMINA: self.type_values[1],
            TrainingType.POWER: self.type_values[2],
            TrainingType.GUTS: self.type_values[3],
            TrainingType.WISDOM: self.type_values[4],
        }


class g:
    presets: Dict[str, Preset] = {}
    data: Dict[str, str] = {}
    path: str = ""
    current: str = ""


def register(name: str, preset: Preset) -> None:
    if name in g.presets:
        raise ValueError("preset.register: duplicated name is not allowed: %s" % name)
    g.presets[name] = preset


def reload():
    g.presets.clear()
    # a new sheet
    # settings = {}
    # for c in UraraWin.GetAllCharacters():
    #     races = {}
    #     for r in Race.repository.find():
    #         if r.grade == Race.GRADE_G1:
    #             races[r.name] = 5
    #         elif r.grade == Race.GRADE_G2:
    #             races[r.name] = 0
    #         elif r.grade == Race.GRADE_OP:
    #             races[r.name] = -5
    #         elif r.grade == Race.GRADE_PRE_OP:
    #             races[r.name] = -10
    #         else:
    #             races[r.name] = 0
    #     settings[c] = {"value":[800,800,800,300,300], "races": races}
    # with open(data.path("UmaMusumeAutoNuturing.json"), "w", encoding="utf-8") as file:
    #     file.write(json.dumps(settings, ensure_ascii=False, indent=2))
    # reset sheet
    # with open(data.path("UmaMusumeAutoNuturing.json"), "r", encoding="utf-8") as file:
    #     g.data = json.load(file)
    #     for d in g.data:
    #         g.data[d]["value"] = [800,800,800,300,300]
    #         for r in g.data[d]["races"]:
    #             race = next(Race.repository.find(filter_by=RaceFilters(name=(r,))))
    #             if race.grade == Race.GRADE_G1:
    #                 g.data[d]["races"][r] = 10
    #             elif race.grade == Race.GRADE_G2:
    #                 g.data[d]["races"][r] = 5
    #             elif race.grade == Race.GRADE_OP:
    #                 g.data[d]["races"][r] = -5
    #             elif race.grade == Race.GRADE_PRE_OP:
    #                 g.data[d]["races"][r] = -10
    #             else:
    #                 g.data[d]["races"][r] = 0
    # with open(data.path("UmaMusumeAutoNuturing.json"), "w", encoding="utf-8") as file:
    #     file.write(json.dumps(g.data, ensure_ascii=False, indent=2))
    # normal flow
    with open(data.path("UmaMusumeAutoNuturing.json"), "r", encoding="utf-8") as file:
        g.data = json.load(file)
    for d in g.data:
        p = Preset(d, g.data[d]["value"], g.data[d]["races"])
        g.presets[d] = p
    app.log.text("loaded: %s" % ", ".join(g.presets.keys()), level=app.DEBUG)

def set_current(name: str) -> None:
    g.current = name
    app.log.text("set current preset: %s" % name, level=app.DEBUG)

def get(name: str) -> Preset:
    return g.presets[name]

def get_current() -> Preset:
    return get(g.current)
