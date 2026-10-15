import collections
from functools import reduce
from genieutils.datfile import DatFile
from utils import get_new_tech, get_new_effect, append_tech, set_require_techs, set_tech_cost, set_tech_time
import constants


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

def _is_valid_discount_target(data, tid):
    """判断某个 tech 是否是「可研发的、适合折扣合并的目标」
    排除:
      - location_id 全部 <= 0 → 纯脚本/幻影科技 (如 Paphos Shadow, 编年史政体 Reset)
      - required_tech_count <= 0 → Doctrine / 自动触发类
      - required_tech_count > 有效前置数 → 文明专属 bug 科技
    """
    if tid >= len(data.techs):
        return False
    t = data.techs[tid]
    if not t.research_locations or all(rl.location_id <= 0 for rl in t.research_locations):
        return False
    if t.required_tech_count <= 0:
        return False
    valid_reqs = sum(1 for x in t.required_techs if x > 0)
    if t.required_tech_count > valid_reqs:
        return False
    return True


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
                if not _is_valid_discount_target(data, tid):
                    continue
                if c == 0:
                    native_cost[(tid, res)].append(('SET', d))
                elif c == 2:
                    native_cost[(tid, res)].append(('MULT', d))

            elif cmd.type == 103:
                tid, c, d = cmd.a, cmd.c, cmd.d
                if not _is_valid_discount_target(data, tid):
                    continue
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
# Step 2: 手动补充规则 — 原生 Tech Tree / Team Bonus / C-Bonus 未覆盖的折扣
# =============================================================================
# 分为两类:
#   A. 建筑遍历规则 — 代码动态查找指定建筑下的所有科技, 自动排除原生已覆盖的
#   B. 特定科技条目 — 固定 tech_id 的 SET_0 / 自定义值, 带注释说明来源
#
# 所有资源ID / 建筑ID / 折扣值均使用 constants.py 常量, 避免魔数
#
# ⚠️ 以下 gap_analysis 识别的条目不在此处处理 — 由 custom_civ_bonus.py 直接 force_research:
#   - French (Franks)  → MILL: 原生 E43 覆盖 Crop rotation/Heavy plow/Horse collar (12/13/14) SET_0,
#         缺 Khitan 经济科技 (1012 Grazing Grasslands / 1013 Enclosures / 1014 Livestock Husbandry) SET_0
#   - Vietnamese      → MILL: 原生 E692 覆盖 12/13/14 wood=0, 同样缺 1012/1013/1014
#   - Burgundians     → MILL: 原生 E782 覆盖 12/13/14 food 0.6, 缺 1012/1013/1014 food 0.6,
#         另外 Burgundians 还有"经济科技提前一个时代可研发"的需求, 用 force_research 实现更合适
#   这三者在 custom_civ_bonus.py Burgundians case 里统一 force_research(1012/1013/1014) 处理,
#   提前时代通过 set_require_techs 控制阶段 (feudal_duplicate / castle_duplicate)
# =============================================================================

def _expand_building_rule(data, building_id, resource_type, multiplier, exclude_ids=()):
    """展开一条建筑遍历规则 → 生成 [(tid, res, mult), ...]
    查找指定建筑下的所有有效科技, 自动排除:
      - 无效科技 (幻影/Doctrine/bug 科技)
      - exclude_ids 指定的排除集合
    注意: 不排除已有原生 type 101 覆盖的科技 — 手动条目直接覆盖最终值,
          原生只覆盖部分资源时, res=-1 会补全所有资源
    """
    entries = []
    exclude = set(exclude_ids)

    for tid, tech in enumerate(data.techs):
        if tid in exclude:
            continue
        if not _is_valid_discount_target(data, tid):
            continue
        loc_ids = {rl.location_id for rl in tech.research_locations}
        if building_id not in loc_ids:
            continue
        entries.append((tid, resource_type, multiplier))

    return entries


