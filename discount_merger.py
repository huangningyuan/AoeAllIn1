import collections
from functools import reduce
from genieutils.datfile import DatFile
from utils import get_new_tech, get_new_effect, append_tech, set_require_techs, set_tech_cost, set_tech_time


def _orig_time(data, tid):
    locs = data.techs[tid].research_locations
    return locs[0].research_time if locs else 0


# =============================================================================
# Step 1: 收集原生 Tech Tree + Team Bonus + C-Bonus 里的 type 101 / 103
# =============================================================================
# 返回:
#   native_cost: dict[(tid, res), list[tuple(tag, value)]]
#     tag='SET'    -> c=0 set cost to absolute value d (通常 d=0 即免费)
#     tag='MULT'   -> c=2 discount multiplier d (0.x 形式)
#   native_time: dict[tid, list[tuple(tag, value)]]
#     tag='SET_ZERO' -> c=0, d=0 (时间 SET_0)
#     tag='SET_ABS'  -> c=0, d!=0 (时间设为绝对值 d, 原生几乎不用)
#     tag='MULT'     -> c=2 discount d / c=1/-1 绝对增减 d 转 multiplier
# =============================================================================

def collect_native_discounts(data):
    native_cost = collections.defaultdict(list)
    native_time = collections.defaultdict(list)

    scan_eff_ids = set()

    for civ in data.civs:
        if civ.tech_tree_id >= 0:
            scan_eff_ids.add(civ.tech_tree_id)
        if civ.team_bonus_id >= 0:
            scan_eff_ids.add(civ.team_bonus_id)

    for t in data.techs:
        if t.civ >= 1 and t.effect_id >= 0:
            scan_eff_ids.add(t.effect_id)

    for eff_id in scan_eff_ids:
        if eff_id >= len(data.effects):
            continue
        eff = data.effects[eff_id]
        for cmd in eff.effect_commands:
            if cmd.type == 101:
                tid, res, c, d = cmd.a, cmd.b, cmd.c, cmd.d
                if c == 0:
                    native_cost[(tid, res)].append(('SET', d))
                elif c == 2:
                    native_cost[(tid, res)].append(('MULT', d))

            elif cmd.type == 103:
                tid, c, d = cmd.a, cmd.c, cmd.d
                ot = _orig_time(data, tid)
                if c == 0:
                    if d == 0:
                        native_time[tid].append(('SET_ZERO',))
                    else:
                        native_time[tid].append(('SET_ABS', d))
                elif c in (1, -1):
                    if ot > 0:
                        native_time[tid].append(('MULT', (ot + d) / ot))
                elif c == 2:
                    native_time[tid].append(('MULT', d))

    return native_cost, native_time


# =============================================================================
# Step 2: 手动补充列表 — 原生完全没 type 101/103 覆盖的科技
# =============================================================================
# 格式:
#   _101_extend_list: [(tech_id, resource_type, final_multiplier), ...]
#     resource_type: -1=全部资源, 0=food, 1=wood, 2=stone, 3=gold
#     final_multiplier: 最终合并后的值, 直接覆盖原生合并结果
#       0 = SET_0 (免费)
#       0.x = 折扣乘数 (乘到原值上得到最终成本)
#
#   _103_extend_list: [(tech_id, final_multiplier), ...]
#     final_multiplier 同上, 直接覆盖原生合并结果
#
# 注意: 这些条目是从 civ_bonuses.py 的原始硬编码整理而来, 已修正 resource_type
# 写错 (type 2=stone 被当成 gold 的 bug)
# =============================================================================

_101_extend_list = [
    # Houfnice (787): Turks Tech Tree 没写, Bulgarians/Danes 也没覆盖
    #   food = Turks 0.5 * Bulgarians 0.5 = 0.25
    #   gold = Turks 0.5 * Danes 0.66 = 0.33
    (787, 0, 0.25),
    (787, 3, 0.33),

    # Heavy Rocket Cart (980): Turks/Danes Tech Tree 没写
    #   wood = Turks 0.5 * Jurchens 0.25 = 0.125 (覆盖原生 Jurchens 单独的 0.25)
    #   gold = Turks 0.5 * Danes 0.66 = 0.33
    (980, 1, 0.125),
    (980, 3, 0.33),
]

_103_extend_list = []


