# -*- coding=UTF-8 -*-
# pyright: strict

from typing import Text

from .. import action, templates


def daily_race(race_name: Text):
    while True:
        name, pos = action.wait_image(
            templates.DAILY_RACE_TICKET_NOT_ENOUGH,
            templates.CONNECTING,
            templates.RETRY_BUTTON,
            templates.DAILY_RACE,
            templates.DAILY_RACE_HARD,
            templates.RACE_START_BUTTON,
            templates.RACE_CONFIRM_BUTTON,
            templates.GREEN_NEXT_BUTTON,
            templates.RACE_RESULT_BUTTON,
            templates.RACE_AGAIN_BUTTON,
            templates.RACE_RESULT_NO1,
            race_name,
            templates.RACE_BUTTON,
        )
        if name == templates.CONNECTING:
            pass
        elif name == templates.DAILY_RACE_TICKET_NOT_ENOUGH:
            break
        else:
            action.click(pos)