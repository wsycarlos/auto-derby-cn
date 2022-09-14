# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from auto_derby import web
from typing import List, Dict, Text, Tuple

import uuid


def fetch_races(races: List[Dict[Text, Text]], default_value: Tuple[Text, ...]):

    token = uuid.uuid4().hex
    form_data = web.prompt(
        web.page.render_cn(
            {
                "type": "RACES_SELECT",
                "submitURL": "?token=" + token,
                "races": races,
                "defaultValue": default_value,
            }
        ),
        web.page.ASSETS,
        web.middleware.Debug(),
        web.middleware.TokenAuth(token, ("POST",)),
    )
    return form_data["value"]