def _build_manual_entries(data):
    """构建所有手动补充条目, 返回 (cost_entries, time_entries)

    cost_entries: [(注释, tid, res, mult), ...]
    time_entries: [(注释, tid, mult), ...]
    """
    cost_entries = []
    time_entries = []

    # =========================================================================
    # A. 建筑遍历规则 — 代码动态查找, 新文明/新科技自动覆盖
    # =========================================================================

    # Burgundians Stable 科技 res=-1 半价
    # 原生 E782 只覆盖 39/435/254/428/209/265 的 food+gold 0.5,
    # 其他 Stable 科技 (236/521/526/631/715/843/1033/1171/1328/786) 完全无 type 101,
    # 统一覆盖所有资源为 0.5 (跳过原生已覆盖的 254/428, 结果一样, 减少冗余)
    comment = 'Burgundians Stable 半价'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.STABLE_ID,
        resource_type=constants.RES_ALL,
        multiplier=constants.BURGUNDIAN_STABLE_TECH_DISCOUNT,
        exclude_ids=(254, 428),
    ))

    # Burmese Monastery 科技 res=-1 半价
    # 原生 E650/E651 完全无 type 101/103, 全部需要补充 (441 Herbal Medicine 除外)
    comment = 'Burmese Monastery 半价 (原生完全无 type 101)'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.MONESTARY_ID,
        resource_type=constants.RES_ALL,
        multiplier=constants.BURMESE_MONASTERY_DISCOUNT,
        exclude_ids=(441,),
    ))

    # Dravidian Barracks 科技 res=-1 半价
    # 原生 E838 只覆盖 197/207/215/217/222/264/429/602/716/875 的 food+gold 0.5,
    # 其他 Barracks 科技 (384/434/885/982/1137/1173/1174/1291/1387/1401/...) 完全无 type 101,
    # 统一覆盖所有资源为 0.5 (跳过原生已覆盖的, 结果一样, 减少冗余)
    comment = 'Dravidian Barracks 半价'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.BARRACK_ID,
        resource_type=constants.RES_ALL,
        multiplier=constants.DRAVIDIANS_TECH_DISCOUNT,
        exclude_ids=(197, 207, 215, 217, 222, 264, 429, 602, 716, 875),
    ))

    # Tupi Barracks 科技 food 半价
    # 原生 C-Bonus E1397 只覆盖 197/207/215/217/222/264/429/602/716/875/
    # 1350/1351/1352/1391/1402 的 food 0.5,
    # 其他 Barracks 科技 (384/434/885/982/1137/1173/1174/1291/1387/1401/1454) 完全无 type 101,
    # 统一覆盖 food 为 0.5 (跳过原生已覆盖的, 结果一样, 减少冗余)
    comment = 'Tupi Barracks food 半价'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.BARRACK_ID,
        resource_type=constants.RES_FOOD,
        multiplier=constants.TUPI_TECH_FOOD_DISCOUNT,
        exclude_ids=(197, 207, 215, 217, 222, 264, 429, 602, 716, 875,
                     1350, 1351, 1352, 1391, 1402),
    ))

    # Tupi Archery Range 科技 food 半价
    # 原生 C-Bonus E1397 只覆盖 98/100/218/237/436/437/481/599/655 的 food 0.5,
    # 其他 Archery 科技 (1334/1378/1451/1452) 完全无 type 101,
    # 统一覆盖 food 为 0.5 (跳过原生已覆盖的, 结果一样, 减少冗余)
    comment = 'Tupi Archery Range food 半价'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.ARCHERY_RANGE_ID,
        resource_type=constants.RES_FOOD,
        multiplier=constants.TUPI_TECH_FOOD_DISCOUNT,
        exclude_ids=(98, 100, 218, 237, 436, 437, 481, 599, 655),
    ))

    # Italians Dock 科技 res=-1 0.75
    # 原生 E259 只覆盖 Dock 6 个科技 (73/905/906/412/1019/1702) ALL 0.75,
    # GAP: 244 Heavy Demolition / 372 Viking LBT / 448 Elite Turtle Ship /
    #       597 Elite Caravel / 1010 Dragon Ship 完全无 type 101,
    # 统一覆盖 ALL 为 0.75 (跳过原生已覆盖的)
    comment = 'Italians Dock 0.75'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.DOCK_ID,
        resource_type=constants.RES_ALL,
        multiplier=constants.ITALIANS_TECH_DISCOUNT,
        exclude_ids=(73, 905, 906, 412, 1019, 1702),
    ))

    # Bulgarians Siege 科技 food 0.5
    # 原生 E706 已覆盖 96/239/255/257/320 的 food 0.5,
    # GAP: 787 Houfnice / 838 Elite Armored Elephant / 980 Heavy Rocket Cart 完全无 type 101,
    # 统一覆盖 food 为 0.5 (跳过原生已覆盖的)
    comment = 'Bulgarians Siege food 0.5'
    cost_entries.extend((comment, e[0], e[1], e[2]) for e in _expand_building_rule(
        data,
        building_id=constants.SIEGE_ID,
        resource_type=constants.RES_FOOD,
        multiplier=0.5,
        exclude_ids=(96, 239, 255, 257, 320),
    ))

    # =========================================================================
    # B. 特定科技条目 — 原生完全无 type 101 覆盖, 或 SET_0 覆盖所有资源
    # =========================================================================

    # --- Bulgarians Free Champion ---
    # 原生完全无 SET_0 覆盖 Champion 264 / 编年史 Champion 1174
    c1 = 'Bulgarians Free Champion'
    cost_entries.append((c1, constants.CHAMPION_TECH_ID, constants.RES_FOOD, 0))
    cost_entries.append((c1, constants.CHAMPION_TECH_ID, constants.RES_GOLD, 0))
    time_entries.append((c1, constants.CHAMPION_TECH_ID, 0))
    cost_entries.append((c1, constants.CHRONICLE_CHAMPION_TECH_ID, constants.RES_FOOD, 0))
    cost_entries.append((c1, constants.CHRONICLE_CHAMPION_TECH_ID, constants.RES_GOLD, 0))
    time_entries.append((c1, constants.CHRONICLE_CHAMPION_TECH_ID, 0))

    # --- Turks Free Winged-Hussar ---
    # 原生 Poles E801 只给 food 0.5, Turks 需要全资源 SET_0
    c2 = 'Turks Free Winged-Hussar'
    cost_entries.append((c2, constants.WINGED_HUSSAR_TECH_ID, constants.RES_ALL, 0))
    time_entries.append((c2, constants.WINGED_HUSSAR_TECH_ID, 0))

    # --- Turks 火药科技半价 ---
    # 原生 Turks E263 只覆盖 Chemistry 47 SET_0 / Bombard Tower 64 food/wood 0.5 /
    # Elite Cannon Galley 376 wood/gold 0.5,
    # Houfnice 787 / Heavy Rocket Cart 980 / Elite Fire Lancer 982 完全无原生 type 101
    c3 = 'Turks 火药科技半价'
    cost_entries.append((c3, constants.HOUFNICE_TECH_ID, constants.RES_ALL, constants.TURKISH_GUNPOWDER_DISCOUNT))
    cost_entries.append((c3, constants.HEAVY_ROCKET_CART_TECH_ID, constants.RES_ALL, constants.TURKISH_GUNPOWDER_DISCOUNT))
    cost_entries.append((c3, constants.ELITE_FIRE_LANCER_TECH_ID, constants.RES_ALL, constants.TURKISH_GUNPOWDER_DISCOUNT))

    # --- Jurchens Siege ext wood 0.25 ---
    # 原生 C-Bonus E995 已覆盖 239/980/321/379 的 wood 0.25
    # Onager 257 / Siege Onager 320 虽然原生无 type 101, 但其资源需求只有 food+gold, 不含 wood,
    # 故无需手动补充 wood 折扣

    return cost_entries, time_entries


