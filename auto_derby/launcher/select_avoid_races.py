# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

if True:
    import sys
    import os

    sys.path.insert(0, os.path.join(__file__, "../../.."))


from select_races import *

from auto_derby import config
from auto_derby.single_mode import Race


def main():
    races = [
        {"name": race.name, "doc": str(race)}
        for race in Race.repository.find()
        if (race.grade == Race.GRADE_PRE_OP or race.grade == Race.GRADE_OP or race.grade == Race.GRADE_G3 or race.grade == Race.GRADE_G2 or race.grade == Race.GRADE_G1) and race.permission != Race.PERMISSION_URA
    ]
    value = fetch_races(races, config.single_mode_training_avoid_races)
    print(f"\nAUTO_DERBY_SINGLE_MODE_AVOID_RACES={','.join(value)}\n")


if __name__ == "__main__":
    main()
