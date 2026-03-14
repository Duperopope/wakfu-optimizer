"""
Upgrade effect_bridge.py v2 - more robust insertion.
Strategy: read file, find exact markers, insert code blocks.
"""
import os
import sys

BRIDGE_PATH = r"H:\Code\Ankama Dev\wakfu-optimizer\engine\effect_bridge.py"
BACKUP_PATH = BRIDGE_PATH + ".bak_v2"

with open(BRIDGE_PATH, 'r', encoding='utf-8') as f:
    src = f.read()

with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print(f"Backup: {BACKUP_PATH}")

# ================================================================
# STEP 1: Add get_states_index() and get_state() 
# Insert right after get_breeds() function
# ================================================================

STATES_LOADER = '''
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

'''

# Find the end of get_breeds()
marker_breeds = 'return _load_json("breeds.json")'
pos = src.find(marker_breeds)
if pos == -1:
    print("ERROR: Could not find get_breeds() marker")
    sys.exit(1)

# Find end of that line
eol = src.index('\n', pos)
insert_pos = eol + 1
src = src[:insert_pos] + STATES_LOADER + src[insert_pos:]
print(f"Inserted get_states_index() after get_breeds()")

# ================================================================
# STEP 2: Replace _apply_state function
# ================================================================

NEW_APPLY_STATE = '''def _apply_state(effect, caster, target, context):
    """Apply a state to target, resolving state effectIds from all_states.json."""
    state_id = int(fp(effect, 0))
    fp_list = effect.get('floatParams', [])
    level = int(fp_list[1]) if len(fp_list) > 1 else 1
    duration = int(fp_list[5]) if len(fp_list) > 5 else 999
    t = target if target else caster

    # Get state metadata from all_states.json
    state_data = get_state(state_id)
    state_name = f"state_{state_id}"
    state_desc = ""
    state_effect_ids = []
    state_type = 0

    if state_data:
        state_desc = state_data.get('description', '')
        state_effect_ids = state_data.get('effectIds', [])
        state_type = state_data.get('stateType', 0)
        dur_params = state_data.get('durationParams', [])
        if dur_params and len(dur_params) >= 1 and dur_params[0] > 0 and duration == 999:
            duration = dur_params[0]

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
'''

# Find the old _apply_state
marker_start = 'def _apply_state(effect, caster, target, context):'
marker_end = '@register_action(20, "SET_STATE")'

start = src.find(marker_start)
end = src.find(marker_end)

if start == -1 or end == -1:
    print(f"ERROR: Could not find _apply_state boundaries (start={start}, end={end})")
    sys.exit(1)

src = src[:start] + NEW_APPLY_STATE + '\n' + src[end:]
print(f"Replaced _apply_state()")

# ================================================================
# STEP 3: Add resolve_state() and describe_state() to SpellExecutor
# Insert INSIDE the class, right before the if __name__ block
# or right after describe_spell method
# ================================================================

EXECUTOR_METHODS = '''
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

        return '\\n'.join(out)

'''

# Find the end of describe_spell method - look for the 'if __name__' block
# or the line that starts at column 0 after SpellExecutor
# Strategy: find 'def describe_spell' then find the next unindented line

desc_marker = 'def describe_spell(self'
desc_pos = src.find(desc_marker)

if desc_pos == -1:
    print("ERROR: Could not find describe_spell")
    sys.exit(1)

# From describe_spell, find the next line that starts at column 0 (not blank)
search_from = desc_pos + 100
pos = search_from
while pos < len(src):
    eol = src.find('\n', pos)
    if eol == -1:
        break
    next_line = src[eol+1:src.find('\n', eol+1) if src.find('\n', eol+1) != -1 else len(src)]
    if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t'):
        # This is the first unindented non-blank line after describe_spell
        insert_at = eol + 1
        src = src[:insert_at] + EXECUTOR_METHODS + src[insert_at:]
        print(f"Inserted resolve_state + describe_state inside SpellExecutor")
        break
    pos = eol + 1

# ================================================================
# SAVE
# ================================================================
with open(BRIDGE_PATH, 'w', encoding='utf-8') as f:
    f.write(src)