def _compile_manual_lists(data):
    """从带注释条目编译出 Step 3 需要的纯列表"""
    cost_entries, time_entries = _build_manual_entries(data)
    cost_list = [(tid, res, mult) for _, tid, res, mult in cost_entries]
    time_list = [(tid, mult) for _, tid, mult in time_entries]
    return cost_list, time_list


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


def _merge_native_time(native_time, data):
    """原生 type 103 合并 → dict[tid, final_multiplier]"""
    final = {}
    for tid, entries in native_time.items():
        has_set_zero = any(e[0] == 'SET_ZERO' for e in entries)
        has_set_abs_zero = any(e[0] == 'SET_ABS' and e[1] == 0 for e in entries)
        if has_set_zero or has_set_abs_zero:
            final[tid] = 0
            continue

        set_abs_vals = [e[1] for e in entries if e[0] == 'SET_ABS' and e[1] != 0]
        if set_abs_vals:
            final[tid] = set_abs_vals[0] / _orig_time(data, tid) if _orig_time(data, tid) > 0 else 1.0
            continue

        mults = [e[1] for e in entries if e[0] == 'MULT']
        final[tid] = reduce(lambda a, b: a * b, mults, 1.0) if mults else 1.0
    return final


def _apply_manual_cost(final_cost, manual_list, data):
    """手动 101 条目与 final_cost 相乘 (SET_0 即乘 0, 与原生合并规则一致)"""
    for tid, res, mult in manual_list:
        keys = []
        if res == -1:
            if tid >= len(data.techs):
                continue
            for rc in data.techs[tid].resource_costs:
                if rc.type >= 0:
                    keys.append((tid, rc.type))
        else:
            keys.append((tid, res))
        for key in keys:
            cur = final_cost.get(key, 1.0)
            final_cost[key] = cur * mult
    return final_cost