# =============================================================================
# Step 3: 合并原生收集 → 最终 multiplier map, 手动直接覆盖
# =============================================================================
#
# 原生合并规则:
#   1. SET_0 优先级最高 → 直接归零
#   2. 所有 MULT 做乘法合并
#   3. res=-1 的通用折扣自动展开到 tech 有成本的每个资源
#
# 然后手动列表里的条目, 按相同 key 直接覆盖最终值
# =============================================================================

def _merge_native_cost(native_cost, data):
    """原生 type 101 合并 → dict[(tid, res), final_multiplier]"""
    fc = {}

    gen_entries = [(tid, entries) for (tid, res), entries in native_cost.items() if res == -1]
    spec_entries = [(tid, res, entries) for (tid, res), entries in native_cost.items() if res != -1]

    for tid, res, entries in spec_entries:
        fc.setdefault((tid, res), []).extend(entries)

    for tid, entries in gen_entries:
        if tid >= len(data.techs):
            continue
        target_res = set()
        for rc in data.techs[tid].resource_costs:
            if rc.type >= 0:
                target_res.add(rc.type)
        if not target_res:
            target_res = {0, 1, 2, 3}
        for tr in target_res:
            fc.setdefault((tid, tr), []).extend(entries)

    final = {}
    for (tid, res), entries in fc.items():
        if any(e[0] == 'SET' and e[1] == 0 for e in entries):
            final[(tid, res)] = 0
        else:
            mults = [e[1] for e in entries if e[0] == 'MULT']
            final[(tid, res)] = reduce(lambda a, b: a * b, mults, 1.0) if mults else 1.0
    return final


def _merge_native_time(native_time):
    """原生 type 103 合并 → dict[tid, final_multiplier]"""
    final = {}
    for tid, entries in native_time.items():
        has_set_zero = any(e[0] == 'SET_ZERO' for e in entries)
        has_set_abs_zero = any(e[0] == 'SET_ABS' and e[1] == 0 for e in entries)
        if has_set_zero or has_set_abs_zero:
            final[tid] = 0
        else:
            mults = [e[1] for e in entries if e[0] == 'MULT']
            final[tid] = reduce(lambda a, b: a * b, mults, 1.0) if mults else 1.0
    return final


def _apply_manual_cost(final_cost, manual_list, data):
    """手动 101 条目直接覆盖 final_cost"""
    for tid, res, mult in manual_list:
        if res == -1:
            if tid >= len(data.techs):
                continue
            for rc in data.techs[tid].resource_costs:
                if rc.type >= 0:
                    final_cost[(tid, rc.type)] = mult
        else:
            final_cost[(tid, res)] = mult
    return final_cost


def _apply_manual_time(final_time, manual_list):
    """手动 103 条目直接覆盖 final_time"""
    for tid, mult in manual_list:
        final_time[tid] = mult
    return final_time


def merge_discounts(data):
    """主入口: 返回 (final_cost, final_time) 两个 map"""
    native_cost, native_time = collect_native_discounts(data)

    final_cost = _merge_native_cost(native_cost, data)
    final_time = _merge_native_time(native_time)

    final_cost = _apply_manual_cost(final_cost, _101_extend_list, data)
    final_time = _apply_manual_time(final_time, _103_extend_list)

    return final_cost, final_time


# =============================================================================
# Step 3: 创建新科技，统一用 c=0 (SET) 输出最终绝对值
# =============================================================================

def build_discount_tech(data, params):
    final_cost, final_time = merge_discounts(data)

    tech = get_new_tech('All Discounts Merged')
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect('All Discounts Merged')

    cnt = 0
    skipped = 0
    for (tid, res), mult in sorted(final_cost.items()):
        if mult != 0 and abs(mult - 1.0) < 0.001:
            continue
        orig = 0
        for rc in data.techs[tid].resource_costs:
            if rc.type == res:
                orig = rc.amount
                break
        if orig <= 0:
            skipped += 1
            continue
        final_val = 0 if mult == 0 else round(orig * mult, 1)
        set_tech_cost(effect, tid, res, final_val)
        cnt += 1

    for tid, mult in sorted(final_time.items()):
        if mult != 0 and abs(mult - 1.0) < 0.001:
            continue
        orig = _orig_time(data, tid)
        final_val = 0 if mult == 0 else round(orig * mult, 1)
        set_tech_time(effect, tid, final_val)
        cnt += 1

    print(f'  [discount_merger] {cnt} commands '
          f'(cost={len([v for v in final_cost.values() if v != 0 or True])}, '
          f'time={len(final_time)})')

    return append_tech(data, tech, effect)