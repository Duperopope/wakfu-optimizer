"""
Wakfu Effect Bridge v2 - Connects BData StaticEffects to the Combat Engine.

Maps actionId + floatParams -> engine function calls.
Resolves: Spell.effectIds -> StaticEffect -> engine action.

Sources:
  - Decompiled wakfu-client.jar (aOC.java, aOx.java)
  - Community docs: https://methodwakfu.com
  - Extracted BData: all_spells.json, static_effects.json, breeds.json

Architecture:
  SpellExecutor.cast(fighter, spell_id, target)
    -> resolves effectIds
    -> for each effect: ActionResolver.execute(effect, caster, target, context)
      -> maps actionId to engine function
      -> calls fighter.take_damage(), fighter.gain_ap(), etc.

Date: 2026-03-13
"""

import json
import os
import logging
import math

logger = logging.getLogger("effect_bridge")

# ============================================================
# DATA LOADER
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "extracted")

_cache = {}

def _load_json(filename):
    if filename not in _cache:
        fpath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(fpath):
            logger.error(f"Data file not found: {fpath}")
            return []
        logger.info(f"Loading {filename}...")
        with open(fpath, 'r', encoding='utf-8') as f:
            _cache[filename] = json.load(f)
        logger.info(f"  Loaded {len(_cache[filename]):,} entries from {filename}")
    return _cache[filename]

def get_effects_index():
    if '_eff_idx' not in _cache:
        effects = _load_json("static_effects.json")
        _cache['_eff_idx'] = {e['id']: e for e in effects}
    return _cache['_eff_idx']

def get_spells_index():
    if '_spell_idx' not in _cache:
        spells = _load_json("all_spells.json")
        _cache['_spell_idx'] = {s['id']: s for s in spells}
    return _cache['_spell_idx']

def get_breeds():
    return _load_json("breeds.json")

def get_states_index():
    """Load all_states.json and build index by state ID."""
    if '_states_index' not in _cache:
        states = _load_json("all_states.json")
        _cache['_states_index'] = {s['id']: s for s in states}
        logger.info(f"States index: {len(_cache['_states_index']):,} states loaded")
    return _cache['_states_index']

def get_state(state_id):
    """Get a single state by ID."""
    idx = get_states_index()
    return idx.get(state_id)


def get_breed_spell_ids(breed_name):
    for b in get_breeds():
        if b.get('name', '').upper() == breed_name.upper():
            return b.get('spellIds', b.get('ehx', []))
    return []

# ============================================================
# HELPERS
# ============================================================
def fp(effect, index, default=0.0):
    """Safely get a floatParam by index."""
    params = effect.get('floatParams', [])
    if index < len(params):
        val = params[index]
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return default
        return val
    return default

ELEMENT_MAP = {0: "neutral", 1: "fire", 2: "water", 3: "earth", 4: "air", 5: "stasis", 6: "light"}

def _resolve_element(effect):
    if '_forced_element' in effect:
        return effect['_forced_element']
    return ELEMENT_MAP.get(effect.get('effectElement', 0), "neutral")

def _get_target_res(target, element):
    if not target or not hasattr(target, 'stats'):
        return 0
    s = target.stats if isinstance(target.stats, dict) else {}
    return s.get(f'res_{element}', s.get('resistance', 0))

# ============================================================
# ACTION REGISTRY
# ============================================================
ACTION_HANDLERS = {}

def register_action(action_id, name=None):
    def decorator(func):
        ACTION_HANDLERS[action_id] = {'handler': func, 'name': name or func.__name__}
        return func
    return decorator

# ============================================================
# CORE DAMAGE HELPER (used by all damage actions)
# ============================================================
def _do_damage(effect, caster, target, context, force_element=None):
    """Central damage calculation. Returns result dict."""
    from engine.damage import calculate_damage
    base = fp(effect, 0)
    element = force_element or _resolve_element(effect)
    is_melee = context.get('is_melee', True)
    is_rear = context.get('is_rear', False)
    is_crit = context.get('is_critical', False)
    is_berserk = context.get('is_berserk', False)
    is_area = context.get('is_area', False)
    is_indirect = context.get('is_indirect', False)
    orientation = context.get('orientation', None)

    caster_stats = caster.stats if hasattr(caster, 'stats') else {}
    caster_di = caster_stats.get('damage_inflicted', 0)
    target_res = _get_target_res(target, element)
    target_crit_res = _get_target_res(target, 'critical') if target else 0
    target_rear_res = _get_target_res(target, 'rear') if target else 0

    result = calculate_damage(
        base_damage=base,
        stats=caster_stats,
        element=element,
        target_elemental_res=target_res,
        target_critical_res=target_crit_res,
        target_rear_res=target_rear_res,
        is_melee=is_melee,
        is_rear=is_rear,
        is_critical=is_crit,
        is_berserk=is_berserk,
        is_area=is_area,
        is_indirect=is_indirect,
        caster_di=caster_di,
        orientation_override=orientation,
    )

    final = result.get('final_damage', base)
    actual = 0
    if target and final > 0:
        actual = target.take_damage(final)

    return {
        'action': 'HP_LOSS',
        'base': base,
        'element': element,
        'final_damage': final,
        'actual_damage': actual,
        'mastery': result.get('total_mastery', 0),
        'di': result.get('total_di', 0),
    }

