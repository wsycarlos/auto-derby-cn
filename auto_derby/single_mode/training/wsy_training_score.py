# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import mathtools
from .globals import g
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Context
    from .training import Training

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

    spd = compute_spd(ctx, trn, t_now)
    sta = compute_sta(ctx, trn, t_now)
    pow_ = compute_pow(ctx, trn, t_now)
    gut = compute_gut(ctx, trn, t_now)
    wis = compute_wis(ctx, trn, t_now)
    skill = compute_skill(ctx, trn, t_now)
    partner = compute_partner(ctx, trn, t_now)

    vit = compute_vit(ctx, trn, t_now)

    return (spd + sta + pow_ + gut + wis + skill + partner + hint) * success_rate + vit - fail_penalty * trn.failure_rate

    
def compute_spd(ctx: Context, trn: Training, t_now: int) -> float:
    
    spd = mathtools.integrate(
        ctx.speed,
        trn.speed,
        (
            (0, 2.0),
            (300, 1.0),
            (600, 0.8),
            (900, 0.7),
            (1100, 0.5),
            (1120, 0.1),
        ),
    )
    if ctx.speed < t_now / 24 * 300:
        spd *= 1.5
    return spd
    
def compute_sta(ctx: Context, trn: Training, t_now: int) -> float:
    
    sta = 0

    if g.traget_distance == "short":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            (
                (0, 2.0),
                (200, 1.0),
                (300, 0.8),
                (350, 0.7),
                (400, 0.5),
                (450, 0.1),
            ),
        )
    elif g.traget_distance == "miles":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            (
                (0, 2.0),
                (300, 1.0),
                (400, 0.8),
                (500, 0.6),
                (600, 0.4),
                (650, 0.1),
            ),
        )
    elif g.traget_distance == "medium":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            (
                (0, 2.0),
                (300, 1.0),
                (500, 0.8),
                (600, 0.6),
                (800, 0.4),
                (850, 0.1),
            ),
        )
    elif g.traget_distance == "long":
        sta = mathtools.integrate(
            ctx.stamina,
            trn.stamina,
            (
                (0, 2.0),
                (300, 1.0),
                (600, 0.8),
                (850, 0.5),
                (1080, 0.3),
                (1120, 0.1),
            ),
        )
    
    return sta
    
def compute_pow(ctx: Context, trn: Training, t_now: int) -> float:

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
    
def compute_gut(ctx: Context, trn: Training, t_now: int) -> float:
    
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
    
def compute_wis(ctx: Context, trn: Training, t_now: int) -> float:
    
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