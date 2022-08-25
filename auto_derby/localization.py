# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Any, Dict, Set

import csv

from . import data

class Localization:

    instance: Localization

    labels: Dict[str, str] = {}
    label_path: Any = None

    def __init__(self, path: str) -> None:
        self.label_path = data.path(path)
        with open(self.label_path, "r", encoding="utf-8") as f:
            label_file = csv.reader(f)
            for row in label_file:
                source_text = row[0]
                dest_text = row[1]
                self.labels[source_text] = dest_text

    @staticmethod
    def Find(Key:Any):
        Key = str(Key)
        return Localization.instance.labels.get(Key,Key)
        
    @staticmethod
    def FindSet(Keys:set[Any]):
        ret:Set[str] = set()
        for Key in Keys:
            _text = Localization.instance.labels.get(Key,Key)
            ret.add(_text)
        return ret

Localization.instance = Localization("localizations.csv")