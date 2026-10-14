# -*- coding: utf-8 -*-
"""
全文明科技减价原生覆盖分析

原理:
  扫描 effect command type=101 (Set Tech Cost), 对每个文明、每个建筑,
  如果该建筑下所有可达科技 (is_avail) 都被原生折扣覆盖 (coverage==100%),
  但全局科技 (含本文明不可达的) 还有缺口, 就输出一条。

验证方法 (与 strings 文本对照):
  1. 文明加成描述在 EN strings 文件中, SID = civ_idx + 120149
     路径: resources/en/strings/key-value/key-value-strings-utf8.txt
     例: civ_idx=19 (Italians) -> SID=120168
  2. 搜索关键词 (大小写不敏感):
       discount / cheaper / reduced cost / cost -
       -\\d+%  (如 -50%, -25%, -66%)
       free / no cost / no fee
  3. 对照 strings 中描述的"哪个建筑/哪类科技 折扣多少",
     看 gap_analysis 输出的建筑是否吻合。

注意:
  - 只覆盖 type=101 (科技折扣)。建筑 cost 折扣、单位训练折扣、
    免费科技 (c=0 d=0)、Unique Tech 触发的折扣不在此范围。
  - 全局科技缺口标记为 "[本文明可达=False]" 是正常的, 表示缺口
    科技属于其他文明或不可达分支, 但需要同步给折扣扩展。
  - Chinese 全局科技折扣 (Technologies cost -5/10/15%) 是独立实现,
    不在 type=101 扫描范围内, 忽略即可。
"""

import sys, collections
sys.path.insert(0, r'D:\aoe\AoeAllIn1')
from genieutils.datfile import DatFile

