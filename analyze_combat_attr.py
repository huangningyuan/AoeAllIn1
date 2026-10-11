import os, re, json
from copy import deepcopy
from genieutils.datfile import DatFile

COMBAT_ATTR = 63
CLASS_OFFSET = 900

BIT_NAMES = {
    1: 'bit1 Harass', 2: 'bit2', 4: 'bit4 Bessian', 8: 'bit8',
    16: 'bit16', 32: 'bit32 Aura', 64: 'bit64 Aura', 128: 'bit128 OotS/Curare',
}

BUILDING_NAMES = {
    12: 'Barracks', 45: 'Dock', 49: 'Siege', 82: 'Castle',
    87: 'Range', 101: 'Stable', 103: 'Blacksmith', 104: 'Monastery',
    109: 'TownCenter', 209: 'University',
}

XS_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\xs\Effects.xs'
CONST_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\xs\Constants.xs'

STR_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\en\strings\key-value\key-value-strings-utf8.txt'
STR_MODDED = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\en\strings\key-value\key-value-modded-strings-utf8.txt'


def _load_strings():
    strings = {}
    for path in [STR_PATH, STR_MODDED]:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.match(r'(\d+)\s+"(.+)"', line.strip())
                if m:
                    strings[int(m.group(1))] = m.group(2)
    return strings


def _parse_xs():
    with open(CONST_PATH, 'r', encoding='utf-8') as f:
        const_content = f.read()
    all_consts = {}
    for m in re.finditer(r'(\w+ID|c\w+Class|c\w+ID)\s*=\s*(-?\d+)', const_content):
        all_consts[m.group(1)] = int(m.group(2))

    with open(XS_PATH, 'r', encoding='utf-8') as f:
        xs_lines = f.readlines()
    for line in xs_lines:
        m = re.search(r'(\w+ID|c\w+Class)\s*=\s*(-?\d+)', line)
        if m:
            all_consts.setdefault(m.group(1), int(m.group(2)))

    func_bodies = {}
    func_params = {}
    current_func = None
    func_start = 0
    brace_depth = 0
    for i, line in enumerate(xs_lines):
        m = re.match(r'void (\w+)\(([^)]*)\)', line)
        if m:
            current_func = m.group(1)
            func_start = i
            params_str = m.group(2)
            params = []
            if params_str.strip():
                for p in params_str.split(','):
                    p = p.strip()
                    pname = p.split()[-1].split('=')[0].strip()
                    params.append(pname)
            func_params[current_func] = params
            brace_depth = line.count('{') - line.count('}')
            continue
        if current_func:
            brace_depth += line.count('{') - line.count('}')
            if brace_depth <= 0:
                func_bodies[current_func] = ''.join(xs_lines[func_start:i + 1])
                current_func = None

    return all_consts, func_bodies, func_params


def _resolve_expr(expr, local_consts, all_consts):
    expr = expr.strip()
    m = re.match(r'^(-?\d+)$', expr)
    if m:
        return int(expr)
    if expr in local_consts:
        return _resolve_expr(str(local_consts[expr]), local_consts, all_consts)
    if expr in all_consts:
        return all_consts[expr]
    return expr


def _expand_target(target_val, units):
    if isinstance(target_val, str):
        return ('unknown', target_val, [])
    if target_val >= CLASS_OFFSET:
        class_id = target_val - CLASS_OFFSET
        return ('class', class_id, [uid for uid, u in enumerate(units) if u and u.class_ == class_id])
    elif target_val < 0:
        return ('unknown', target_val, [])
    else:
        return ('unit', target_val, [target_val])


def _expand_func(func_name, arg_values, func_bodies, func_params, all_consts, depth=0):
    if depth > 5 or func_name not in func_bodies:
        return []
    params = func_params.get(func_name, [])
    local_consts = {}
    for pi, pname in enumerate(params):
        if pi < len(arg_values):
            local_consts[pname] = _resolve_expr(arg_values[pi], local_consts, all_consts)

    body = func_bodies[func_name]
    results = []

    for m in re.finditer(r'xsEffectAmount\(c(Add|Set)Attribute\s*,\s*(\w+)\s*,\s*cCombatAbility\s*,\s*(-?\d+)', body):
        op_type = 'ADD' if m.group(1) == 'Add' else 'SET'
        target_expr = m.group(2)
        amount = int(m.group(3))
        resolved = _resolve_expr(target_expr, local_consts, all_consts)
        results.append({'op': op_type, 'target': resolved, 'amount': amount})

    for m in re.finditer(r'(\w+)\(([^)]*),\s*playerId\)', body):
        fname = m.group(1)
        args_str = m.group(2)
        if fname in ('xsResetTaskAmount', 'xsEffectAmount', 'xsTaskAmount', 'xsTask',
                     'xsModifyObjectTasks', 'HandicapSetup', 'HunnicHorseGraphic', 'xsTaskAura'):
            continue
        if fname in func_bodies:
            arg_parts = [a.strip() for a in args_str.split(',')]
            expanded_args = [str(_resolve_expr(a, local_consts, all_consts)) for a in arg_parts]
            results.extend(_expand_func(fname, expanded_args, func_bodies, func_params, all_consts, depth + 1))

    return results


