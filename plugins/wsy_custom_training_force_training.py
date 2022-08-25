import auto_derby
from auto_derby import single_mode, mathtools
from auto_derby.single_mode import training
from auto_derby.single_mode.training import wsy_training_score

class Training(single_mode.Training):
    def score(self, ctx: single_mode.Context) -> float:

        training_score = wsy_training_score.compute(ctx, self)

        t_now = ctx.turn_count_v2()
        sigma = mathtools.interpolate(
                t_now,
                (
                    (0, 5),
                    (24, 5),
                    (48, 5),
                    (72, 0),
                ),
            )

        return training_score + sigma


class Race(auto_derby.config.single_mode_race_class):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        if ctx.target_fan_count <= ctx.fan_count:
            ret -= 100
        return ret

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_training_class = Training
        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())