def _apply_manual_time(final_time, manual_list):
    """手动 103 条目与 final_time 相乘 (SET_0 即乘 0, 与原生合并规则一致)"""
    for tid, mult in manual_list:
        cur = final_time.get(tid, 1.0)
        final_time[tid] = cur * mult
    return final_time


def merge_discounts(data):
    """主入口: 返回 (final_cost, final_time) 两个 map"""
    native_cost, native_time = collect_native_discounts(data)

    final_cost = _merge_native_cost(native_cost, data)
    final_time = _merge_native_time(native_time, data)

    manual_cost_list, manual_time_list = _compile_manual_lists(data)

    final_cost = _apply_manual_cost(final_cost, manual_cost_list, data)
    final_time = _apply_manual_time(final_time, manual_time_list)

    return final_cost, final_time


# =============================================================================
# Step 2.5: 常量 ↔ 原生 effect 校验
# =============================================================================
# 每条手动规则用到的折扣常量, 应该对齐某个原生 type 101 c=2 命令的 d 值
# 这里硬编码对齐关系, 版本更新导致原生 d 值变化时, 打印 MISMATCH 提醒
# =============================================================================

_NATIVE_ALIGNMENT_SPECS = [
    # (常量名, 原生 effect_id, cmd_type, tid, cmd_b(resource), cmd_c, 期望 d)
    ('BURGUNDIAN_ECO_FOOD_DISCOUNT',     782, 101, 12,  0, 2, 0.6),

    ('BURGUNDIAN_STABLE_TECH_DISCOUNT',  782, 101, 39,  -1, 2, 0.5),

    ('TURKISH_GUNPOWDER_DISCOUNT',       263, 101, 64,  -1, 2, 0.5),

    ('JURCHENS_SIEGE_WOOD_DISCOUNT',     995, 101, 239, 1,  2, 0.25),

    ('DRAVIDIANS_TECH_DISCOUNT',         838, 101, 197, 0,  2, 0.5),

    ('TUPI_TECH_FOOD_DISCOUNT',          1397, 101, 197, 0,  2, 0.5),
]


def validate_discount_constants(data):
    """校验常量 ↔ 原生 effect d 值对齐, 不通过只打印不报错"""
    import constants as C

    ok_cnt = 0
    mismatch_cnt = 0

    for const_name, eff_id, cmd_type, tid, exp_b, exp_c, exp_d in _NATIVE_ALIGNMENT_SPECS:
        const_val = getattr(C, const_name, None)
        if const_val is None:
            print('  [validate] %s: 常量 MISSING' % const_name)
            mismatch_cnt += 1
            continue

        eff = data.effects[eff_id]
        found = []
        for cmd in eff.effect_commands:
            if cmd.type == cmd_type and cmd.a == tid:
                if exp_b == -1 or cmd.b == exp_b:
                    found.append(cmd)

        if not found:
            print('  [validate] %s: 原生 E%d 101 tid=%d 未找到 c=%d d=%g (常量=%g)' %
                  (const_name, eff_id, tid, exp_c, exp_d, const_val))
            mismatch_cnt += 1
            continue

        matched = False
        for cmd in found:
            if cmd.c == exp_c and abs(cmd.d - const_val) < 0.001:
                matched = True
                break

        if matched:
            ok_cnt += 1
        else:
            native_ds = set((c.c, round(c.d, 4)) for c in found)
            print('  [validate] %s MISMATCH: 常量=%g 原生 E%d 101 tid=%d c/d 组合=%s' %
                  (const_name, const_val, eff_id, tid, native_ds))
            mismatch_cnt += 1

    if mismatch_cnt:
        print('  [validate] %d/%d 通过, %d 不匹配, 请手动核对常量是否需要更新' %
              (ok_cnt, ok_cnt + mismatch_cnt, mismatch_cnt))
    else:
        print('  [validate] %d/%d 全部通过' % (ok_cnt, ok_cnt + mismatch_cnt))


# =============================================================================
# Step 3: 创建新科技，统一用 c=0 (SET) 输出最终绝对值
# =============================================================================

def build_discount_tech(data, params):
    validate_discount_constants(data)
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