# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import mathtools
from ... import preset
from .globals import g
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Context
    from .training import Training

default_speed_matrix = ((0, 2.0), (300, 1.0), (600, 0.8), (900, 0.7), (1100, 0.5), (1120, 0.1))

default_short_stamina_matrix = ((0, 2.0), (200, 1.0), (300, 0.8), (350, 0.7), (400, 0.5), (450, 0.1))
default_miles_stamina_matrix = ((0, 2.0), (300, 1.0), (400, 0.8), (500, 0.6), (600, 0.4), (650, 0.1))
default_medium_stamina_matrix = ((0, 2.0), (400, 1.0), (600, 0.8), (700, 0.6), (800, 0.4), (850, 0.1))
default_long_stamina_matrix = ((0, 2.0), (450, 1.0), (650, 0.8), (850, 0.5), (1080, 0.3), (1120, 0.1))

def compute(ctx: Context, trn: Training) -> float:
    t_now = ctx.turn_count_v2()

    success_rate = 1 - trn.failure_rate
        
    fail_penalty = 0
    if trn.type != trn.TYPE_WISDOM:
        fail_penalty = mathtools.interpolate(
            t_now,
            (
                (0, 30),
                (72, 60),
            )
        )
        
    has_hint = any(i for i in trn.partners if i.has_hint)
    hint = 3 if has_hint else 0
    
    spd = 0
    sta = 0
    pow_ = 0
    gut = 0
    wis = 0
    
    preset_speed = preset.get_current().value().get(trn.TYPE_SPEED, -1)
    preset_stamina = preset.get_current().value().get(trn.TYPE_STAMINA, -1)
    preset_power = preset.get_current().value().get(trn.TYPE_POWER, -1)
    preset_gut = preset.get_current().value().get(trn.TYPE_GUTS, -1)
    preset_wisdom = preset.get_current().value().get(trn.TYPE_WISDOM, -1)

    spd = compute_target_value(ctx.speed, trn.speed, preset_speed)
    sta = compute_target_value(ctx.stamina, trn.stamina, preset_stamina)
    pow_ = compute_target_value(ctx.power, trn.power, preset_power)
    gut = compute_target_value(ctx.guts, trn.guts, preset_gut)
    wis = compute_target_value(ctx.wisdom, trn.wisdom, preset_wisdom)


    skill = compute_skill(ctx, trn, t_now)
    partner = compute_partner(ctx, trn, t_now)

    vit = compute_vit(ctx, trn, t_now)

    return (spd + sta + pow_ + gut + wis + skill + partner + hint) * success_rate + vit - fail_penalty * trn.failure_rate

def compute_target_value(ctx_value:int, trn_value:int, target_value: int) -> float:

    matrix = (
        (0, 2.0),
        ((int)(target_value * 0.5), 1.0),
        ((int)(target_value * 0.75), 0.8),
        (target_value, 0.5),
        ((int)(target_value * 1.1), 0.1)
    )

    val = mathtools.integrate(
        ctx_value,
        trn_value,
        matrix,
    )

    return val
    
def compute_vit(ctx: Context, trn: Training, t_now: int) -> float:
    
    vit = mathtools.clamp(trn.vitality, 0, 1 - ctx.vitality) * ctx.max_vitality * 0.6
    
    if ctx.date[1:] in ((6, 1),):
        vit *= 1.2
    if ctx.date[1:] in ((6, 2), (7, 1), (7, 2), (8, 1)):
        vit *= 1.5
    if ctx.date[0] == 4:
        vit *= 0.3

    return vit
    
def compute_skill(ctx: Context, trn: Training, t_now: int) -> float:
    
    skill = trn.skill * 0.5
    
    return skill
    
def compute_partner(ctx: Context, trn: Training, t_now: int) -> float:
    
    partner = 0
    
    for i in trn.partners:
        partner += i.score(ctx)

    return partner