# ============================================================
# DAMAGE ACTIONS
# ============================================================
@register_action(1, "HP_LOSS")
def action_hp_loss(effect, caster, target, context):
    return _do_damage(effect, caster, target, context)

@register_action(4, "HP_LOSS_INDIRECT")
def action_hp_loss_indirect(effect, caster, target, context):
    ctx = dict(context, is_indirect=True)
    return _do_damage(effect, caster, target, ctx)

@register_action(5, "HP_LOSS_EARTH")
def action_hp_loss_earth(effect, caster, target, context):
    return _do_damage(effect, caster, target, context, force_element="earth")

@register_action(6, "HP_LOSS_FIRE")
def action_hp_loss_fire(effect, caster, target, context):
    return _do_damage(effect, caster, target, context, force_element="fire")

@register_action(7, "HP_LOSS_WATER")
def action_hp_loss_water(effect, caster, target, context):
    return _do_damage(effect, caster, target, context, force_element="water")

@register_action(8, "HP_LOSS_AIR")
def action_hp_loss_air(effect, caster, target, context):
    return _do_damage(effect, caster, target, context, force_element="air")

@register_action(9, "HP_LOSS_STASIS")
def action_hp_loss_stasis(effect, caster, target, context):
    return _do_damage(effect, caster, target, context, force_element="stasis")

@register_action(330, "HP_LOSS_LEVEL_BASED")
def action_hp_loss_level_based(effect, caster, target, context):
    """Level-scaled damage. 
    floatParams[0] = base damage (often 0 for level-scaled spells)
    floatParams[1] = per-level scaling factor
    If base=0, compute from spell level: base = level * scaling
    In Wakfu, action 330 scales damage with caster level.
    Formula: base_damage = floatParams[0] + (caster_level * floatParams[1])
    If both are 0, use a minimum of 1 * caster_level / 100 as fallback.
    """
    from engine.damage import calculate_damage
    fp_list = effect.get('floatParams', [])
    base_raw = fp_list[0] if len(fp_list) > 0 else 0
    scaling = fp_list[1] if len(fp_list) > 1 else 0
    
    # Get caster level
    caster_stats = caster.stats if hasattr(caster, 'stats') else {}
    caster_level = caster_stats.get('level', 100)
    
    # Compute effective base damage
    if base_raw == 0 and scaling != 0:
        # Pure level scaling: damage = caster_level * scaling_factor
        base = caster_level * abs(scaling)
    elif base_raw == 0 and scaling == 0:
        # Both zero: this effect relies on external context (state level, etc.)
        # Check if we have a state level from context
        from_state = context.get('from_state')
        if from_state and hasattr(target if target else caster, 'states'):
            t = target if target else caster
            state_lvl = t.states.get_level(f"state_{from_state}")
            if state_lvl > 0:
                base = state_lvl
            else:
                base = 0
        else:
            base = 0
    else:
        # Normal: base + level scaling
        base = base_raw + (caster_level * scaling) if scaling else base_raw
    
    element = _resolve_element(effect)
    is_melee = context.get('is_melee', True)
    is_rear = context.get('is_rear', False)
    is_crit = context.get('is_critical', False)
    is_berserk = context.get('is_berserk', False)
    
    target_res = _get_target_res(target, element)
    target_crit_res = _get_target_res(target, 'critical') if target else 0
    target_rear_res = _get_target_res(target, 'rear') if target else 0
    
    result = calculate_damage(
        base_damage=base,
        stats=caster_stats,
        element=element,
        target_elemental_res=target_res,
        target_critical_res=target_crit_res,
        target_rear_res=target_rear_res,
        is_melee=is_melee,
        is_rear=is_rear,
        is_critical=is_crit,
        is_berserk=is_berserk,
    )
    
    # Apply damage to target
    actual = result
    if isinstance(result, dict):
        actual = result.get('final_damage', result.get('damage', 0))
    
    applied = {}
    if target and hasattr(target, 'take_damage') and actual > 0:
        applied = target.take_damage(actual)
    
    return {
        'action': 'HP_LOSS_LEVEL_BASED',
        'base_raw': base_raw,
        'scaling': scaling,
        'caster_level': caster_level,
        'effective_base': base,
        'element': element,
        'damage': actual,
        'actual_damage': applied.get('hp_lost', actual) if isinstance(applied, dict) else actual,
        **({k: v for k, v in applied.items()} if isinstance(applied, dict) else {})
    }

