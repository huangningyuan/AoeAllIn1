import copy
import json
import os
from tkinter.filedialog import SaveAs

from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand
from genieutils.tech import ResearchLocation
from genieutils.unit import TrainLocation

from all_in_1_params import All_In_1_Params
import constants
from constants import (
    CHRONICLE_CIV_IDS,
    ELITE_IBIRAPEMA_TEMP_TECH_ID,
    ELITE_TEMPLE_GUARD_TECH_ID,
    FLEMISH_MILITIA_ID,
    PASTURE_ID,
    PHALANGITE_IDS,
    SETTLEMENT_ID,
    SOUTH_MESO_CIV_IDS,
    TEMPLE_GUARD_IDS,
    ELITE_PHALANGITE_TECH_ID,
)
from ftt import move_tech_button
from ftt import move_unit_button
from unique_techs import get_ut
import utils
from utils import append_tech, set_unit_attribute
from utils import enable_unit
from utils import force_tech
from utils import get_dead_unit
from utils import (
    disable_unit,
    get_civ_name,
    get_new_effect,
    get_tech_id_by_name,
    set_require_techs,
)
from utils import get_new_tech
from utils import research_tech

_UNIT_SWITCH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unit_switch.json')
with open(_UNIT_SWITCH_PATH, 'r', encoding='utf-8') as _f:
    _UNIT_SWITCH_CATEGORIES = json.load(_f)


def _resolve_id(raw_id, params):
    if isinstance(raw_id, int):
        return raw_id
    if isinstance(raw_id, str):
        return params.other_params.get(raw_id)
    return None


def _resolve_ids(raw_ids, params):
    result = []
    for raw_id in raw_ids:
        resolved = _resolve_id(raw_id, params)
        if resolved is not None:
            result.append(resolved)
    return result


def _civ_matches(civ_match, civ_name, civ_id):
    if civ_match is None:
        return False
    if civ_match.get('default', False):
        return False
    if civ_name in civ_match.get('civ_names', []):
        return True
    if civ_id in civ_match.get('civ_ids', []):
        return True
    return False


def _execute_unit_switch(effect, civ_name, civ_id, params):
    for category in _UNIT_SWITCH_CATEGORIES:
        matched_sc = None
        default_sc = None
        for sc in category.get('switch_contents', []):
            if sc.get('civ_match', {}).get('default', False):
                default_sc = sc
            elif _civ_matches(sc.get('civ_match'), civ_name, civ_id):
                matched_sc = sc
                break
        target_sc = matched_sc if matched_sc is not None else default_sc
        if target_sc is None:
            continue

        unit_button_id = category.get('unit_button_id')
        tech_button_id = category.get('tech_button_id')

        all_uids = set()
        all_tids = set()
        for sc in category.get('switch_contents', []):
            all_uids.update(_resolve_ids(sc.get('unit_ids', []), params))
            all_tids.update(_resolve_ids(sc.get('tech_ids', []), params))

        enable_uids = set(_resolve_ids(target_sc.get('unit_ids', []), params))
        enable_tids = set(_resolve_ids(target_sc.get('tech_ids', []), params))

        for uid in (all_uids - enable_uids):
            move_unit_button(effect, uid, -1)
        for tid in (all_tids - enable_tids):
            move_tech_button(effect, tid, -1)
        for uid in enable_uids:
            move_unit_button(effect, uid, unit_button_id)
        for tid in enable_tids:
            move_tech_button(effect, tid, tech_button_id)


def get_next_position(pos: tuple):
    match pos[0]:
        case constants.MULE_CART_ID:
            match pos[1]:
                case 4:
                    return (pos[0], pos[1] + 2)
                case 8:
                    return (pos[0], pos[1] + 2)
                case 24:
                    return (pos[0], pos[1] + 2)
                case 28:
                    return (pos[0], pos[1] + 2)
                case 14:
                    return (pos[0], 21)
                case 34:
                    return (constants.MILL_ID, 2)
                case _:
                    return (pos[0], pos[1] + 1)
        case constants.MILL_ID:
            match pos[1]:
                case 9:
                    return (pos[0], pos[1] + 2)
                case 29:
                    return (pos[0], pos[1] + 2)
                case 3:
                    return (pos[0], pos[1] + 3)
                case 23:
                    return (pos[0], pos[1] + 3)
                case 14:
                    return (pos[0], 21)
                case 34:
                    return (constants.BLACKSMITH_ID, 1)
                case _:
                    return (pos[0], pos[1] + 1)
        case constants.BLACKSMITH_ID:
            match pos[1]:
                case 2:
                    return (pos[0], 4)
                case 5:
                    return (pos[0], 7)
                case 14:
                    return (pos[0], 21)
                case _:
                    return (pos[0], pos[1] + 1)