orig_len = os.path.getsize(BACKUP_PATH)
new_len = len(src)
print(f"\nSaved: {BRIDGE_PATH}")
print(f"  Before: {orig_len:,} chars")
print(f"  After:  {new_len:,} chars")
print(f"  Added:  {new_len - orig_len:,} chars")

# ================================================================
# TEST
# ================================================================
print("\n" + "=" * 70)
print("TESTING updated bridge")
print("=" * 70)

sys.path.insert(0, r"H:\Code\Ankama Dev\wakfu-optimizer")

# Clear cached modules
for mod_name in list(sys.modules.keys()):
    if 'effect_bridge' in mod_name or 'engine' in mod_name:
        del sys.modules[mod_name]

try:
    from engine.effect_bridge import (
        SpellExecutor, get_states_index, get_state,
        ACTION_HANDLERS, get_effects_index
    )

    # 1. States loaded
    states_idx = get_states_index()
    print(f"  States: {len(states_idx):,}")

    # 2. get_state
    s3114 = get_state(3114)
    print(f"  State 3114: type={s3114['stateType']}, effects={s3114['effectIds']}")

    # 3. SpellExecutor methods exist
    executor = SpellExecutor()
    assert hasattr(executor, 'resolve_state'), "resolve_state missing!"
    assert hasattr(executor, 'describe_state'), "describe_state missing!"
    print(f"  SpellExecutor: resolve_state OK, describe_state OK")

    # 4. describe_state
    for sid in [3114, 3129, 3136]:
        desc = executor.describe_state(sid)
        print(f"\n  {desc}")

    # 5. resolve_state
    print(f"\n  Resolving state 3114:")
    result = executor.resolve_state(3114)
    print(f"    Effects: {result['effect_count']}")
    for eff in result['effects']:
        name = eff.get('action_name', eff.get('action', '?'))
        print(f"    -> {name} (id={eff.get('effect_id')})")

    # 6. APPLY_STATE with state resolution (mock fighter)
    print(f"\n  Testing APPLY_STATE handler:")
    from engine.fighter import StateManager

    class MockFighter:
        def __init__(self):
            self.stats = {'hp': 10000}
            self.states = StateManager()

    caster = MockFighter()
    target = MockFighter()

    effects_idx = get_effects_index()
    found_test = False
    for eid, eff in effects_idx.items():
        if eff.get('actionId') == 304:
            fp0 = eff.get('floatParams', [])
            if fp0 and fp0[0] == 3114.0:
                handler = ACTION_HANDLERS[304]['handler']
                result = handler(eff, caster, target, {})
                print(f"    Applied state {result['state_id']}, "
                      f"sub-effects: {len(result.get('state_effects', []))}")
                for se in result.get('state_effects', []):
                    name = se.get('action_name', se.get('action', '?'))
                    print(f"      -> {name} (id={se.get('effect_id')})")
                print(f"    Target has state_3114: {target.states.has_state('state_3114')}")
                found_test = True
                break

    if not found_test:
        print(f"    No effect applying state 3114 found, testing with manual effect")
        fake_effect = {'id': 999999, 'actionId': 304, 'floatParams': [3114.0, 1.0, 0, 0, 0, 2.0]}
        handler = ACTION_HANDLERS[304]['handler']
        result = handler(fake_effect, caster, target, {})
        print(f"    Applied state {result['state_id']}, sub-effects: {len(result.get('state_effects', []))}")
        print(f"    Target has state_3114: {target.states.has_state('state_3114')}")

    # 7. Coverage
    total_se = sum(len(s.get('effectIds', [])) for s in states_idx.values())
    handled = sum(1 for s in states_idx.values()
                  for eid in s.get('effectIds', [])
                  if effects_idx.get(eid, {}).get('actionId') in ACTION_HANDLERS)
    print(f"\n  State effects coverage: {handled}/{total_se} ({handled/total_se*100:.1f}%)")

    print(f"\n  ALL TESTS PASSED")

except Exception as e:
    print(f"\n  ERROR: {e}")
    import traceback
    traceback.print_exc()
    print(f"\n  Restoring backup...")
    with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
        orig = f.read()
    with open(BRIDGE_PATH, 'w', encoding='utf-8') as f:
        f.write(orig)
    print(f"  Restored.")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