@register_action(3, "HEAL")
def action_heal(effect, caster, target, context):
    from engine.damage import calculate_heal
    base = fp(effect, 0)
    t = target if target else caster
    caster_stats = caster.stats if hasattr(caster, 'stats') else {}
    result = calculate_heal(base_heal=base, stats=caster_stats)
    actual = t.heal(result.get('final_heal', base))
    return {'action': 'HEAL', 'base': base, 'healed': actual}

# ============================================================
# HP STEAL
# ============================================================
def _do_steal(effect, caster, target, context, force_element=None):
    result = _do_damage(effect, caster, target, context, force_element=force_element)
    stolen = result.get('actual_damage', 0)
    healed = caster.heal(stolen) if stolen > 0 else 0
    result['action'] = 'HP_STEAL'
    result['healed'] = healed
    return result

@register_action(39, "HP_STEAL")
def action_hp_steal(effect, caster, target, context):
    return _do_steal(effect, caster, target, context)

@register_action(40, "HP_STEAL_FIRE")
def action_hp_steal_fire(effect, caster, target, context):
    return _do_steal(effect, caster, target, context, force_element="fire")

@register_action(47, "HP_STEAL_WATER")
def action_hp_steal_water(effect, caster, target, context):
    return _do_steal(effect, caster, target, context, force_element="water")

@register_action(48, "HP_STEAL_EARTH")
def action_hp_steal_earth(effect, caster, target, context):
    return _do_steal(effect, caster, target, context, force_element="earth")

@register_action(49, "HP_STEAL_AIR")
def action_hp_steal_air(effect, caster, target, context):
    return _do_steal(effect, caster, target, context, force_element="air")

# ============================================================
# RESOURCE ACTIONS
# ============================================================
@register_action(41, "ADD_AP")
def action_add_ap(effect, caster, target, context):
    amount = int(fp(effect, 0))
    t = target if target else caster
    t.gain_ap(amount)
    return {'action': 'ADD_AP', 'amount': amount}

@register_action(42, "ADD_MP")
def action_add_mp(effect, caster, target, context):
    amount = int(fp(effect, 0))
    t = target if target else caster
    t.gain_mp(amount)
    return {'action': 'ADD_MP', 'amount': amount}

@register_action(43, "ADD_WP")
def action_add_wp(effect, caster, target, context):
    amount = int(fp(effect, 0))
    t = target if target else caster
    t.gain_wp(amount)
    return {'action': 'ADD_WP', 'amount': amount}

@register_action(44, "REMOVE_AP")
def action_remove_ap(effect, caster, target, context):
    amount = int(fp(effect, 0))
    if target: target.spend_ap(amount)
    return {'action': 'REMOVE_AP', 'amount': amount}

@register_action(45, "REMOVE_MP")
def action_remove_mp(effect, caster, target, context):
    amount = int(fp(effect, 0))
    if target: target.spend_mp(amount)
    return {'action': 'REMOVE_MP', 'amount': amount}

@register_action(46, "REMOVE_WP")
def action_remove_wp(effect, caster, target, context):
    amount = int(fp(effect, 0))
    if target: target.spend_wp(amount)
    return {'action': 'REMOVE_WP', 'amount': amount}

# ============================================================
# STATE ACTIONS
# ============================================================
def _apply_state(effect, caster, target, context):
    """Apply a state to target, resolving state effectIds from all_states.json."""
    fp_list = effect.get('floatParams', [])
    state_id = int(fp_list[0]) if len(fp_list) > 0 else 0
    
    # Level: fp[1] if present and > 0, otherwise fp[2], otherwise 1
    level = 0
    for idx in [1, 2]:
        if len(fp_list) > idx and fp_list[idx] != 0:
            level = int(fp_list[idx])
            break
    if level <= 0:
        level = 1
    
    # Duration: fp[5] if present and > 0
    duration_from_effect = 0
    if len(fp_list) > 5 and fp_list[5] != 0:
        duration_from_effect = int(fp_list[5])
    
    t = target if target else caster

    # Get state metadata from all_states.json
    state_data = get_state(state_id)
    state_name = f"state_{state_id}"
    state_desc = ""
    state_effect_ids = []
    state_type = 0
    duration = duration_from_effect

    if state_data:
        state_desc = state_data.get('description', '')
        state_effect_ids = state_data.get('effectIds', [])
        state_type = state_data.get('stateType', 0)
        dur_params = state_data.get('durationParams', [])
        
        # Duration fallback chain:
        # 1. From effect floatParams (if > 0)
        # 2. From state durationParams[0] (if > 0)
        # 3. Default to 999 (infinite/permanent)
        if duration <= 0:
            if dur_params and len(dur_params) >= 1 and dur_params[0] > 0:
                duration = dur_params[0]
            elif dur_params and len(dur_params) >= 1 and dur_params[0] == -1:
                duration = 999  # infinite state
            else:
                duration = 999

    if duration <= 0:
        duration = 1

    # Apply state to target
    if hasattr(t, 'states'):
        t.states.add_state(
            name=state_name,
            level=level,
            duration=duration,
            source=f"effect_{effect.get('id', 0)}"
        )

    # Resolve state effects (passive bonuses)
    state_effects_results = []
    if state_effect_ids and context.get('resolve_state_effects', True):
        effects_idx = get_effects_index()
        resolved_key = f"_resolved_state_{state_id}"
        if not context.get(resolved_key):
            sub_context = dict(context)
            sub_context[resolved_key] = True
            sub_context['from_state'] = state_id
            sub_context['resolve_state_effects'] = True

            for se_id in state_effect_ids:
                se = effects_idx.get(se_id)
                if se:
                    aid = se.get('actionId', -1)
                    handler_info = ACTION_HANDLERS.get(aid)
                    if handler_info:
                        try:
                            result = handler_info['handler'](se, caster, t, sub_context)
                            result['effect_id'] = se_id
                            result['action_id'] = aid
                            result['action_name'] = handler_info['name']
                            result['from_state'] = state_id
                            state_effects_results.append(result)
                        except Exception as e:
                            logger.debug(f"  State {state_id} effect {se_id}: {e}")
                            state_effects_results.append({
                                'action': 'STATE_EFFECT_ERROR',
                                'effect_id': se_id, 'error': str(e),
                                'from_state': state_id
                            })
                    else:
                        state_effects_results.append({
                            'action': 'UNHANDLED', 'action_id': aid,
                            'effect_id': se_id, 'from_state': state_id,
                            'fp': se.get('floatParams', [])
                        })

    return {
        'action': 'APPLY_STATE', 'state_id': state_id,
        'state_name': state_name, 'state_desc': state_desc,
        'state_type': state_type, 'level': level, 'duration': duration,
        'state_effect_count': len(state_effect_ids),
        'state_effects': state_effects_results
    }