def add_civ_switch(data: DatFile, params: All_In_1_Params):
    print('Adding civ switches...')
    current_civ_num = len(data.civs)
    # find elite uu tech
    techs = data.techs
    effects = data.effects
    units = data.civs[0].units
    append_tech(data, get_new_tech('----Civ switches----'), get_new_effect('----Civ switches----'))

    uu_tech_id_list: dict[int, int] = dict()
    uu_id_list: dict[int, int] = dict()
    elite_uu_id_list: dict[int, int] = dict()
    uu_unit_ids_by_civ: dict[int, set[int]] = dict()
    for tech_id, tech in enumerate(techs):
        civ_id = tech.civ
        if len(tech.research_locations) == 0:
            continue
        research_location_id = tech.research_locations[0].location_id
        research_button_id = tech.research_locations[0].button_id
        if (research_location_id == constants.CASTLE_ID and research_button_id == 6
                and civ_id in range(1, current_civ_num)):
            uu_tech_id_list[civ_id] = tech_id
        if tech.effect_id == -1 or tech.civ == -1:
            continue
        effect = effects[tech.effect_id]
        if len(effect.effect_commands) == 1:
            command = effect.effect_commands[0]
            if command.type == 2:
                unit = units[command.a]
                train_location = unit.creatable.train_locations[0]
                if train_location.unit_id == constants.CASTLE_ID and train_location.button_id == 1:
                    uu_id_list[civ_id] = command.a
                    uu_unit_ids_by_civ.setdefault(civ_id, set()).add(command.a)
    for effect in effects:
        for command in effect.effect_commands:
            if command.type != 3:
                continue
            for civ_id, known_uu_ids in uu_unit_ids_by_civ.items():
                if command.a in known_uu_ids:
                    elite_uu_id_list[civ_id] = command.b

    but_id = 1380
    effect = effects[but_id]
    but_uu_id_list = list[int]()
    for command in effect.effect_commands:
        if command.type == 15:
            but_uu_id_list.append(command.a)
    for civ_id in range(1, current_civ_num):
        if civ_id not in uu_id_list:
            print(f'Failed to find uu for civ {civ_id}')
            exit(1)
        if uu_id_list[civ_id] not in but_uu_id_list:
            effect.effect_commands.append(EffectCommand(15, uu_id_list[civ_id], -1, 100, 0.85))
            if civ_id in elite_uu_id_list and elite_uu_id_list[civ_id] not in but_uu_id_list:
                effect.effect_commands.append(EffectCommand(15, elite_uu_id_list[civ_id], -1, 100, 0.85))
        

    print(uu_id_list)
    additional_ut_ids: dict[int, list[int]] = {
        civ_id: list(tech_ids)
        for civ_id, tech_ids in params.civ_index_to_additional_uts.items()
    }

    # huskarl
    tech = techs[365]
    new_location = ResearchLocation(constants.BARRACK_ID, tech.research_locations[0].research_time, 29, -1)
    tech.research_locations.append(new_location)

    # tarkan
    tech = techs[2]
    new_location = ResearchLocation(constants.STABLE_ID, tech.research_locations[0].research_time, 26, -1)
    tech.research_locations.append(new_location)

    name = 'enable all uus'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
    effect = get_new_effect(name)
    for civ_id in range(1, current_civ_num):
        enable_unit(effect, uu_id_list[civ_id])
    append_tech(data, tech, effect)

    civ_switch_unit_offset_id = len(units) - 1
    civ_switch_tech_offset_id = len(techs) - 1
    for civ_id in range(1, current_civ_num):
        civ_name = get_civ_name(data.civs, civ_id)
        name = 'switch to ' + civ_name
        tech = get_new_tech(name)
        tech.required_tech_count = 1
        effect = get_new_effect(name)
        for j in range(1, current_civ_num):
            if j == civ_id:
                disable_unit(effect, civ_switch_unit_offset_id + j)
                move_unit_button(effect, uu_id_list[j], 1)
                move_tech_button(effect, uu_tech_id_list[j], 6, 0)
                for aid in additional_ut_ids.get(j, []):
                    move_tech_button(effect, aid, 6, 0)
            else:
                enable_unit(effect, civ_switch_unit_offset_id + j)
                move_unit_button(effect, uu_id_list[j], -1)
                move_tech_button(effect, uu_tech_id_list[j], -1, 0)
                for aid in additional_ut_ids.get(j, []):
                    move_tech_button(effect, aid, -1, 0)
        _execute_unit_switch(effect, civ_name, civ_id, params)
        append_tech(data, tech, effect)

        if civ_name == 'Sicilians':
            move_unit_button(effect, 1659, 1)
        else:
            move_unit_button(effect, 1659, -1)
        if civ_name == 'Bulgarians':
            move_unit_button(effect, 1227, 1)
        else:
            move_unit_button(effect, 1227, -1)

        if civ_name == 'Huns':
            move_unit_button(effect, 886, 1)
            move_unit_button(effect, 887, 1)
        else:
            move_unit_button(effect, 886, -1)
            move_unit_button(effect, 887, -1)

        if civ_name == 'Goths':
            move_unit_button(effect, 759, 1)
            move_unit_button(effect, 761, 1)
        else:
            move_unit_button(effect, 759, -1)
            move_unit_button(effect, 761, -1)


    lfc_offset = 6800
    lfh_offset = 105800
    for civ in data.civs:
        pos = (constants.MULE_CART_ID, 1)
        for civ_id in range(1, current_civ_num):
            unit = get_dead_unit(units, )
            unit.icon_id = units[elite_uu_id_list[civ_id]].icon_id
            unit.creatable.train_locations.append(TrainLocation(0, pos[0], pos[1], -1))
            unit.building.tech_id = civ_switch_tech_offset_id + civ_id
            unit.name = 'switch to ' + get_civ_name(data.civs, civ_id)
            unit.id = civ_id + civ_switch_unit_offset_id
            unit.base_id = civ_id + civ_switch_unit_offset_id
            unit.copy_id = civ_id + civ_switch_unit_offset_id
            unit.language_dll_creation = lfc_offset + civ_id
            unit.language_dll_help = lfh_offset + civ_id
            civ.units.append(unit)
            pos = get_next_position(pos)

    name = 'disable civ switch'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for civ_id in range(civ_switch_unit_offset_id, civ_switch_unit_offset_id + current_civ_num - 1):
        disable_unit(effect, civ_id)
    append_tech(data, tech, effect)

    for civ_id in range(1, current_civ_num):
        name = 'initialize civ switch ' + get_civ_name(data.civs, civ_id)
        tech = get_new_tech(name)
        tech.civ = civ_id
        set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
        effect = get_new_effect(name)
        force_tech(effect, civ_switch_tech_offset_id + civ_id)
        research_tech(effect, civ_switch_tech_offset_id + civ_id)
        append_tech(data, tech, effect)

    name = 'enable elite uu tech'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 266)
    effect = get_new_effect(name)
    for civ_id in range(1, current_civ_num):
        force_tech(effect, uu_tech_id_list[civ_id])
    append_tech(data, tech, effect)
    print('Civ switches added.')