dat = DatFile.parse(r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\empires2_x2_p1.dat')

RES_NAMES = {0: 'FOOD', 1: 'WOOD', 2: 'STONE', 3: 'GOLD'}
ALL_RES = {0, 1, 2, 3}
UNREACHABLE = {716, 1387, 1334}

effect_civs = collections.defaultdict(set)
for ci, c in enumerate(dat.civs):
    if c.tech_tree_id >= 0: effect_civs[c.tech_tree_id].add(ci)
    if c.team_bonus_id >= 0: effect_civs[c.team_bonus_id].add(ci)
for ti, t in enumerate(dat.techs):
    if t.effect_id >= 0 and t.civ >= 0:
        effect_civs[t.effect_id].add(t.civ)

def _is_valid(tid):
    if tid >= len(dat.techs): return False
    t = dat.techs[tid]
    if not t.research_locations or all(rl.location_id <= 0 for rl in t.research_locations): return False
    if t.required_tech_count <= 0: return False
    valid_reqs = sum(1 for x in t.required_techs if x > 0)
    if t.required_tech_count > valid_reqs: return False
    return True

native_cost = collections.defaultdict(list)
for eff_id, civs in effect_civs.items():
    if eff_id >= len(dat.effects): continue
    for cmd in dat.effects[eff_id].effect_commands:
        if cmd.type != 101: continue
        tid = int(cmd.a)
        if not _is_valid(tid): continue
        res = int(cmd.b)
        for civ_idx in civs:
            native_cost[(civ_idx, tid, res)].append((int(cmd.c), float(cmd.d)))

region_techs, civ_disabled, civ_enabled = set(), {}, {}
for ci, c in enumerate(dat.civs):
    eid = c.tech_tree_id
    if eid < 0: continue
    dis, ena = set(), set()
    for cmd in dat.effects[eid].effect_commands:
        if cmd.type == 102: dis.add(int(cmd.d))
        elif cmd.type == 8 and cmd.b == 12 and cmd.d >= 1:
            ena.add(int(cmd.a)); region_techs.add(int(cmd.a))
    civ_disabled[ci] = dis; civ_enabled[ci] = ena

def _is_make_avail(tid):
    if tid >= len(dat.techs): return False
    t = dat.techs[tid]
    has_loc = any(rl.location_id > 0 for rl in t.research_locations) if t.research_locations else False
    return not has_loc and t.required_tech_count == 0 and t.effect_id >= 0

def is_avail(civ_idx, tid):
    if tid in UNREACHABLE or tid >= len(dat.techs): return False
    t = dat.techs[tid]
    if t.civ >= 0 and t.civ != civ_idx: return False
    if tid in civ_disabled.get(civ_idx, set()): return False
    if tid in region_techs and tid not in civ_enabled.get(civ_idx, set()): return False
    for r in t.required_techs:
        if r < 0 or r >= len(dat.techs): continue
        if r == 1138 and 1138 not in civ_enabled.get(civ_idx, set()): return False
        if _is_make_avail(r):
            pre = dat.techs[r]
            if pre.civ >= 0 and pre.civ != civ_idx: return False
            if r in civ_disabled.get(civ_idx, set()): return False
            if r in region_techs and r not in civ_enabled.get(civ_idx, set()): return False
    return True

def get_civ_discounts(civ_idx):
    d = {}
    for (ci, tid, res), entries in native_cost.items():
        if ci != civ_idx: continue
        for c, val in entries:
            if c not in (0, 2): continue
            target = ALL_RES if res == -1 else {res}
            for r in target:
                d.setdefault(tid, set()).add(r)
    return d

BUILDINGS = [
    ('BARRACK', 12), ('ARCHERY_RANGE', 87), ('STABLE', 101),
    ('SIEGE', 49), ('BLACKSMITH', 103), ('CASTLE', 82),
    ('DOCK', 45), ('MONESTARY', 104), ('UNIVERSITY', 209),
    ('MARKET', 84), ('MILL', 68),
]
all_valid_by_loc = {}
for i in range(len(dat.techs)):
    if not _is_valid(i): continue
    for rl in dat.techs[i].research_locations:
        all_valid_by_loc.setdefault(rl.location_id, []).append(i)

EXCLUDE = {
    ('Turks', 'DOCK'), ('Burgundians', 'DOCK'),
    ('Jurchens', 'CASTLE'), ('Khitans', 'ARCHERY_RANGE'),
}
MERGER_EXISTING = {
    ('Burgundians', 'STABLE'), ('Burmese', 'MONESTARY'),
    ('Dravidians', 'BARRACK'), ('Tupi', 'BARRACK'), ('Tupi', 'ARCHERY_RANGE'),
}

for civ_idx in range(1, len(dat.civs)):
    c = dat.civs[civ_idx]
    discounts = get_civ_discounts(civ_idx)
    if not discounts: continue
    
    for bname, bloc in BUILDINGS:
        if (c.name, bname) in EXCLUDE: continue
        techs_here = all_valid_by_loc.get(bloc, [])
        if not techs_here: continue
        avail = [tid for tid in techs_here if is_avail(civ_idx, tid)]
        if not avail: continue
        covered_avail = [tid for tid in avail if tid in discounts]
        coverage = len(covered_avail) / len(avail) if avail else 0
        if coverage < 0.999: continue
        
        covered_global = [tid for tid in techs_here if tid in discounts]
        gap = set(techs_here) - set(covered_global)
        if not gap: continue
        
        res_set = set()
        for tid, rset in discounts.items():
            if tid in techs_here: res_set.update(rset)
        res_str = '+'.join(sorted(RES_NAMES.get(r, str(r)) for r in res_set))
        
        status = "✅ 已有" if (c.name, bname) in MERGER_EXISTING else "🔥 新增"
        print(f"\n{'='*70}")
        print(f"{status} {c.name:15s} → {bname:15s} (loc={bloc})  覆盖率=100%  GAP={len(gap)}  折扣资源={res_str}")
        print(f"  可达={len(avail)}  全局={len(techs_here)}")
        
        print(f"  \n  [原生已覆盖 {len(covered_global)} 个]:")
        for tid in sorted(covered_global):
            t = dat.techs[tid]
            print(f"    ✅ {tid:5d} {t.name:30s} civ={t.civ}  [本文明可达={is_avail(civ_idx,tid)}]")
        
        print(f"\n  [GAP {len(gap)} 个 - 需扩展]:")
        for tid in sorted(gap):
            t = dat.techs[tid]
            mark = "🔒" if is_avail(civ_idx, tid) else "  "
            print(f"    {mark} {tid:5d} {t.name:30s} civ={t.civ}  [本文明可达={is_avail(civ_idx,tid)}]")