AGE_TECH_MAP = {
    104: 1, 101: 2, 102: 3, 103: 4,
    1209: 2, 113: 3, 115: 4,
}


def _make_age_resolver(techs):
    cache = {}

    def resolve(tid):
        if tid in cache:
            return cache[tid]
        if tid in AGE_TECH_MAP:
            cache[tid] = AGE_TECH_MAP[tid]
            return cache[tid]
        if tid < 0 or tid >= len(techs):
            cache[tid] = 1
            return 1
        t = techs[tid]
        reqs = [r for r in t.required_techs if r >= 0]
        if not reqs:
            cache[tid] = 1
            return 1
        best = 0
        for r in reqs:
            a = resolve(r)
            if a > best:
                best = a
        cache[tid] = best
        return best

    return resolve, cache


def _tech_dev(t):
    rl = t.research_locations[0] if t.research_locations else None
    if rl is None:
        return 'auto'
    has_cost = any(rc.amount > 0 for rc in t.resource_costs)
    return 'manual' if (has_cost and rl.location_id > 0) else 'auto'


def _tech_info(tid, techs, strings, age_resolve):
    t = techs[tid]
    lid = getattr(t, 'language_dll_name', 0)
    name = strings.get(lid, t.name) if lid else t.name
    return {
        'dev': _tech_dev(t),
        'age_id': age_resolve(tid),
        'req': [r for r in t.required_techs if r >= 0],
        'civ': t.civ,
        'effect_id': t.effect_id,
        'name': name,
    }


def _fmt_bits(amount):
    amount = int(amount)
    bits = [b for b in [1, 2, 4, 8, 16, 32, 64, 128] if (amount & b)]
    return '+'.join(BIT_NAMES.get(b, 'bit' + str(b)) for b in bits) if bits else '(none)'