@register_action(20, "SET_STATE")
def action_set_state(effect, caster, target, context):
    return _apply_state(effect, caster, target, context)

@register_action(304, "APPLY_STATE")
def action_apply_state(effect, caster, target, context):
    return _apply_state(effect, caster, target, context)

@register_action(306, "APPLY_STATE_LEVEL")
def action_apply_state_level(effect, caster, target, context):
    return _apply_state(effect, caster, target, context)

@register_action(21, "REMOVE_STATE")
def action_remove_state(effect, caster, target, context):
    state_id = int(fp(effect, 0))
    t = target if target else caster
    if hasattr(t, 'states'):
        t.states.remove_state(f"state_{state_id}")
    return {'action': 'REMOVE_STATE', 'state_id': state_id}

@register_action(305, "REMOVE_STATE_LEVEL")
def action_remove_state_level(effect, caster, target, context):
    return action_remove_state(effect, caster, target, context)

@register_action(307, "MODIFY_STATE_LEVEL")
def action_modify_state_level(effect, caster, target, context):
    state_id = int(fp(effect, 0))
    delta = int(fp(effect, 2, 0))
    return {'action': 'MODIFY_STATE_LEVEL', 'state_id': state_id, 'delta': delta}

# ============================================================
# MASTERY / STAT MODIFIERS
# ============================================================
def _stat_mod(action_name, effect, caster, target, context):
    amount = fp(effect, 0)
    duration = int(fp(effect, 4, 0))
    t = target if target else caster
    return {'action': action_name, 'amount': amount, 'duration': duration}

@register_action(72, "ADD_MASTERY_ALL")
def action_add_mastery_all(e, c, t, ctx): return _stat_mod('ADD_MASTERY_ALL', e, c, t, ctx)

@register_action(73, "REMOVE_MASTERY")
def action_remove_mastery(e, c, t, ctx): return _stat_mod('REMOVE_MASTERY', e, c, t, ctx)

@register_action(80, "ADD_RESIST")
def action_add_resist(e, c, t, ctx): return _stat_mod('ADD_RESIST', e, c, t, ctx)

@register_action(82, "ADD_MASTERY_FIRE")
def action_add_mastery_fire(e, c, t, ctx): return _stat_mod('ADD_MASTERY_FIRE', e, c, t, ctx)

@register_action(83, "ADD_MASTERY_EARTH")
def action_add_mastery_earth(e, c, t, ctx): return _stat_mod('ADD_MASTERY_EARTH', e, c, t, ctx)

@register_action(84, "ADD_MASTERY_WATER")
def action_add_mastery_water(e, c, t, ctx): return _stat_mod('ADD_MASTERY_WATER', e, c, t, ctx)

@register_action(85, "ADD_MASTERY_AIR")
def action_add_mastery_air(e, c, t, ctx): return _stat_mod('ADD_MASTERY_AIR', e, c, t, ctx)

@register_action(90, "ADD_RESIST_FIRE")
def action_add_resist_fire(e, c, t, ctx): return _stat_mod('ADD_RESIST_FIRE', e, c, t, ctx)

@register_action(91, "ADD_RESIST_EARTH")
def action_add_resist_earth(e, c, t, ctx): return _stat_mod('ADD_RESIST_EARTH', e, c, t, ctx)

