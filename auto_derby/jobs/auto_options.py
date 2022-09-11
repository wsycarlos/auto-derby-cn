import time

from .. import action, app, templates
from ..single_mode import event

ALL_OPTIONS = [
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
]

def auto_options():

    while True:

        tmpl, _ = action.wait_image(templates.SINGLE_MODE_OPTION1, templates.SINGLE_MODE_FINISH_BUTTON)
        
        if tmpl.name == templates.SINGLE_MODE_FINISH_BUTTON:
            break
        
        time.sleep(0.2)  # wait animation
        ans = event.get_choice(app.device.screenshot(max_age=0))
        action.tap_image(ALL_OPTIONS[ans - 1])