def scan_attr63_conflicts(data, log=False):
    """
    扫描 dat 中所有 attr=63 冲突，返回结构化修复计划。
    返回值: list[dict], 每个 dict 代表一个 (unit, correction) 需要修正
    """
    units = data.civs[0].units
    techs = data.techs
    effects = data.effects
    strings = _load_strings()
    all_consts, func_bodies, func_params = _parse_xs()
    age_resolve, _age_cache = _make_age_resolver(techs)

    CIV_NAMES = {}
    for ci, c in enumerate(data.civs):
        if c is not None:
            cid = getattr(c, 'ID', ci)
            CIV_NAMES[cid] = getattr(c, 'name', 'Civ' + str(cid))

    unit_ops = {}

    def add_op(uid, op_dict):
        if uid < 0 or uid >= len(units) or units[uid] is None:
            return
        unit_ops.setdefault(uid, []).append(op_dict)

    # 1. Dat direct effect commands (c=63)
    for eid, eff in enumerate(effects):
        cmds = [c for c in eff.effect_commands if c.c == COMBAT_ATTR]
        if not cmds:
            continue
        techs_pt = [tid for tid, t in enumerate(techs) if t.effect_id == eid]
        for tid in techs_pt:
            ti = _tech_info(tid, techs, strings, age_resolve)
            for cmd in cmds:
                op_map = {0: 'SET', 4: 'ADD', 5: 'MUL', 203: 'SET_SEL', 204: 'ADD_SEL'}
                op = op_map.get(cmd.type, 'TYPE' + str(cmd.type))
                amount = int(cmd.d)
                if cmd.b >= 0:
                    class_id = cmd.b
                    unit_ids = [uid for uid, u in enumerate(units) if u and u.class_ == class_id]
                    target_spec = 'class=' + str(class_id)
                else:
                    unit_ids = [cmd.a]
                    target_spec = 'unit=' + str(cmd.a)
                for uid in unit_ids:
                    add_op(uid, {
                        'op': op, 'amount': amount, 'effect_id': eid,
                        'tech_id': tid, 'tech_name': ti['name'],
                        'source': 'dat', 'target_spec': target_spec, 'ti': ti,
                    })

    # 2. XS expanded ops — group by (func_num, eid) to preserve effect_id for dedup
    xs_func_eid_to_techs = {}
    for eid, eff in enumerate(effects):
        for cmd in eff.effect_commands:
            if cmd.type == 1 and cmd.a == 33:
                func_num = int(cmd.d)
                techs_pt = [tid for tid, t in enumerate(techs) if t.effect_id == eid]
                xs_func_eid_to_techs.setdefault((func_num, eid), []).extend(techs_pt)

    for (func_num, eid), tech_ids in xs_func_eid_to_techs.items():
        func_name = 'EffectFunction' + str(func_num)
        if func_name not in func_bodies:
            continue
        xsops = _expand_func(func_name, [], func_bodies, func_params, all_consts)
        for xsop in xsops:
            kind, target_id, unit_ids = _expand_target(xsop['target'], units)
            ti_cache = {}
            for tid in tech_ids:
                ti_cache.setdefault(tid, _tech_info(tid, techs, strings, age_resolve))
            for uid in unit_ids:
                for tid in tech_ids:
                    add_op(uid, {
                        'op': xsop['op'], 'amount': xsop['amount'], 'effect_id': eid,
                        'tech_id': tid, 'tech_name': ti_cache[tid]['name'],
                        'source': 'xs', 'target_spec': kind + '=' + str(target_id), 'ti': ti_cache[tid],
                    })

    # 3. BASE
    base_count = 0
    for uid, u in enumerate(units):
        if u and u.type_50:
            boc = getattr(u.type_50, 'break_off_combat', 0)
            if boc:
                add_op(uid, {
                    'op': 'BASE', 'amount': boc, 'effect_id': -1,
                    'tech_id': -1, 'tech_name': 'NATIVE',
                    'source': 'base', 'target_spec': 'native', 'ti': None,
                })
                base_count += 1

    # 3.5 Dedup ops from shared effects: same unit + same effect_id + same op + same amount = one op
    # (shared effect across multiple tech variants should only count once)
    effect_to_techs_cache = {}
    def get_shared_techs(eid):
        if eid not in effect_to_techs_cache:
            effect_to_techs_cache[eid] = [tid for tid, t in enumerate(techs) if t.effect_id == eid]
        return effect_to_techs_cache[eid]

    for uid in list(unit_ops.keys()):
        ops = unit_ops[uid]
        seen = set()
        deduped = []
        for op in ops:
            key = (op.get('effect_id', -1), op['op'], op['amount'], op.get('target_spec', ''))
            if key not in seen:
                seen.add(key)
                op['shared_tech_ids'] = get_shared_techs(op.get('effect_id', -1))
                deduped.append(op)
        unit_ops[uid] = deduped

    # 4. Merge same-tech ops per unit
    for uid in list(unit_ops.keys()):
        ops = unit_ops[uid]
        base_op = None
        tech_groups = {}
        for op in ops:
            if op['tech_id'] < 0:
                base_op = op
                continue
            tech_groups.setdefault(op['tech_id'], []).append(op)
        new_ops = []
        if base_op is not None:
            new_ops.append(base_op)
        for tid, gops in tech_groups.items():
            set_op = None
            add_amount = 0
            add_op_template = None
            for op in gops:
                if op['op'] in ('SET', 'SET_SEL'):
                    set_op = op
                elif op['op'] in ('ADD', 'ADD_SEL'):
                    add_amount += op['amount']
                    if add_op_template is None:
                        add_op_template = op
            if add_op_template is not None and add_amount != 0:
                merged = dict(add_op_template)
                merged['amount'] = add_amount
                new_ops.append(merged)
            if set_op is not None:
                new_ops.append(set_op)
        unit_ops[uid] = new_ops

    if log:
        print(f'[scan] {len(unit_ops)} units have ops, {base_count} with native boc.')

    # 5. Compute conflict per unit and build fix plan
    fix_plan_entries = []

    for uid, ops in unit_ops.items():
        if uid >= len(units) or units[uid] is None:
            continue
        u = units[uid]
        boc = getattr(u.type_50, 'break_off_combat', 0) if u.type_50 else 0

        set_ops = [op for op in ops if op['op'] in ('SET', 'SET_SEL')]
        add_ops = [op for op in ops if op['op'] in ('ADD', 'ADD_SEL')]

        # Collect all tech-add sources (positive adds only — negative are existing compensations)
        positive_adds = [op for op in add_ops if op['amount'] > 0]
        negative_adds = [op for op in add_ops if op['amount'] < 0]

        # Compute ideal final value (bitwise OR semantics)
        # Start with native
        ideal = boc
        for op in positive_adds:
            ideal |= op['amount']
        for op in set_ops:
            # SET is tricky — if SET comes after ADD, SET overrides.
            # If SET comes before ADD, ADD bits persist.
            # Conservative ideal = native OR all positive add bits OR all set bits
            ideal |= op['amount']

        # Worst-case outcome: last SET covers everything before it,
        # then all ADDs stack arithmetically on top (carries).
        if set_ops:
            last_set_amount = set_ops[-1]['amount']
            worst_case = last_set_amount + sum(op['amount'] for op in positive_adds)
        else:
            worst_case = boc + sum(op['amount'] for op in positive_adds)
        worst_case += sum(op['amount'] for op in negative_adds)

        correction = ideal - worst_case

        if correction == 0:
            continue

        # Per-bit overlap analysis: which bits have 2+ contributors?
        all_amounts_with_sources = []
        if boc:
            all_amounts_with_sources.append(('NATIVE', -1, boc, None))
        for op in positive_adds:
            all_amounts_with_sources.append((op['tech_name'], op['tech_id'], op['amount'], op))
        for op in set_ops:
            all_amounts_with_sources.append((op['tech_name'], op['tech_id'], op['amount'], op))

        conflict_bits = set()
        for bit in [1, 2, 4, 8, 16, 32, 64, 128]:
            contributors = [a for a in all_amounts_with_sources if a[2] & bit]
            if len(contributors) >= 2:
                conflict_bits.add(bit)

        # Only keep tech_sources whose amount touches a conflict bit
        all_tech_sources = []
        if boc and any(boc & b for b in conflict_bits):
            all_tech_sources.append({'kind': 'NATIVE', 'tech_id': -1, 'amount': boc, 'tech_name': 'Native', 'effect_id': -1, 'shared_tech_ids': []})
        for op in positive_adds:
            ti = op['ti']
            if not any(op['amount'] & b for b in conflict_bits):
                continue
            all_tech_sources.append({
                'kind': op['op'], 'tech_id': op['tech_id'], 'amount': op['amount'],
                'dev': ti['dev'], 'age_id': ti['age_id'],
                'tech_name': op['tech_name'],
                'effect_id': op.get('effect_id', -1),
                'shared_tech_ids': op.get('shared_tech_ids', [op['tech_id']]),
            })
        for op in set_ops:
            ti = op['ti']
            all_tech_sources.append({
                'kind': op['op'], 'tech_id': op['tech_id'], 'amount': op['amount'],
                'dev': ti['dev'], 'age_id': ti['age_id'],
                'tech_name': op['tech_name'],
                'effect_id': op.get('effect_id', -1),
                'shared_tech_ids': op.get('shared_tech_ids', [op['tech_id']]),
            })

        # Deduplicate tech_sources by effect_id (shared effect appears once)
        seen_effects = set()
        dedup_sources = []
        for s in all_tech_sources:
            if s['effect_id'] >= 0 and s['effect_id'] in seen_effects:
                continue
            seen_effects.add(s['effect_id'])
            dedup_sources.append(s)
        all_tech_sources = dedup_sources

        tech_sources = [s for s in all_tech_sources if s['tech_id'] >= 0]

        fix_plan = _decide_fix_strategy(tech_sources, correction)

        entry = {
            'unit_id': uid,
            'unit_name': u.name,
            'display_name': strings.get(getattr(u, 'language_dll_name', 0), u.name) if getattr(u, 'language_dll_name', 0) else u.name,
            'class': u.class_,
            'boc': boc,
            'native_bits': _fmt_bits(boc),
            'ideal': ideal,
            'ideal_bits': _fmt_bits(ideal),
            'worst_case': worst_case,
            'worst_bits': _fmt_bits(worst_case),
            'correction': correction,
            'correction_bits': _fmt_bits(correction),
            'sources': all_tech_sources,
            'fix_plan': fix_plan,
        }
        fix_plan_entries.append(entry)

    if log:
        print(f'[scan] {len(fix_plan_entries)} unit-entries need correction.')

    return fix_plan_entries