@register_action(92, "ADD_RESIST_WATER")
def action_add_resist_water(e, c, t, ctx): return _stat_mod('ADD_RESIST_WATER', e, c, t, ctx)

@register_action(93, "ADD_RESIST_AIR")
def action_add_resist_air(e, c, t, ctx): return _stat_mod('ADD_RESIST_AIR', e, c, t, ctx)

@register_action(120, "ADD_DAMAGE_INFLICTED")
def action_add_di(e, c, t, ctx): return _stat_mod('ADD_DI', e, c, t, ctx)

@register_action(121, "ADD_HEAL_PERFORMED")
def action_add_heal_perf(e, c, t, ctx): return _stat_mod('ADD_HEAL_PERFORMED', e, c, t, ctx)

@register_action(130, "ADD_DODGE")
def action_add_dodge(e, c, t, ctx): return _stat_mod('ADD_DODGE', e, c, t, ctx)

@register_action(131, "ADD_LOCK")
def action_add_lock(e, c, t, ctx): return _stat_mod('ADD_LOCK', e, c, t, ctx)

@register_action(132, "REMOVE_DODGE")
def action_remove_dodge(e, c, t, ctx): return _stat_mod('REMOVE_DODGE', e, c, t, ctx)

@register_action(133, "REMOVE_LOCK")
def action_remove_lock(e, c, t, ctx): return _stat_mod('REMOVE_LOCK', e, c, t, ctx)

@register_action(149, "ADD_CRITICAL_MASTERY")
def action_add_crit_mastery(e, c, t, ctx): return _stat_mod('ADD_CRIT_MASTERY', e, c, t, ctx)

@register_action(150, "ADD_CRITICAL")
def action_add_crit(e, c, t, ctx): return _stat_mod('ADD_CRITICAL', e, c, t, ctx)

@register_action(160, "ADD_INIT")
def action_add_init(e, c, t, ctx): return _stat_mod('ADD_INIT', e, c, t, ctx)

@register_action(161, "ADD_WILLPOWER")
def action_add_willpower(e, c, t, ctx): return _stat_mod('ADD_WILLPOWER', e, c, t, ctx)

@register_action(173, "ADD_BLOCK")
def action_add_block(e, c, t, ctx): return _stat_mod('ADD_BLOCK', e, c, t, ctx)

@register_action(175, "ADD_MASTERY_MELEE")
def action_add_mastery_melee(e, c, t, ctx): return _stat_mod('ADD_MASTERY_MELEE', e, c, t, ctx)

@register_action(176, "ADD_MASTERY_DISTANCE")
def action_add_mastery_dist(e, c, t, ctx): return _stat_mod('ADD_MASTERY_DISTANCE', e, c, t, ctx)

@register_action(177, "ADD_MASTERY_REAR")
def action_add_mastery_rear(e, c, t, ctx): return _stat_mod('ADD_MASTERY_REAR', e, c, t, ctx)

@register_action(178, "ADD_MASTERY_HEAL")
def action_add_mastery_heal(e, c, t, ctx): return _stat_mod('ADD_MASTERY_HEAL', e, c, t, ctx)

@register_action(179, "ADD_MASTERY_BERSERK")
def action_add_mastery_berserk(e, c, t, ctx): return _stat_mod('ADD_MASTERY_BERSERK', e, c, t, ctx)

@register_action(1052, "ADD_MASTERY_CRITICAL")
def action_add_mastery_crit(e, c, t, ctx): return _stat_mod('ADD_MASTERY_CRITICAL', e, c, t, ctx)

@register_action(1053, "ADD_RESIST_CRITICAL")
def action_add_resist_crit(e, c, t, ctx): return _stat_mod('ADD_RESIST_CRITICAL', e, c, t, ctx)

@register_action(1068, "MODIFY_CHARACTERISTIC")
def action_modify_char(e, c, t, ctx): return _stat_mod('MODIFY_CHAR', e, c, t, ctx)

# ============================================================
# MOVEMENT ACTIONS
# ============================================================
@register_action(56, "PUSH")
def action_push(effect, caster, target, context):
    return {'action': 'PUSH', 'distance': int(fp(effect, 0, 1))}

@register_action(57, "PULL")
def action_pull(effect, caster, target, context):
    return {'action': 'PULL', 'distance': int(fp(effect, 0, 1))}

@register_action(58, "TELEPORT")
def action_teleport(effect, caster, target, context):
    return {'action': 'TELEPORT'}

@register_action(51, "ADD_RANGE")
def action_add_range(e, c, t, ctx): return _stat_mod('ADD_RANGE', e, c, t, ctx)

@register_action(52, "REMOVE_RANGE")
def action_remove_range(e, c, t, ctx): return _stat_mod('REMOVE_RANGE', e, c, t, ctx)

