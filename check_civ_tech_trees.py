# -*- coding: utf-8 -*-
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genieutils.datfile import DatFile
import civ_name as civ_names

GAME_DATA_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat'
CIV_TECH_TREES_PATH = os.path.join(GAME_DATA_PATH, 'CivTechTrees')
DAT_FILE = os.path.join(GAME_DATA_PATH, 'empires2_x2_p1.dat')
ZH_STRINGS_FILE = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\zh\strings\key-value\key-value-strings-utf8.txt'
EN_STRINGS_FILE = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\en\strings\key-value\key-value-strings-utf8.txt'


def load_strings(filepath):
    result = {}
    if not os.path.exists(filepath):
        return result
    pattern = re.compile(r'^(\d+)\s+"(.*)"\s*$')
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                sid = int(m.group(1))
                text = m.group(2)
                result[sid] = text
    return result
SKIP_NODE_TYPES = {'UniqueUnit', 'RegionalBuilding', 'UniqueBuilding'}

UNIT_NODE_TYPES = {'Unit', 'RegionalUnit'}
BUILDING_LIKE_TYPES = {'BuildingTech', 'BuildingNonTech'}
UNIT_LIKE_TYPES = UNIT_NODE_TYPES | BUILDING_LIKE_TYPES
TECH_NODE_TYPES = {'Research', 'UnitUpgrade', 'UniqueTech', 'RegionalTech'}

# Tech 35 "Galleon" is the player-facing clickable tech (research_locations set,
# but effect_id=-1, no effect of its own). Real ship upgrades for Galleon/
# Fast Fire Ship/Carrack are done by layer-2 helper techs that require Tech 35
# as a prerequisite (required_techs=(35, ...)). JSON UnitUpgrade nodes point
# Trigger Tech ID at layer-1 (player-facing), so we must also check layer-2.
TECH_35_REAL_UPGRADES = {911, 246, 904}

# Known exceptions: (civ_file, node_type, node_id) — do NOT flag these
# Reason: some buildings/techs are disabled indirectly (e.g. via enable tech that grants
# a replacement, or by a workaround) and there's no direct disable in the Tech Tree effect.
EXCEPTIONS = {
    'ARMENIANS': {
        ('Research', 375),       # Dry Dock - confirmed JSON bug
        ('BuildingTech', 584),   # Mining Camp - replaced by tech 940 (Armenian Mt. Camels)
        ('BuildingTech', 562),   # Lumber Camp - replaced by tech 940
    },
    'GEORGIANS': {
        ('BuildingTech', 584),   # Mining Camp - replaced by tech 932 (Georgian Mt. Camels)
        ('BuildingTech', 562),   # Lumber Camp - replaced by tech 932
    },
}

# Tech 137 "Castle -- Age Three" is the universal (civ=-1) tech that enables
# Castle(82) via effect type=2 a=82 b=1. Turks disable 137 but use their own
# exclusive Tech 354 "Turk Castle" (civ=10, same effect) as a replacement.
# We must NOT treat 137's make_avail_units as effectively disabled for Turks
# — they still get Castle through 354.
SKIP_MAKEAVAIL_DISABLE_TECHS = {
    137,  # Castle -- Age Three
}


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_tech_effect_cache(data, cache, tech_id):
    if tech_id in cache:
        return cache[tech_id]
    if tech_id >= len(data.techs):
        cache[tech_id] = None
        return None
    tech = data.techs[tech_id]
    if tech.effect_id < 0 or tech.effect_id >= len(data.effects):
        cache[tech_id] = None
        return None
    teff = data.effects[tech.effect_id]
    make_avail_units = []
    disable_units = []
    upgrade_pairs = []
    for tcmd in teff.effect_commands:
        if tcmd.type == 2 and tcmd.b == 1:
            make_avail_units.append(tcmd.a)
        elif tcmd.type == 2 and tcmd.b == 0:
            disable_units.append(tcmd.a)
        elif tcmd.type == 3:
            upgrade_pairs.append((tcmd.a, tcmd.b))
    cache[tech_id] = {
        'name': tech.name,
        'make_avail_units': make_avail_units,
        'disable_units': disable_units,
        'upgrade_pairs': upgrade_pairs,
    }
    return cache[tech_id]


def index_json_nodes(json_data):
    by_node_id = {}
    by_trigger_tech_id = {}

    for arr_name in ('civ_techs_units', 'civ_techs_buildings'):
        for node in json_data.get(arr_name, []):
            if not isinstance(node, dict):
                continue
            node_type = node.get('Node Type')
            if node_type in SKIP_NODE_TYPES:
                continue

            nid = node.get('Node ID')
            if nid is not None:
                by_node_id.setdefault(nid, []).append(node)

            ttid = node.get('Trigger Tech ID')
            if ttid is not None:
                by_trigger_tech_id.setdefault(ttid, []).append(node)

    return by_node_id, by_trigger_tech_id