def _decide_fix_strategy(tech_sources, correction):
    """
    Decide whether to append correction to an existing effect or create a new joint tech.

    Rules:
    - If NO tech_sources (only NATIVE), skip (can't fix — no tech to piggyback on)
    - Sort sources by age: auto=0 earliest, then manual by age_id
    - If exactly 1 source → append to that effect
    - If 2+ sources AND order deterministic → append to latest effect
    - Otherwise → create joint tech with preqs = all shared_tech_ids, required_tech_count = len(effects)
    """
    if not tech_sources:
        return {'strategy': 'skip', 'reason': 'no tech sources'}

    if len(tech_sources) == 1:
        return {
            'strategy': 'append_to_effect',
            'target_effect_id': tech_sources[0]['effect_id'],
            'correction': correction,
            'reason': 'single source effect',
        }

    auto_sources = [s for s in tech_sources if s['dev'] == 'auto']
    manual_sources = [s for s in tech_sources if s['dev'] == 'manual']

    if not manual_sources:
        sorted_sources = sorted(auto_sources, key=lambda s: s['age_id'] or 0)
        last = sorted_sources[-1]
        return {
            'strategy': 'append_to_effect',
            'target_effect_id': last['effect_id'],
            'correction': correction,
            'reason': 'all-auto sources, append to latest age ' + str(last['age_id']),
        }

    if not auto_sources:
        return {
            'strategy': 'new_joint_tech',
            'target_effect_ids': [s['effect_id'] for s in manual_sources],
            'correction': correction,
            'reason': 'all-manual sources, order indeterminate',
        }

    max_auto_age = max((s['age_id'] or 0) for s in auto_sources)
    all_manual_after_auto = all((s['age_id'] or 0) >= max_auto_age for s in manual_sources)

    if all_manual_after_auto:
        sorted_manual = sorted(manual_sources, key=lambda s: s['age_id'] or 0)
        last = sorted_manual[-1]
        return {
            'strategy': 'append_to_effect',
            'target_effect_id': last['effect_id'],
            'correction': correction,
            'reason': 'manuals all >= auto age, append to latest manual',
        }
    else:
        return {
            'strategy': 'new_joint_tech',
            'target_effect_ids': [s['effect_id'] for s in tech_sources],
            'correction': correction,
            'reason': 'mixed auto/manual with overlapping ages, order indeterminate',
        }