# ============================================================
# ARMOR
# ============================================================
@register_action(31, "ADD_ARMOR")
def action_add_armor(effect, caster, target, context):
    from engine.damage import calculate_armor
    base = fp(effect, 0)
    t = target if target else caster
    result = calculate_armor(base_armor=base)
    t.gain_armor(result.get('final_armor', base))
    return {'action': 'ADD_ARMOR', 'base': base, 'final': result.get('final_armor', base)}

# ============================================================
# TRIGGER / CONDITIONAL / SPECIAL
# ============================================================
@register_action(2, "TRIGGER_EFFECT")
def action_trigger(effect, caster, target, context):
    return {'action': 'TRIGGER', 'condition': effect.get('condition', ''), 'fp': effect.get('floatParams', [])}

@register_action(300, "EFFECT_ON_TARGET")
def action_effect_on_target(effect, caster, target, context):
    return {'action': 'EFFECT_ON_TARGET', 'fp': effect.get('floatParams', [])}

@register_action(301, "EFFECT_ON_CASTER")
def action_effect_on_caster(effect, caster, target, context):
    return {'action': 'EFFECT_ON_CASTER', 'fp': effect.get('floatParams', [])}

@register_action(400, "CUSTOM_ACTION")
def action_custom(effect, caster, target, context):
    return {'action': 'CUSTOM', 'effect_id': effect.get('id'), 'fp': effect.get('floatParams', [])}

@register_action(315, "SUMMON")
def action_summon(effect, caster, target, context):
    return {'action': 'SUMMON', 'fp': effect.get('floatParams', [])}

@register_action(321, "SET_HP_PERCENT")
def action_set_hp_pct(effect, caster, target, context):
    pct = fp(effect, 0)
    return {'action': 'SET_HP_PCT', 'percent': pct}

@register_action(349, "DYNAMIC_EFFECT")
def action_dynamic(effect, caster, target, context):
    return {'action': 'DYNAMIC', 'fp': effect.get('floatParams', [])}

@register_action(843, "SRAM_DOUBLE")
def action_sram_double(effect, caster, target, context):
    return {'action': 'SRAM_DOUBLE'}

@register_action(844, "SRAM_TRAP")
def action_sram_trap(effect, caster, target, context):
    return {'action': 'SRAM_TRAP', 'fp': effect.get('floatParams', [])}

@register_action(875, "SPECIAL_MECHANIC")
def action_special(effect, caster, target, context):
    return {'action': 'SPECIAL', 'effect_id': effect.get('id'), 'fp': effect.get('floatParams', [])}

@register_action(913, "SUBLIMATION")
def action_sublimation(effect, caster, target, context):
    return {'action': 'SUBLIMATION', 'fp': effect.get('floatParams', [])}

@register_action(1083, "AREA_EFFECT")
def action_area(effect, caster, target, context):
    return {'action': 'AREA_EFFECT', 'shape': effect.get('areaShape'), 'size': effect.get('areaSize')}

# ============================================================
# SPELL EXECUTOR
# ============================================================

@register_action(55, "SWAP_POSITION")
def action_swap_position(effect, caster, target, context):
    """Swap positions between caster and target."""
    distance = fp(effect, 0)
    return {'action': 'SWAP_POSITION', 'distance': distance}

@register_action(303, "CONDITIONAL_EFFECT")
def action_conditional_effect(effect, caster, target, context):
    """Conditional effect - triggers based on conditions."""
    condition_id = int(fp(effect, 0))
    return {'action': 'CONDITIONAL_EFFECT', 'condition_id': condition_id,
            'fp': effect.get('floatParams', [])}

@register_action(865, "TRAP_ACTIVATE")
def action_trap_activate(effect, caster, target, context):
    """Activate a Sram trap."""
    trap_power = fp(effect, 0)
    return {'action': 'TRAP_ACTIVATE', 'power': trap_power}

@register_action(447, "ADD_AP_GAIN")
def action_add_ap_gain(effect, caster, target, context):
    """Modify AP gain per turn."""
    amount = fp(effect, 0)
    t = target if target else caster
    return {'action': 'ADD_AP_GAIN', 'amount': amount}

@register_action(26, "ADD_HP")
def action_add_hp(effect, caster, target, context):
    """Add max HP."""
    amount = fp(effect, 0)
    t = target if target else caster
    if hasattr(t, 'stats'):
        t.stats['hp'] = t.stats.get('hp', 0) + amount
    return {'action': 'ADD_HP', 'amount': amount}

@register_action(180, "ADD_CONTROL")
def action_add_control(effect, caster, target, context):
    """Add control (summon slots)."""
    amount = fp(effect, 0)
    return {'action': 'ADD_CONTROL', 'amount': amount}

@register_action(302, "EFFECT_ON_STATE")
def action_effect_on_state(effect, caster, target, context):
    """Apply effect when a specific state is active."""
    state_id = int(fp(effect, 0))
    return {'action': 'EFFECT_ON_STATE', 'state_id': state_id,
            'fp': effect.get('floatParams', [])}

