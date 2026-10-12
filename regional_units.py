import json
import os

from all_in_1_params import All_In_1_Params
from genieutils.datfile import DatFile

from utils import append_tech
from utils import enable_unit
from utils import force_research_tech
from utils import get_new_effect
from utils import get_new_tech
from utils import replace_require_tech
from utils import set_require_techs

BARRACK_ID = 12
CIV_TECH_TREES_PATH = os.path.join(
    r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat',
    'CivTechTrees',
)

FEUDAL_AGE_TECH = 101
CASTLE_AGE_TECH = 102
IMPERIAL_AGE_TECH = 103
DUPLICATE_IMPERIAL_TECH = 115

HOPLITE_UNIT_IDS = {2110, 2111}
HOPLITE_MAKE_AVAIL_TECH_IDS = {1136}
HOPLITE_UPGRADE_TECH_IDS = {1137}

WAR_CHARIOT_UNIT_IDS = {2150, 2151}
WAR_CHARIOT_MAKE_AVAIL_TECH_IDS = {1169}
WAR_CHARIOT_UPGRADE_TECH_IDS = {1171}


def _age_to_replacement(age_id: int, build_id: int,
                        params: All_In_1_Params) -> int | None:
    barrack = (build_id == BARRACK_ID)
    if age_id == FEUDAL_AGE_TECH:
        return params.early_feudal_tech_id if barrack else params.feudal_duplicate_tech_id
    elif age_id == CASTLE_AGE_TECH:
        return params.early_castle_tech_id if barrack else params.castle_duplicate_tech_id
    elif age_id in (IMPERIAL_AGE_TECH, DUPLICATE_IMPERIAL_TECH):
        return params.early_imp_duplicate_tech_id if barrack else params.imp_duplicate_tech_id
    return None


def _dup_tech_from_orig(orig, dup_name: str, params: All_In_1_Params,
                        unit_build_id: int = -1):
    build_id = unit_build_id
    if build_id == -1 and orig.research_locations:
        build_id = orig.research_locations[0].location_id

    req_ids = [r for r in orig.required_techs if r != -1 and r != 104]

    replaced = []
    for r in req_ids:
        rep = _age_to_replacement(r, build_id, params)
        replaced.append(rep if rep is not None else r)

    if params.switch_tech_id not in replaced:
        replaced.append(params.switch_tech_id)

    dup = get_new_tech(dup_name)
    dup.civ = -1
    set_require_techs(dup, *replaced)
    return dup


def scan_regional_nodes():
    regional_units: dict[int, dict] = {}
    regional_techs: dict[int, dict] = {}

    for fname in sorted(os.listdir(CIV_TECH_TREES_PATH)):
        if not fname.endswith('.json'):
            continue
        with open(os.path.join(CIV_TECH_TREES_PATH, fname), 'r', encoding='utf-8') as f:
            j = json.load(f)
        for arr_name in ('civ_techs_units', 'civ_techs_buildings'):
            for node in j.get(arr_name, []):
                if not isinstance(node, dict):
                    continue
                ntype = node.get('Node Type', '')
                nid = node['Node ID']
                entry = {
                    'name': node['Name'],
                    'age_id': node.get('Age ID'),
                    'build_id': node.get('Building ID'),
                    'link_id': node.get('Link ID'),
                    'trigger_tech_id': node.get('Trigger Tech ID'),
                }
                if ntype == 'RegionalUnit':
                    if nid not in regional_units:
                        regional_units[nid] = entry
                elif ntype == 'RegionalTech':
                    if nid not in regional_techs:
                        regional_techs[nid] = entry

    return regional_units, regional_techs


def scan_dat_make_avail(data: DatFile, regional_unit_ids: set[int]):
    unit_to_make_avail_tech: dict[int, int] = {}
    for i, t in enumerate(data.techs):
        if t.effect_id < 0 or t.effect_id >= len(data.effects):
            continue
        for cmd in data.effects[t.effect_id].effect_commands:
            if cmd.type == 2 and cmd.b == 1 and cmd.a in regional_unit_ids:
                unit_to_make_avail_tech.setdefault(int(cmd.a), i)
    return unit_to_make_avail_tech


