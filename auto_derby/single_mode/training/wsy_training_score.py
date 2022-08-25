# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import mathtools
from .globals import g
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Context
    from .training import Training

default_speed_matrix = ((0, 2.0), (300, 1.0), (600, 0.8), (900, 0.7), (1100, 0.5), (1120, 0.1))

default_short_stamina_matrix = ((0, 2.0), (200, 1.0), (300, 0.8), (350, 0.7), (400, 0.5), (450, 0.1))
default_miles_stamina_matrix = ((0, 2.0), (300, 1.0), (400, 0.8), (500, 0.6), (600, 0.4), (650, 0.1))
default_medium_stamina_matrix = ((0, 2.0), (300, 1.0), (500, 0.8), (600, 0.6), (800, 0.4), (850, 0.1))
default_long_stamina_matrix = ((0, 2.0), (300, 1.0), (600, 0.8), (850, 0.5), (1080, 0.3), (1120, 0.1))

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

    if g.traget_distance == "custom":
        target_speed = g.target_values.get(trn.TYPE_SPEED, -1)
        if target_speed > 0:
            spd = compute_target_value(ctx.speed, trn.speed, target_speed)
        elif target_speed == 0:
            spd = 0
        else:
            spd = compute_default_spd(ctx, trn, t_now)
            
        target_stamina = g.target_values.get(trn.TYPE_STAMINA, -1)
        if target_stamina > 0:
            sta = compute_target_value(ctx.stamina, trn.stamina, target_stamina)
        elif target_stamina == 0:
            sta = 0
        else:
            sta = compute_default_sta(ctx, trn, t_now)
        
        target_power = g.target_values.get(trn.TYPE_POWER, -1)
        if target_power > 0:
            pow_ = compute_target_value(ctx.power, trn.power, target_power)
        elif target_power == 0:
            pow_ = 0
        else:
            pow_ = compute_default_pow(ctx, trn, t_now)
        
        target_gut = g.target_values.get(trn.TYPE_GUTS, -1)
        if target_gut > 0:
            gut = compute_target_value(ctx.guts, trn.guts, target_gut)
        elif target_gut == 0:
            gut = 0
        else:
            gut = compute_default_gut(ctx, trn, t_now)
        
        target_wisdom = g.target_values.get(trn.TYPE_WISDOM, -1)
        if target_wisdom > 0:
            wis = compute_target_value(ctx.wisdom, trn.wisdom, target_wisdom)
        elif target_wisdom == 0:
            wis = 0
        else:
            wis = compute_default_wis(ctx, trn, t_now)
    else:
        spd = compute_default_spd(ctx, trn, t_now)
        sta = compute_default_sta(ctx, trn, t_now)
        pow_ = compute_default_pow(ctx, trn, t_now)
        gut = compute_default_gut(ctx, trn, t_now)
        wis = compute_default_wis(ctx, trn, t_now)


    skill = compute_skill(ctx, trn, t_now)
    partner = compute_partner(ctx, trn, t_now)

    vit = compute_vit(ctx, trn, t_now)

    return (spd + sta + pow_ + gut + wis + skill + partner + hint) * success_rate + vit - fail_penalty * trn.failure_rate

def compute_target_value(ctx_value:int, trn_value:int, target_value: int) -> float:

    matrix = (
        (0, 2.0),
        ((int)(target_value * 0.25), 1.0),
        ((int)(target_value * 0.5), 0.8),
        (target_value, 0.5),
        ((int)(target_value * 1.1), 0.1)
    )

    val = mathtools.integrate(
        ctx_value,
        trn_value,
        matrix,
    )

    return val

    
def compute_default_spd(ctx: Context, trn: Training, t_now: int) -> float:
    
    spd = mathtools.integrate(
        ctx.speed,
        trn.speed,
        default_speed_matrix,
    )
    if ctx.speed < t_now / 24 * 300:
        spd *= 1.5
    return spd
    
def compute_default_sta(ctx: Context, trn: Training, t_now: int) -> float:
    
    sta = 0

    if g.traget_distance == "short":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            default_short_stamina_matrix,
        )
    elif g.traget_distance == "miles":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            default_miles_stamina_matrix,
        )
    elif g.traget_distance == "medium":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            default_medium_stamina_matrix,
        )
    elif g.traget_distance == "long":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            default_long_stamina_matrix,
        )
    
    return sta
    
def compute_default_pow(ctx: Context, trn: Training, t_now: int) -> float:

    pow = mathtools.integrate(
        ctx.power,
        trn.power,
        (
            (0, 1.0),
            (300, 0.2 + ctx.speed / 600),
            (600, 0.1 + ctx.speed / 900),
            (900, ctx.speed / 900 / 3),
            (1120, 0.1),
        ),
    )
    return pow
    
def compute_default_gut(ctx: Context, trn: Training, t_now: int) -> float:
    
    gut = mathtools.integrate(
        ctx.guts,
        trn.guts,
        (
            (0, 2.0),
            (300, 1.0),
            (400, 0.3),
            (600, 0.1),
        )
        if ctx.speed > 400 / 24 * t_now
        else
        (
            (0, 2.0),
            (300, 0.5),
            (400, 0.1)
        ),
    )
    return gut
    
def compute_default_wis(ctx: Context, trn: Training, t_now: int) -> float:
    
    wis = mathtools.integrate(
        ctx.wisdom,
        trn.wisdom,
        (
            (0, 2.0),
            (300, 0.8),
            (600, 0.5),
            (900, 0.3),
            (1120, 0.1),
        ),
    )
    if ctx.wisdom > 300 and ctx.speed < min(1120, 300 / 24 * t_now):
        wis *= 0.1

    return wis
    
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