if __name__ == '__main__':
    mod_path = utils.get_mod_path('All Civ Bonus Description')
    en_file_name = os.path.join(mod_path, 'resources', 'en', 'strings', 'key-value', 'key-value-modded-strings-utf8.txt')
    zh_file_name = os.path.join(mod_path, 'resources', 'zh', 'strings', 'key-value', 'key-value-modded-strings-utf8.txt')
    offset = 26800
    civ_en_zh_dict = {
        'Britons': '不列颠', 'Franks': '法兰克', 'Goths': '哥特', 'Teutons': '条顿',
        'Japanese': '日本', 'Chinese': '中国', 'Byzantines': '拜占庭', 'Persians': '波斯',
        'Saracens': '萨拉森', 'Turks': '土耳其', 'Vikings': '维京', 'Mongols': '蒙古',
        'Celts': '凯尔特', 'Spanish': '西班牙', 'Aztecs': '阿兹特克', 'Mayans': '玛雅',
        'Huns': '匈奴', 'Koreans': '朝鲜', 'Italians': '意大利', 'Hindustanis': '印度斯坦',
        'Incas': '印加', 'Magyars': '马扎尔', 'Slavs': '斯拉夫', 'Portuguese': '葡萄牙',
        'Ethiopians': '埃塞俄比亚', 'Malians': '马里', 'Berbers': '柏柏尔', 'Khmer': '高棉',
        'Malay': '马来', 'Burmese': '缅甸', 'Vietnamese': '越南', 'Bulgarians': '保加利亚',
        'Tatars': '鞑靼', 'Cumans': '库曼', 'Lithuanians': '立陶宛', 'Burgundians': '勃艮第',
        'Sicilians': '西西里', 'Poles': '波兰', 'Bohemians': '波西米亚', 'Dravidians': '达罗毗荼',
        'Bengalis': '孟加拉', 'Gurjaras': '瞿折罗', 'Romans': '罗马', 'Armenians': '亚美尼亚',
        'Georgians': '格鲁吉亚', 'Achaemenids': '阿契美尼德', 'Athenians': '雅典',
        'Spartans': '斯巴达', 'Wei': '魏', 'Shu': '蜀', 'Wu': '吴', 'Jurchens': '女真',
        'Khitans': '契丹', 'Puru': '普鲁', 'Thracians': '色雷斯', 'Macedonians': '马其顿',
        'Muisca': '穆伊斯卡', 'Mapuche': '马普切', 'Tupi': '图皮',
        'Saxons': '撒克逊', 'Danes': '丹麦', 'Varangians': '瓦良吉',
    }
    en = open(en_file_name, 'w')
    zh = open(zh_file_name, 'w', encoding='utf-8')
    en.write('26800 "enable all civ bonus"\n')
    zh.write('26800 "启用所有文明加成"\n')
    mod_path = utils.get_mod_path()
    file_name = os.path.join(mod_path, 'resources', '_common', 'dat', 'empires2_x2_p1.dat')
    data = DatFile.parse(file_name)
    civs = data.civs
    for i in range(1, len(civs)):
        civ_name = get_civ_name(civs, i)
        en.write('%d "switch to %s"\n' % (offset + i, civ_name))
        zh.write('%d "切换到%s"\n' % (offset + i, civ_en_zh_dict[civ_name]))

    en.close()
    zh.close()