@register_action(421, "STEAL_STAT")
def action_steal_stat(effect, caster, target, context):
    """Steal a stat from target."""
    amount = fp(effect, 0)
    stat_type = int(fp(effect, 1)) if len(effect.get('floatParams', [])) > 1 else 0
    return {'action': 'STEAL_STAT', 'amount': amount, 'stat_type': stat_type}

@register_action(430, "DAMAGE_REFLECT")
def action_damage_reflect(effect, caster, target, context):
    """Reflect damage back to attacker."""
    percent = fp(effect, 0)
    return {'action': 'DAMAGE_REFLECT', 'percent': percent}



@register_action(55, "SWAP_POSITION")
def action_swap_position(effect, caster, target, context):
    """Swap positions between caster and target."""
    distance = fp(effect, 0)
    return {'action': 'SWAP_POSITION', 'distance': distance}

@register_action(303, "CONDITIONAL_EFFECT")
def action_conditional_effect(effect, caster, target, context):
    """Conditional effect - triggers based on conditions."""
    condition_id = int(fp(effect, 0))
    return {'action': 'CONDITIONAL_EFFECT', 'condition_id': condition_id,
            'fp': effect.get('floatParams', [])}

@register_action(865, "TRAP_ACTIVATE")
def action_trap_activate(effect, caster, target, context):
    """Activate a Sram trap."""
    trap_power = fp(effect, 0)
    return {'action': 'TRAP_ACTIVATE', 'power': trap_power}

@register_action(447, "ADD_AP_GAIN")
def action_add_ap_gain(effect, caster, target, context):
    """Modify AP gain per turn."""
    amount = fp(effect, 0)
    t = target if target else caster
    return {'action': 'ADD_AP_GAIN', 'amount': amount}

@register_action(26, "ADD_HP")
def action_add_hp(effect, caster, target, context):
    """Add max HP."""
    amount = fp(effect, 0)
    t = target if target else caster
    if hasattr(t, 'stats'):
        t.stats['hp'] = t.stats.get('hp', 0) + amount
    return {'action': 'ADD_HP', 'amount': amount}

@register_action(180, "ADD_CONTROL")
def action_add_control(effect, caster, target, context):
    """Add control (summon slots)."""
    amount = fp(effect, 0)
    return {'action': 'ADD_CONTROL', 'amount': amount}

@register_action(302, "EFFECT_ON_STATE")
def action_effect_on_state(effect, caster, target, context):
    """Apply effect when a specific state is active."""
    state_id = int(fp(effect, 0))
    return {'action': 'EFFECT_ON_STATE', 'state_id': state_id,
            'fp': effect.get('floatParams', [])}

@register_action(421, "STEAL_STAT")
def action_steal_stat(effect, caster, target, context):
    """Steal a stat from target."""
    amount = fp(effect, 0)
    stat_type = int(fp(effect, 1)) if len(effect.get('floatParams', [])) > 1 else 0
    return {'action': 'STEAL_STAT', 'amount': amount, 'stat_type': stat_type}

@register_action(430, "DAMAGE_REFLECT")
def action_damage_reflect(effect, caster, target, context):
    """Reflect damage back to attacker."""
    percent = fp(effect, 0)
    return {'action': 'DAMAGE_REFLECT', 'percent': percent}


