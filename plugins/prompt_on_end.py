import auto_derby
from auto_derby.single_mode import Context
from auto_derby import terminal


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next = auto_derby.config.on_single_mode_end

        def _handle(ctx: Context) -> None:
            terminal.pause(f"pause after nurturing!")

        auto_derby.config.on_single_mode_end = _handle


auto_derby.plugin.register(__name__, Plugin())
