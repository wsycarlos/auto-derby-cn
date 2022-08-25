from auto_derby.single_mode.commands.race import RaceResult
from auto_derby.single_mode.context import Context
import auto_derby
from auto_derby import action, templates


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next = auto_derby.config.on_single_mode_race_result

        def _handle(ctx: Context, result: RaceResult):
            if result.is_failed:
                action.wait_tap_image(templates.SINGLE_MODE_END_BUTTON)
            _next(ctx, result)

        def _should_retry_race(ctx: Context, result: RaceResult) -> bool:
            return False

        auto_derby.config.single_mode_should_retry_race = _should_retry_race
        auto_derby.config.on_single_mode_race_result = _handle


auto_derby.plugin.register(__name__, Plugin())