class SpellExecutor:
    def __init__(self):
        self.effects_index = None
        self.spells_index = None
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self.effects_index = get_effects_index()
            self.spells_index = get_spells_index()
            self._loaded = True
            logger.info(f"SpellExecutor: {len(self.spells_index):,} spells, "
                        f"{len(self.effects_index):,} effects, "
                        f"{len(ACTION_HANDLERS)} handlers")

    def get_spell(self, spell_id):
        self._ensure_loaded()
        return self.spells_index.get(spell_id)

    def get_effect(self, effect_id):
        self._ensure_loaded()
        return self.effects_index.get(effect_id)

    def get_spell_effects(self, spell_id):
        spell = self.get_spell(spell_id)
        if not spell: return []
        result = []
        for eid in spell.get('effectIds', []):
            eff = self.get_effect(eid)
            if eff:
                result.append(eff)
        return result

    def cast(self, caster, spell_id, target=None, context=None):
        self._ensure_loaded()
        spell = self.get_spell(spell_id)
        if not spell:
            logger.error(f"Spell {spell_id} not found")
            return []

        if context is None:
            context = {}
        context['spell_id'] = spell_id
        context['spell'] = spell

        results = []
        for eff in self.get_spell_effects(spell_id):
            aid = eff.get('actionId', -1)
            handler_info = ACTION_HANDLERS.get(aid)

            if handler_info:
                try:
                    result = handler_info['handler'](eff, caster, target, context)
                    result['effect_id'] = eff.get('id')
                    result['action_id'] = aid
                    result['action_name'] = handler_info['name']
                    results.append(result)
                except Exception as e:
                    logger.error(f"  Effect {eff['id']}: {handler_info['name']} FAILED: {e}")
                    results.append({'action': 'ERROR', 'effect_id': eff.get('id'), 'error': str(e)})
            else:
                results.append({
                    'action': 'UNHANDLED', 'action_id': aid,
                    'effect_id': eff.get('id'), 'fp': eff.get('floatParams', [])
                })
        return results

    def describe_spell(self, spell_id):
        self._ensure_loaded()
        spell = self.get_spell(spell_id)
        if not spell: return f"Spell {spell_id}: NOT FOUND"

        lines = [f"Spell {spell_id}: PA={spell.get('PA_base', 0)}, breed={spell.get('breedId')}, maxLvl={spell.get('maxLevel')}"]
        for eff in self.get_spell_effects(spell_id):
            aid = eff.get('actionId', -1)
            h = ACTION_HANDLERS.get(aid)
            name = h['name'] if h else f"UNKNOWN_{aid}"
            fp_list = eff.get('floatParams', [])
            cond = eff.get('condition', '')
            line = f"  [{eff['id']}] {name}"
            if fp_list: line += f" fp={fp_list[:6]}"
            if eff.get('stateId'): line += f" stateId={eff['stateId']}"
            if cond: line += f" cond='{cond[:50]}'"
            lines.append(line)
        return '\n'.join(lines)


    def resolve_state(self, state_id, caster=None, target=None, context=None):
        """Resolve all effects of a state and return results."""
        self._ensure_loaded()
        state_data = get_state(state_id)
        if not state_data:
            return {'state_id': state_id, 'error': 'State not found', 'effects': []}

        if context is None:
            context = {}
        context[f'_resolved_state_{state_id}'] = True

        results = []
        for eid in state_data.get('effectIds', []):
            eff = self.get_effect(eid)
            if not eff:
                results.append({'effect_id': eid, 'action': 'NOT_FOUND'})
                continue

            aid = eff.get('actionId', -1)
            handler_info = ACTION_HANDLERS.get(aid)
            if handler_info:
                try:
                    result = handler_info['handler'](eff, caster, target, context)
                    result['effect_id'] = eid
                    result['action_id'] = aid
                    result['action_name'] = handler_info['name']
                    results.append(result)
                except Exception as e:
                    results.append({'effect_id': eid, 'action': 'ERROR', 'error': str(e)})
            else:
                results.append({
                    'effect_id': eid, 'action': 'UNHANDLED', 'action_id': aid,
                    'fp': eff.get('floatParams', [])
                })

        return {
            'state_id': state_id,
            'state_type': state_data.get('stateType', 0),
            'description': state_data.get('description', ''),
            'duration_params': state_data.get('durationParams', []),
            'effect_count': len(state_data.get('effectIds', [])),
            'effects': results
        }

    def describe_state(self, state_id):
        """Human-readable description of a state."""
        self._ensure_loaded()
        state_data = get_state(state_id)
        if not state_data:
            return f"State {state_id}: NOT FOUND"

        out = []
        out.append(f"State {state_id} (type={state_data.get('stateType', '?')}, "
                   f"desc='{state_data.get('description', '')}'):")
        out.append(f"  Duration params: {state_data.get('durationParams', [])}")
        out.append(f"  Effect IDs: {state_data.get('effectIds', [])}")

        for eid in state_data.get('effectIds', []):
            eff = self.get_effect(eid)
            if eff:
                aid = eff.get('actionId', -1)
                h = ACTION_HANDLERS.get(aid)
                name = h['name'] if h else f'UNKNOWN_{aid}'
                fp_list = eff.get('floatParams', [])
                out.append(f"    [{eid}] {name} fp={fp_list[:6]}")
            else:
                out.append(f"    [{eid}] NOT FOUND in effects")

        return '\n'.join(out)

executor = SpellExecutor()

# ============================================================
# SELF-TEST
# ============================================================
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=" * 70)
    print("EFFECT BRIDGE v2 SELF-TEST")
    print("=" * 70)

    print(f"\nRegistered handlers: {len(ACTION_HANDLERS)}")

    # Coverage
    effects = _load_json("static_effects.json")
    from collections import Counter
    action_counts = Counter(e['actionId'] for e in effects)
    handled = sum(c for a, c in action_counts.items() if a in ACTION_HANDLERS)
    total = sum(action_counts.values())
    handled_types = len([a for a in action_counts if a in ACTION_HANDLERS])
    total_types = len(action_counts)

    print(f"Coverage: {handled_types}/{total_types} action types = {handled:,}/{total:,} effects ({handled*100/total:.1f}%)")

    unhandled = [(a, c) for a, c in action_counts.most_common() if a not in ACTION_HANDLERS]
    if unhandled:
        print(f"\nTop 5 unhandled:")
        for a, c in unhandled[:5]:
            print(f"  action {a}: {c:,} effects")

    # SRAM spells
    print(f"\n--- SRAM SPELLS ---")
    for sid in get_breed_spell_ids("SRAM"):
        print(executor.describe_spell(sid))
        print()