def activate_all_regional_units(data: DatFile, params: All_In_1_Params):
    """Global one-shot activation for all regional units and their upgrades."""
    print('Activating regional units...')
    append_tech(data, get_new_tech('Enable regional units'), get_new_effect('Enable regional units effect'))

    regional_units, regional_techs = scan_regional_nodes()
    regional_unit_ids = set(regional_units.keys())
    unit_to_make_avail_tech = scan_dat_make_avail(data, regional_unit_ids)

    make_avail_techs_seen = set()
    upgrade_techs_seen = set()

    # --- Base units ---
    for unit_id, info in sorted(regional_units.items()):
        if unit_id in HOPLITE_UNIT_IDS | WAR_CHARIOT_UNIT_IDS:
            continue
        if info['link_id'] is not None:
            continue

        make_avail_tid = unit_to_make_avail_tech.get(unit_id)
        if make_avail_tid is not None and make_avail_tid not in HOPLITE_MAKE_AVAIL_TECH_IDS | WAR_CHARIOT_MAKE_AVAIL_TECH_IDS:
            if make_avail_tid in make_avail_techs_seen:
                continue
            make_avail_techs_seen.add(make_avail_tid)

            orig = data.techs[make_avail_tid]
            dup = _dup_tech_from_orig(orig, f'Dup {orig.name}', params,
                                      unit_build_id=info.get('build_id', -1))
            effect = get_new_effect(f'Dup {orig.name} effect')
            force_research_tech(effect, make_avail_tid)
            append_tech(data, dup, effect)
        else:
            age_id = info.get('age_id')
            build_id = info.get('build_id', -1)
            if age_id is None or age_id <= 1:
                continue
            dup = get_new_tech(f'Enable {info["name"]}')
            effect = get_new_effect(f'Enable {info["name"]} effect')
            age_tech = FEUDAL_AGE_TECH if age_id == 2 else CASTLE_AGE_TECH if age_id == 3 else IMPERIAL_AGE_TECH
            age_rep = _age_to_replacement(age_tech, build_id, params)
            reqs = []
            if age_rep is not None:
                reqs.append(age_rep)
            reqs.append(params.switch_tech_id)
            set_require_techs(dup, *reqs)
            enable_unit(effect, unit_id)
            append_tech(data, dup, effect)

    # --- Upgrade techs ---
    all_upgrade_orig_ids = set(regional_techs.keys())
    for info in regional_units.values():
        if info['trigger_tech_id'] is not None:
            all_upgrade_orig_ids.add(info['trigger_tech_id'])
    all_upgrade_orig_ids -= HOPLITE_UPGRADE_TECH_IDS | WAR_CHARIOT_UPGRADE_TECH_IDS
    all_upgrade_orig_ids -= HOPLITE_UNIT_IDS | WAR_CHARIOT_UNIT_IDS
    all_upgrade_orig_ids -= make_avail_techs_seen

    for orig_tid in sorted(all_upgrade_orig_ids):
        if orig_tid in upgrade_techs_seen:
            continue
        if orig_tid in make_avail_techs_seen:
            continue
        if orig_tid >= len(data.techs):
            continue
        orig = data.techs[orig_tid]
        if orig.civ != -1:
            continue
        if orig.effect_id < 0 or orig.effect_id >= len(data.effects):
            continue
        upgrade_techs_seen.add(orig_tid)

        reqs = [r for r in orig.required_techs if r != -1 and r != 104]
        set_require_techs(orig, *reqs)

        build_id = orig.research_locations[0].location_id if orig.research_locations else -1
        for age_tid in (101, 102, 103, 115):
            if age_tid in orig.required_techs:
                rep = _age_to_replacement(age_tid, build_id, params)
                if rep is not None:
                    replace_require_tech(orig, age_tid, rep)

    print(f'Regional units activated: {len(make_avail_techs_seen)} make-avail, '
          f'{len(upgrade_techs_seen)} upgrade techs patched')