def main():
    print("Loading dat file...")
    data = DatFile.parse(DAT_FILE)
    print(f"  Loaded {len(data.techs)} techs, {len(data.effects)} effects, {len(data.civs)} civs")

    tech_tree_effects = {}
    for eff in data.effects:
        if eff.name.endswith('Tech Tree'):
            civ_name = eff.name[:-10]
            tech_tree_effects[civ_name] = eff
    print(f"Found {len(tech_tree_effects)} Tech Tree effects")

    tech_effect_cache = {}

    civ_dat_status = {}
    for civ_name, eff in tech_tree_effects.items():
        status = {
            'disabled_techs': set(),
            'enabled_techs': set(),
            'direct_disabled_units': set(),
        }
        for cmd in eff.effect_commands:
            if cmd.type == 102:
                tid = int(cmd.d)
                status['disabled_techs'].add(tid)
                build_tech_effect_cache(data, tech_effect_cache, tid)
            elif cmd.type == 8 and cmd.d == 1.0 and cmd.b == 12:
                tid = int(cmd.a)
                status['enabled_techs'].add(tid)
                build_tech_effect_cache(data, tech_effect_cache, tid)
            elif cmd.type == 2 and cmd.b == 0:
                status['direct_disabled_units'].add(cmd.a)
        civ_dat_status[civ_name] = status

    print(f"Cached {len(tech_effect_cache)} unique tech effects")

    civ_effective_disabled_units = {}
    civ_disabled_make_avail_techs = {}
    civ_disabled_upgrade_techs = {}
    for civ_name, status in civ_dat_status.items():
        s = set(status['direct_disabled_units'])

        disabled_make_avail = set()
        disabled_upgrade = set()
        for tid in status['disabled_techs']:
            info = tech_effect_cache.get(tid)
            if info is None:
                continue
            if info['make_avail_units']:
                disabled_make_avail.add(tid)
            if info['upgrade_pairs']:
                disabled_upgrade.add(tid)
            if tid not in SKIP_MAKEAVAIL_DISABLE_TECHS:
                s.update(info['make_avail_units'])
                for _src, dst in info['upgrade_pairs']:
                    s.add(dst)

        for tid in status['enabled_techs']:
            info = tech_effect_cache.get(tid)
            if info is None:
                continue
            s.update(info['disable_units'])
            s.difference_update(info['make_avail_units'])

        civ_effective_disabled_units[civ_name] = s
        civ_disabled_make_avail_techs[civ_name] = disabled_make_avail
        civ_disabled_upgrade_techs[civ_name] = disabled_upgrade

    all_json_files = sorted(
        f.replace('.json', '')
        for f in os.listdir(CIV_TECH_TREES_PATH)
        if f.endswith('.json')
    )

    problems = []
    warnings = []

    for civ_file in all_json_files:
        tt_name = civ_names.from_json_file(civ_file)

        if civ_names.is_chronicle(tt_name):
            continue

        json_path = os.path.join(CIV_TECH_TREES_PATH, civ_file + '.json')
        json_data = load_json(json_path)

        if tt_name not in civ_dat_status:
            warnings.append(f"  [WARN] No Tech Tree effect for {civ_file} (tried: {tt_name})")
            continue

        dat_status = civ_dat_status[tt_name]
        eff_disabled_units = civ_effective_disabled_units[tt_name]
        by_node_id, by_trigger_tech_id = index_json_nodes(json_data)

        # 构建每个 real upgrade tech 升级到的目标 Node ID 集合（从 dat type=3）
        real_tech_to_upgrade_nodes = {}
        for tid in TECH_35_REAL_UPGRADES:
            info = tech_effect_cache.get(tid)
            if not info:
                continue
            nodes = set()
            for src, dst in info['upgrade_pairs']:
                nodes.add(dst)
            if nodes:
                real_tech_to_upgrade_nodes[tid] = nodes

        # 反向 UnitUpgrade TTID=35 → 对应的 real upgrade techs
        # 通过 Node ID 反查：每个 TTID=35 的 UnitUpgrade 节点，看哪个 real tech 升级到它
        node_id_to_real_techs = {}
        for real_tid, target_nodes in real_tech_to_upgrade_nodes.items():
            for nid in target_nodes:
                node_id_to_real_techs.setdefault(nid, set()).add(real_tid)

        # ================================================================
        # 正向检查 A: dat disabled_tech → JSON 对应节点应 NotAvailable
        #   Research / UniqueTech: Node ID = tech_id
        #   UnitUpgrade (TTID 直接匹配): Trigger Tech ID = tech_id
        #   UnitUpgrade (tech 35 映射): disable real upgrade tech → 其目标 Node ID
        #     且那个 UnitUpgrade 的 TTID 必须是 35 才算（直接匹配 real tech 的走正常流程）
        # ================================================================
        # 先处理 real upgrade tech 禁用 → 目标 Node ID 且 TTID=35 的 UnitUpgrade
        for real_tid, target_nodes in real_tech_to_upgrade_nodes.items():
            if real_tid not in dat_status['disabled_techs']:
                continue
            for nid in target_nodes:
                for node in by_node_id.get(nid, []):
                    if node.get('Node Type') != 'UnitUpgrade':
                        continue
                    if node.get('Trigger Tech ID') != 35:
                        continue
                    ns = node.get('Node Status')
                    if ns != 'NotAvailable':
                        rtname = data.techs[real_tid].name if real_tid < len(data.techs) else '?'
                        problems.append({
                            'tt_name': tt_name, 'civ_file': civ_file,
                            'issue': 'dat_disabled_json_enabled',
                            'tech_id': real_tid, 'tech_name': rtname,
                            'tech_sid': data.techs[real_tid].language_dll_name if real_tid < len(data.techs) else 0,
                            'node_name': node.get('Name'), 'node_id': nid,
                            'node_type': 'UnitUpgrade',
                            'json_available': True, 'dat_available': False,
                            'note': f'tech 35 mapping (TTID=35)',
                        })

        # 再处理 direct TTID/NodeID 匹配
        for tid in dat_status['disabled_techs']:
            tname = data.techs[tid].name if tid < len(data.techs) else '?'
            # Research / UniqueTech: Node ID = tech ID
            for node in by_node_id.get(tid, []):
                if node.get('Node Type') not in ('Research', 'UniqueTech'):
                    continue
                ns = node.get('Node Status')
                if ns != 'NotAvailable':
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'dat_disabled_json_enabled',
                        'tech_id': tid, 'tech_name': tname,
                        'tech_sid': data.techs[tid].language_dll_name if tid < len(data.techs) else 0,
                        'node_name': node.get('Name'), 'node_id': tid,
                        'node_type': node['Node Type'],
                        'json_available': True, 'dat_available': False,
                    })
            # UnitUpgrade: Trigger Tech ID = tech ID
            for node in by_trigger_tech_id.get(tid, []):
                if node.get('Node Type') != 'UnitUpgrade':
                    continue
                ns = node.get('Node Status')
                if ns != 'NotAvailable':
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'dat_disabled_json_enabled',
                        'tech_id': tid, 'tech_name': tname,
                        'tech_sid': data.techs[tid].language_dll_name if tid < len(data.techs) else 0,
                        'node_name': node.get('Name'), 'node_id': node.get('Node ID'),
                        'node_type': 'UnitUpgrade',
                        'json_available': True, 'dat_available': False,
                    })

        # ================================================================
        # 正向检查 B: eff_disabled_units → JSON 对应 Unit/Building 应 NotAvailable
        # ================================================================
        for uid in eff_disabled_units:
            for node in by_node_id.get(uid, []):
                if node.get('Node Type') not in UNIT_LIKE_TYPES:
                    continue
                ns = node.get('Node Status')
                if ns != 'NotAvailable':
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'dat_disabled_json_enabled',
                        'tech_id': uid, 'tech_name': f'unit {uid}',
                        'tech_sid': 0,
                        'node_name': node.get('Name'), 'node_id': uid,
                        'node_type': node['Node Type'],
                        'json_available': True, 'dat_available': False,
                    })

        # ================================================================
        # 正向检查 C: dat enabled_tech → JSON TTID=T 节点不应 NotAvailable
        # ================================================================
        for tid in dat_status['enabled_techs']:
            for node in by_trigger_tech_id.get(tid, []):
                ns = node.get('Node Status')
                if ns == 'NotAvailable':
                    tname = tech_effect_cache.get(tid, {}).get('name', '?')
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'json_notavail_dat_enabled',
                        'tech_id': tid, 'tech_name': tname,
                        'tech_sid': data.techs[tid].language_dll_name if tid < len(data.techs) else 0,
                        'node_name': node.get('Name'), 'node_id': node.get('Node ID'),
                        'node_type': node['Node Type'],
                        'json_available': False, 'dat_available': True,
                    })

        # ================================================================
        # 反向检查: JSON NotAvailable 节点 → dat 应有对应 disable
        # ================================================================
        civ_exceptions = EXCEPTIONS.get(civ_file, set())
        for nid, nodes in by_node_id.items():
            for node in nodes:
                if node.get('Node Status') != 'NotAvailable':
                    continue
                ntype = node.get('Node Type')

                if (ntype, nid) in civ_exceptions:
                    continue

                if ntype == 'RegionalUnit':
                    continue

                if ntype in UNIT_LIKE_TYPES:
                    if nid in eff_disabled_units:
                        continue
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'json_notavail_dat_enabled',
                        'tech_id': nid, 'tech_name': f'{ntype} {node.get("Name")}',
                        'tech_sid': 0,
                        'node_name': node.get('Name'), 'node_id': nid,
                        'node_type': ntype,
                        'json_available': False, 'dat_available': True,
                    })

                elif ntype == 'Research':
                    if nid in dat_status['disabled_techs']:
                        continue
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'json_notavail_dat_enabled',
                        'tech_id': nid, 'tech_name': data.techs[nid].name if nid < len(data.techs) else node.get('Name'),
                        'tech_sid': data.techs[nid].language_dll_name if nid < len(data.techs) else 0,
                        'node_name': node.get('Name'), 'node_id': nid,
                        'node_type': 'Research',
                        'json_available': False, 'dat_available': True,
                    })

                elif ntype == 'UnitUpgrade':
                    ttid = node.get('Trigger Tech ID')
                    if ttid is None:
                        continue
                    # 检查 direct TTID 匹配
                    if ttid in dat_status['disabled_techs']:
                        continue
                    # 检查 tech 35 映射：这个 UnitUpgrade 的 Node ID 对应的 real upgrade tech 是否被 disable
                    if ttid == 35 and nid in node_id_to_real_techs:
                        if node_id_to_real_techs[nid] & dat_status['disabled_techs']:
                            continue
                    problems.append({
                        'tt_name': tt_name, 'civ_file': civ_file,
                        'issue': 'json_notavail_dat_enabled',
                        'tech_id': ttid, 'tech_name': data.techs[ttid].name if ttid < len(data.techs) else node.get('Name'),
                        'tech_sid': data.techs[ttid].language_dll_name if ttid < len(data.techs) else 0,
                        'node_name': node.get('Name'), 'node_id': nid,
                        'node_type': ntype,
                        'json_available': False, 'dat_available': True,
                        'note': f'TTID={ttid}',
                    })

    if warnings:
        print(f"\n{'='*60}")
        print(f"WARNINGS ({len(warnings)}):")
        print(f"{'='*60}")
        for w in warnings:
            print(w)

    print(f"\nLoading strings for localized names...")
    zh_strings = load_strings(ZH_STRINGS_FILE)
    en_strings = load_strings(EN_STRINGS_FILE)
    print(f"  zh strings: {len(zh_strings)}, en strings: {len(en_strings)}")

    rows = []
    for p in problems:
        sid = p.get('tech_sid', 0) or 0
        p['tech_en'] = en_strings.get(sid, p.get('tech_name', '?'))
        p['tech_zh'] = zh_strings.get(sid, p.get('tech_name', '?'))
        p['civ_zh'] = civ_names.to_zh(p['tt_name'])
        rows.append(p)

    if not rows and not warnings:
        print("  No problems found!")
        return

    # === English table ===
    print(f"\n{'='*70}")
    print(f"PROBLEMS ({len(rows)})")
    print(f"{'='*70}")
    print(f"| Civ | Tech | In JSON | In Dat |")
    print(f"|-----|------|---------|--------|")
    for r in rows:
        note = f" ({r['note']})" if r.get('note') else ''
        print(f"| {r['tt_name']} | {r['tech_en']}{note} | {'✓' if r['json_available'] else '✗'} | {'✓' if r['dat_available'] else '✗'} |")

    # === Chinese table ===
    print(f"\n{'='*70}")
    print(f"问题 ({len(rows)})")
    print(f"{'='*70}")
    print(f"| 文明 | 科技 | 科技树中可用 | 实际可用 |")
    print(f"|------|------|-------------|-----------|")
    for r in rows:
        note = f" ({r['note']})" if r.get('note') else ''
        print(f"| {r['civ_zh']} | {r['tech_zh']}{note} | {'✓' if r['json_available'] else '✗'} | {'✓' if r['dat_available'] else '✗'} |")


if __name__ == '__main__':
    main()