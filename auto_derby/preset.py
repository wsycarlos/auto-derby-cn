# -*- coding=UTF-8 -*-
# pyright: strict


import importlib.util
from abc import ABC, abstractmethod
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Dict

from .constants import TrainingType
from .single_mode import Context

import cast_unknown as cast

from . import app


class Preset(ABC):
    @abstractmethod
    def score(self, old_score: float, match_name: str, ctx: Context) -> float:
        ...
    @abstractmethod
    def value(self) -> Dict[TrainingType, int]:
        ...


class g:
    presets: Dict[str, Preset] = {}
    path: str = ""
    current: str = ""


def register(name: str, preset: Preset) -> None:
    if name in g.presets:
        raise ValueError("preset.register: duplicated name is not allowed: %s" % name)
    g.presets[name] = preset


def reload():
    g.presets.clear()
    for i in Path(g.path).glob("*.py"):
        spec = importlib.util.spec_from_file_location(i.stem, i)
        assert spec
        module = importlib.util.module_from_spec(spec)
        loader = cast.instance(spec.loader, SourceFileLoader)
        loader.exec_module(module)
    app.log.text("loaded: %s" % ", ".join(g.presets.keys()), level=app.DEBUG)

def set_current(name: str) -> None:
    g.current = name
    app.log.text("set current preset: %s" % name, level=app.DEBUG)


def get(name: str) -> Preset:
    return g.presets[name]

def get_current() -> Preset:
    return get(g.current)
