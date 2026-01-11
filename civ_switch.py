import copy
import os
from tkinter.filedialog import SaveAs

from genieutils.datfile import DatFile
from genieutils.tech import ResearchLocation
from genieutils.unit import TrainLocation

import constants
from all_in_1_params import All_In_1_Params
from constants import CHRONICLE_CIV_IDS
from ftt import move_tech_button
from ftt import move_unit_button
from unique_techs import get_ut
import utils
from utils import append_tech, set_unit_attribute
from utils import enable_unit
from utils import force_tech
from utils import get_dead_unit
from utils import get_new_effect, get_tech_id_by_name, set_require_techs, get_civ_name, disable_unit
from utils import get_new_tech
from utils import research_tech


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

    uu_tech_id_list = dict()
    uu_id_list = dict()
    for civ_id, tech in enumerate(techs):
        research_location_id = tech.research_locations[0].location_id
        research_button_id = tech.research_locations[0].button_id
        if (research_location_id == constants.CASTLE_NUM and research_button_id == 6
                and tech.civ in range(1, current_civ_num)):
            uu_tech_id_list[tech.civ] = civ_id
            # for command in data.effects[tech.effect_id].effect_commands:
            #     if constants.CASTLE_NUM in list(map(lambda x: x.unit_id, units[command.a].creatable.train_locations)):
            #         uu_id_list[tech.civ] = command.a
            #         break
        if tech.effect_id == -1 or tech.civ == -1:
            continue
        effect = effects[tech.effect_id]
        if len(effect.effect_commands) == 1:
            command = effect.effect_commands[0]
            if command.type == 2:
                unit = units[command.a]
                train_location = unit.creatable.train_locations[0]
                if train_location.unit_id == constants.CASTLE_NUM and train_location.button_id == 1:
                    uu_id_list[tech.civ] = unit.id
    for civ_id in range(1, current_civ_num):
        if civ_id not in uu_id_list:
            print(f'Failed to find uu for civ {civ_id}')
            exit(1)

    print(uu_id_list)
    additional_ut_ids = dict()
    name = 'Force uu uts castle'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
    effect = get_new_effect(name)
    # franks
    tech_id = 83
    force_tech(effect, tech_id)
    move_tech_button(effect, tech_id, -1)
    additional_ut_ids[2] = tech_id
    # Athenians
    tech_id = params.ut_in_castle_with_mutex_list['Taxiarchs']
    force_tech(effect, tech_id)
    move_tech_button(effect, tech_id, -1)
    additional_ut_ids[47] = tech_id
    # Shu
    tech_id = params.ut_in_castle_with_mutex_list['Coiled Serpent Array']
    force_tech(effect, tech_id)
    move_tech_button(effect, tech_id, -1)
    additional_ut_ids[49] = tech_id
    # Wu
    tech_id = params.ut_in_castle_with_mutex_list['Red Cliffs Tactics']
    force_tech(effect, tech_id)
    move_tech_button(effect, tech_id, -1)
    additional_ut_ids[50] = tech_id
    append_tech(data, tech, effect)

    name = 'Force uu uts imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    # byz
    tech_id = 61
    force_tech(effect, tech_id)
    move_tech_button(effect, tech_id, -1)
    additional_ut_ids[7] = tech_id
    append_tech(data, tech, effect)

    # Corvinian Army
    name = 'Corvinian Army'
    tech = get_ut(data, params, 514, True)
    tech.research_locations[0].button_id = 0
    effect = get_new_effect(name)
    food = 35 * 0.8
    gold = 45 * 0.8
    set_unit_attribute(effect, 869, -1, 105, 0)
    set_unit_attribute(effect, 871, -1, 105, 0)
    set_unit_attribute(effect, 869, -1, 103, food + gold)
    set_unit_attribute(effect, 871, -1, 103, food + gold)
    cov_tech_id, effect_id = append_tech(data, tech, effect)
    additional_ut_ids[22] = cov_tech_id
    name = 'Corvinian Army Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, cov_tech_id)
    effect = get_new_effect(name)
    food = 35 * 0.75
    set_unit_attribute(effect, 869, -1, 105, 0)
    set_unit_attribute(effect, 871, -1, 105, 0)
    set_unit_attribute(effect, 869, -1, 103, food + gold)
    set_unit_attribute(effect, 871, -1, 103, food + gold)
    append_tech(data, tech, effect)
    name = 'Corvinian Army + Kshatriyas'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, get_tech_id_by_name(data, 'Kshatriyas Castle Militia'), cov_tech_id)
    effect = get_new_effect(name)
    food = 35 * 0.75 * 0.8
    set_unit_attribute(effect, 869, -1, 105, 0)
    set_unit_attribute(effect, 871, -1, 105, 0)
    set_unit_attribute(effect, 869, -1, 103, food + gold)
    set_unit_attribute(effect, 871, -1, 103, food + gold)
    append_tech(data, tech, effect)
    name = 'Corvinian Army + Kshatriyas Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, get_tech_id_by_name(data, 'Kshatriyas Imp Militia'), cov_tech_id)
    effect = get_new_effect(name)
    food = 35 * 0.75 * 0.75
    set_unit_attribute(effect, 869, -1, 105, 0)
    set_unit_attribute(effect, 871, -1, 105, 0)
    set_unit_attribute(effect, 869, -1, 103, food + gold)
    set_unit_attribute(effect, 871, -1, 103, food + gold)
    append_tech(data, tech, effect)

    additional_ut_ids[28] = params.ut_in_castle_with_mutex_list['Double Crossbow']
    additional_ut_ids[43] = params.ut_in_castle_with_mutex_list['Comitatenses']
    additional_ut_ids[21] = params.ut_in_castle_with_mutex_list['Fabric Shields']
    additional_ut_ids[41] = params.ut_in_castle_with_mutex_list['Paiks']
    additional_ut_ids[25] = params.ut_in_castle_with_mutex_list['Royal Heirs']
    additional_ut_ids[27] = params.ut_in_castle_with_mutex_list['Maghrebi Camels']
    additional_ut_ids[39] = params.ut_in_castle_with_mutex_list['Wagenburg Tactics']
    additional_ut_ids[46] = params.ut_in_castle_with_mutex_list['Sparabaras']
    additional_ut_ids[49] = params.ut_in_castle_with_mutex_list['Coiled Serpent Array']
    additional_ut_ids[50] = params.ut_in_castle_with_mutex_list['Red Cliffs Tactics']
    additional_ut_ids[54] = params.ut_in_castle_with_mutex_list['Sarissophoroi']
    additional_ut_ids[55] = params.ut_in_castle_with_mutex_list['Bessian Metalworking']
    additional_ut_ids[56] = params.ut_in_castle_with_mutex_list['Leaf-Headed Shafts']

    # huskarl
    tech = techs[365]
    new_location = ResearchLocation(constants.BARRACK_NUM, tech.research_locations[0].research_time, 0, -1)
    tech.research_locations.append(new_location)
    move_tech_button(effects[462], 365, 29, 1)

    # tarkan
    tech = techs[2]
    new_location = ResearchLocation(constants.STABLE_NUM, tech.research_locations[0].research_time, 0, -1)
    tech.research_locations.append(new_location)
    move_tech_button(effects[538], 2, 26, 1)

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
                # enable_unit(effect, uu_id_list[j])
                move_unit_button(effect, uu_id_list[j], 1)
                move_tech_button(effect, uu_tech_id_list[j], 6, 0)
                if j in additional_ut_ids.keys():
                    move_tech_button(effect, additional_ut_ids[j], 6, 0)
            else:
                enable_unit(effect, civ_switch_unit_offset_id + j)
                # disable_unit(effect, uu_id_list[j])
                move_unit_button(effect, uu_id_list[j], -1)
                move_tech_button(effect, uu_tech_id_list[j], -1, 0)
                if j in additional_ut_ids.keys():
                    move_tech_button(effect, additional_ut_ids[j], -1, 0)
        # dromon
        if civ_name in ('Huns', 'Byzantines', 'Armenians', 'Romans', 'Goths'):
            move_unit_button(effect, constants.DROMON_ID, 23)
            move_unit_button(effect, constants.CANNON_GALLEON_ID, -1)
            move_unit_button(effect, constants.E_CANNON_GALLEON_ID, -1)
            move_unit_button(effect, constants.LOU_CHUAN_ID, -1)
            move_tech_button(effect, params.other_params.get('bm_dock_id'), -1)
            move_tech_button(effect, params.other_params.get('sit_t_dock_id'), -1)
            move_tech_button(effect, params.other_params.get('tb_dock_id'), -1)
            move_tech_button(effect, params.other_params.get('roc_dock_id'), -1)
        # lou chuan
        elif civ_name in ('Wei', 'Shu', 'Wu', 'Chinese', 'Jurchens'):
            move_unit_button(effect, constants.LOU_CHUAN_ID, 23)
            move_tech_button(effect, params.other_params.get('bm_dock_id'), 28)
            move_tech_button(effect, params.other_params.get('sit_t_dock_id'), 28)
            move_tech_button(effect, params.other_params.get('tb_dock_id'), 28)
            move_tech_button(effect, params.other_params.get('roc_dock_id'), 28)
            move_unit_button(effect, constants.CANNON_GALLEON_ID, -1)
            move_unit_button(effect, constants.E_CANNON_GALLEON_ID, -1)
            move_unit_button(effect, constants.DROMON_ID, -1)
        # cannon galleon
        else:
            move_unit_button(effect, constants.DROMON_ID, -1)
            move_unit_button(effect, constants.CANNON_GALLEON_ID, 23)
            move_unit_button(effect, constants.E_CANNON_GALLEON_ID, 23)
            move_unit_button(effect, constants.LOU_CHUAN_ID, -1)
            move_tech_button(effect, params.other_params.get('bm_dock_id'), -1)
            move_tech_button(effect, params.other_params.get('sit_t_dock_id'), -1)
            move_tech_button(effect, params.other_params.get('tb_dock_id'), -1)
            move_tech_button(effect, params.other_params.get('roc_dock_id'), -1)

        bog_dock_id = params.other_params['bog_dock_id']
        # e turtle
        if civ_name == 'Koreans':
            move_tech_button(effect, constants.E_TURTLE_TECH_ID, 29)
            move_tech_button(effect, params.other_params['shin_dock_id'], 29)
            move_tech_button(effect, constants.E_CARAVEL_TECH_ID, -1)
            move_tech_button(effect, constants.E_LONGBOAT_TECH_ID, -1)
            move_tech_button(effect, bog_dock_id, -1)
        # caravel
        elif civ_name == 'Portuguese':
            move_tech_button(effect, constants.E_TURTLE_TECH_ID, -1)
            move_tech_button(effect, params.other_params['shin_dock_id'], -1)
            move_tech_button(effect, constants.E_CARAVEL_TECH_ID, 29)
            move_tech_button(effect, constants.E_LONGBOAT_TECH_ID, -1)
            move_tech_button(effect, bog_dock_id, -1)
        # longboat
        elif civ_name == 'Vikings':
            move_tech_button(effect, constants.E_TURTLE_TECH_ID, -1)
            move_tech_button(effect, params.other_params['shin_dock_id'], -1)
            move_tech_button(effect, constants.E_CARAVEL_TECH_ID, -1)
            move_tech_button(effect, constants.E_LONGBOAT_TECH_ID, 29)
            move_tech_button(effect, bog_dock_id, 29)
        # krepost
        if civ_name == 'Bulgarians':
            move_unit_button(effect, constants.KREPOST_ID, 5)
            move_unit_button(effect, constants.DONJON_ID, -1)
            move_unit_button(effect, constants.SHIPYARD_ID, -1)
        # donjon
        elif civ_name == 'Sicilians':
            move_unit_button(effect, constants.KREPOST_ID, -1)
            move_unit_button(effect, constants.DONJON_ID, 5)
            move_unit_button(effect, constants.SHIPYARD_ID, 5)
        # shipyard
        elif civ_id in constants.CHRONICLE_CIV_IDS:
            move_unit_button(effect, constants.KREPOST_ID, -1)
            move_unit_button(effect, constants.DONJON_ID, -1)
            move_unit_button(effect, constants.SHIPYARD_ID, 5)
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
        if civ_name == 'Sicilians':
            move_unit_button(effect, 1659, 1)
        else:
            move_unit_button(effect, 1659, -1)
        if civ_name == 'Bulgarians':
            move_unit_button(effect, 1227, 1)
        else:
            move_unit_button(effect, 1227, -1)
        HEI_GUANG_ID = [1944, 1946]
        HEAVY_HEI_GUANG_TECH_ID = 1033
        KNIGHT_ID = [38, 283]
        CAVALIER_TECH_ID = 209
        PALADIN_ID = 569
        PALADIN_TECH_ID = 265
        SAVAR_ID = 1813
        SAVAR_TECH_ID = 526
        XOLOTL_ID = 1570
        # hei guang
        if civ_name in ('Wei', 'Shu', 'Wu'):
            for i in HEI_GUANG_ID:
                move_unit_button(effect, i, 2)
            move_tech_button(effect, HEAVY_HEI_GUANG_TECH_ID, 7)
            for i in KNIGHT_ID:
                move_unit_button(effect, i, -1)
            move_tech_button(effect, CAVALIER_TECH_ID, -1)
            move_unit_button(effect, PALADIN_ID, -1)
            move_tech_button(effect, PALADIN_TECH_ID, -1)
            move_unit_button(effect, SAVAR_ID, -1)
            move_tech_button(effect, SAVAR_TECH_ID, -1)
            move_unit_button(effect, XOLOTL_ID, -1)
        elif civ_name == 'Persians':
            for i in HEI_GUANG_ID:
                move_unit_button(effect, i, -1)
            move_tech_button(effect, HEAVY_HEI_GUANG_TECH_ID, -1)
            move_unit_button(effect, PALADIN_ID, -1)
            move_tech_button(effect, PALADIN_TECH_ID, -1)
            for i in KNIGHT_ID:
                move_unit_button(effect, i, 2)
            move_tech_button(effect, CAVALIER_TECH_ID, 7)
            move_unit_button(effect, SAVAR_ID, 2)
            move_tech_button(effect, SAVAR_TECH_ID, 7)
            move_unit_button(effect, XOLOTL_ID, -1)
        elif civ_name in ('Aztecs', 'Mayans', 'Incas'):
            for i in HEI_GUANG_ID:
                move_unit_button(effect, i, -1)
            move_tech_button(effect, HEAVY_HEI_GUANG_TECH_ID, -1)
            for i in KNIGHT_ID:
                move_unit_button(effect, i, -1)
            move_tech_button(effect, CAVALIER_TECH_ID, -1)
            move_unit_button(effect, PALADIN_ID, -1)
            move_tech_button(effect, PALADIN_TECH_ID, -1)
            move_unit_button(effect, SAVAR_ID, -1)
            move_tech_button(effect, SAVAR_TECH_ID, -1)
            move_unit_button(effect, XOLOTL_ID, 2)
        else:
            for i in HEI_GUANG_ID:
                move_unit_button(effect, i, -1)
            move_tech_button(effect, HEAVY_HEI_GUANG_TECH_ID, -1)
            move_unit_button(effect, SAVAR_ID, -1)
            move_tech_button(effect, SAVAR_TECH_ID, -1)
            for i in KNIGHT_ID:
                move_unit_button(effect, i, 2)
            move_tech_button(effect, CAVALIER_TECH_ID, 7)
            move_unit_button(effect, PALADIN_ID, 2)
            move_tech_button(effect, PALADIN_TECH_ID, 7)
            move_unit_button(effect, XOLOTL_ID, -1)
        if civ_name == 'Khitans':
            move_unit_button(effect, 1889, 1)
            for i in constants.PORT_IDS:
                move_unit_button(effect, i, -1)
        elif civ_id in CHRONICLE_CIV_IDS:
            move_unit_button(effect, 1889, -1)
            for i in constants.PORT_IDS:
                move_unit_button(effect, i, 1)

        append_tech(data, tech, effect)
    lfc_offset = 6800
    lfh_offset = 105800
    for civ in data.civs:
        pos = (constants.MULE_CART_ID, 1)
        for civ_id in range(1, current_civ_num):
            unit = get_dead_unit(units, )
            unit.icon_id = units[uu_id_list[civ_id]].icon_id
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
    civ_en_zh_dict = {'Britons': '不列颠', 'Franks': '法兰克', 'Goths': '哥特', 'Teutons': '条顿', 'Japanese': '日本',
                      'Chinese': '中国', 'Byzantines': '拜占庭', 'Persians': '波斯', 'Saracens': '萨拉森',
                      'Turks': '土耳其', 'Vikings': '维京', 'Mongols': '蒙古', 'Celts': '凯尔特', 'Spanish': '西班牙',
                      'Aztecs': '阿兹特克', 'Mayans': '玛雅', 'Huns': '匈人', 'Koreans': '高丽', 'Italians': '意大利',
                      'Hindustanis': '印度斯坦', 'Incas': '印加', 'Magyars': '马扎尔', 'Slavs': '斯拉夫',
                      'Portuguese': '葡萄牙', 'Ethiopians': '埃塞俄比亚', 'Malians': '马里', 'Berbers': '柏柏尔',
                      'Khmer': '高棉', 'Malay': '马来', 'Burmese': '缅甸', 'Vietnamese': '越南',
                      'Bulgarians': '保加利亚', 'Tatars': '鞑靼', 'Cumans': '库曼', 'Lithuanians': '立陶宛',
                      'Burgundians': '勃艮第', 'Sicilians': '西西里', 'Poles': '波兰', 'Bohemians': '波西米亚',
                      'Dravidians': '达罗毗荼', 'Bengalis': '孟加拉', 'Gurjaras': '瞿折罗', 'Romans': '罗马',
                      'Armenians': '亚美尼亚', 'Georgians': '格鲁吉亚', 'Achaemenids': '阿契美尼德',
                      'Athenians': '雅典', 'Spartans': '斯巴达', 'Wei': '魏', 'Shu': '蜀', 'Wu': '吴',
                      'Jurchens': '女真', 'Khitans': '契丹', 'Puru': '普鲁', 'Thracians': '色雷斯', 'Macedonians': '马其顿'}
    en = open(en_file_name, 'w')
    zh = open(zh_file_name, 'w', encoding='utf-8')
    en.write('26800 "enable all civ bonus"\n')
    zh.write('26800 "激活全文明特性"\n')
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
