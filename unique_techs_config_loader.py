import json
import os

from genieutils.datfile import DatFile

import constants
from utils import append_tech

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unique_techs_config.json')


def _get_constant(name: str):
    return getattr(constants, name)


def _resolve_building(building_name: str):
    return _get_constant(building_name)


def _resolve_icon(icon_name: str | None):
    if icon_name is None:
        return None
    return _get_constant(icon_name)


def load_config(path: str = CONFIG_FILE):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_native_mutex_groups() -> list[list[int]]:
    linked_path = os.path.join(constants.GAME_DATA_PATH, 'linkedTechs.json')
    if not os.path.exists(linked_path):
        return []
    with open(linked_path, 'r', encoding='utf-8') as f:
        linked = json.load(f)

    groups: list[list[int]] = []
    for entry in linked.get('LinkedTechs', []):
        if entry.get('Type') != 'MutuallyExclusive':
            continue
        techs = entry.get('Techs', [])
        if len(techs) >= 2:
            groups.append(list(techs))

    return groups


def generate_techs(data: DatFile, params, config=None):
    if config is None:
        config = load_config()

    from unique_techs import get_ut

    native_mutex_groups = _load_native_mutex_groups()

    source_id_to_effect_id: dict[int, int] = {}
    source_id_to_first_tech_id: dict[int, int] = {}
    source_id_to_all_tech_ids: dict[int, list[int]] = {}
    civ_index_to_additional_uts: dict[int, list[int]] = {}

    for section in config['sections']:
        building_id = _resolve_building(section['building'])
        is_castle_section = section['building'] == 'CASTLE_ID'

        for entry in section['techs']:
            source_id = entry['source_id']
            button = entry['button']
            in_castle = entry.get('in_castle', False)
            icon_name = entry.get('icon')
            tech_name = entry['tech_name']
            additional_ut_civ = entry.get('additional_ut')

            share_effect = source_id in source_id_to_effect_id

            tech = get_ut(data, params, source_id, in_castle)
            tech.research_locations[0].location_id = building_id
            tech.research_locations[0].button_id = button
            if icon_name:
                tech.icon_id = _resolve_icon(icon_name)
            tech.name = tech_name

            if share_effect:
                tech.effect_id = source_id_to_effect_id[source_id]

            tech_id = append_tech(data, tech)

            if not share_effect:
                source_id_to_effect_id[source_id] = tech.effect_id
                source_id_to_first_tech_id[source_id] = tech_id
                source_id_to_all_tech_ids[source_id] = [tech_id]
            else:
                source_id_to_all_tech_ids[source_id].append(tech_id)

            if is_castle_section and additional_ut_civ is not None:
                civ_index_to_additional_uts.setdefault(additional_ut_civ, []).append(tech_id)

    return {
        'source_id_to_effect_id': source_id_to_effect_id,
        'source_id_to_first_tech_id': source_id_to_first_tech_id,
        'source_id_to_all_tech_ids': source_id_to_all_tech_ids,
        'civ_index_to_additional_uts': civ_index_to_additional_uts,
        'native_mutex_groups': native_mutex_groups,
    }


def apply_mutex_groups(data: DatFile, result: dict, extra_groups: list[list[int]] | None = None):
    import mutex as _mutex
    from utils import disable_tech

    all_tech_ids_map = result['source_id_to_all_tech_ids']

    all_groups_sids: list[list[int]] = []

    for source_id, tech_ids in all_tech_ids_map.items():
        if len(tech_ids) > 1:
            all_groups_sids.append([source_id])

    for group in result.get('native_mutex_groups', []):
        all_groups_sids.append(group)
    if extra_groups:
        all_groups_sids.extend(extra_groups)

    effect_disable_set: dict[int, set[int]] = {}
    linked_entries: list[list[int]] = []

    for group_sids in all_groups_sids:
        config_sids = [sid for sid in group_sids if sid in all_tech_ids_map]
        if len(config_sids) < 2:
            if len(config_sids) == 1:
                if len(all_tech_ids_map[config_sids[0]]) <= 1:
                    continue
            else:
                continue

        group_techs: list[int] = []
        for sid in config_sids:
            group_techs.extend(all_tech_ids_map[sid])
        linked_entries.append(group_techs)

        group_effects = {data.techs[tid].effect_id for tid in group_techs}

        for eid in group_effects:
            for tid in group_techs:
                effect_disable_set.setdefault(eid, set()).add(tid)

    for eid, targets in effect_disable_set.items():
        for tid in targets:
            disable_tech(data.effects[eid], tid)

    for group_techs in linked_entries:
        _mutex.current_name_id += 1
        tech_names = {data.techs[tid].name for tid in group_techs}
        comment = '/'.join(tech_names)
        entry = {
            "NameId": _mutex.current_name_id,
            "Comment": comment,
            "Type": "MutuallyExclusive",
            "Techs": group_techs,
        }
        _mutex.LINKED_TECHS.setdefault('LinkedTechs', []).append(entry)