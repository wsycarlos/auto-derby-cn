# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type, Text, Tuple

from ...constants import TrainingType

if TYPE_CHECKING:
    from .partner import Partner
    from .training import Training


class g:
    training_class: Type[Training]
    partner_class: Type[Partner]
    target_levels: Dict[TrainingType, int] = {}
    target_values: Dict[TrainingType, int] = {}
    force_races: Tuple[Text, ...]
    prefered_races: Tuple[Text, ...]
    avoid_races: Tuple[Text, ...]

    target_config: str

    # deprecated
    image_path: str = ""  # replaced by web log