def apply_attr63_fixes(data, plan=None):
    """
    Apply attr=63 conflict corrections to dat.

    Aggregates plan entries by strategy:
    - append_to_effect: corrections appended directly to the target effect object
    - new_joint_tech: one auto tech per unique (preqs_tuple, required_count), with all corrections bundled

    Returns (append_count, joint_count, total_corrections_applied).
    """
    from utils import plus_unit_attribute, append_tech, get_new_tech, get_new_effect, set_require_techs

    if plan is None:
        plan = scan_attr63_conflicts(data)

    effect_to_techs_cache = {}
    def get_shared_techs(eid):
        if eid not in effect_to_techs_cache:
            effect_to_techs_cache[eid] = [tid for tid, t in enumerate(data.techs) if t.effect_id == eid]
        return effect_to_techs_cache[eid]

    append_targets = {}
    joint_pools = {}

    for entry in plan:
        fp = entry['fix_plan']
        strategy = fp['strategy']
        if strategy == 'skip':
            continue

        unit_id = entry['unit_id']
        correction = fp['correction']

        if strategy == 'append_to_effect':
            eid = fp['target_effect_id']
            append_targets.setdefault(eid, []).append((unit_id, correction))
        elif strategy == 'new_joint_tech':
            target_eids = fp['target_effect_ids']
            all_preqs = set()
            for eid in target_eids:
                all_preqs.update(get_shared_techs(eid))
            preqs_sorted = tuple(sorted(all_preqs))
            required_count = len(target_eids)
            key = (preqs_sorted, required_count)
            entry_pool = joint_pools.setdefault(key, {'corrs': [], 'target_effect_ids': target_eids})
            entry_pool['corrs'].append((unit_id, correction))

    total_corrections = 0

    for eid, corrs in append_targets.items():
        effect = data.effects[eid]
        for uid, corr in corrs:
            plus_unit_attribute(effect, uid, -1, COMBAT_ATTR, corr)
            total_corrections += 1

    for (preqs, required_count), pool in joint_pools.items():
        corrs = pool['corrs']
        target_effect_ids = pool['target_effect_ids']
        names = []
        seen_names = set()
        for eid in target_effect_ids:
            tid = get_shared_techs(eid)[0]
            n = data.techs[tid].name or ('effect_%d' % eid)
            if n not in seen_names:
                seen_names.add(n)
                names.append(n)
        joint_name = 'Combat Aura Fix (' + '+'.join(names) + ')'
        tech = get_new_tech(joint_name)
        set_require_techs(tech, *preqs)
        tech.required_tech_count = required_count
        effect = get_new_effect(joint_name)
        for uid, corr in corrs:
            plus_unit_attribute(effect, uid, -1, COMBAT_ATTR, corr)
            total_corrections += 1
        append_tech(data, tech, effect)

    return (len(append_targets), len(joint_pools), total_corrections)