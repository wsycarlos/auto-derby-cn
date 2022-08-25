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
                    (24, 3),
                    (48, 2),
                    (72, 0),
                ),
            )

        return training_score + sigma

class Race(auto_derby.config.single_mode_race_class):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        if ctx.target_fan_count > ctx.fan_count:
            pass
        elif self.grade in (Race.GRADE_OP, Race.GRADE_PRE_OP):
            ret -= 15
        elif self.grade == Race.GRADE_G1 and self.estimate_order(ctx) > 3:
            ret -= 10
        else:
            ret -= 5
        return ret

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_training_class = Training
        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())
