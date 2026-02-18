import copy

from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand

import constants
from all_in_1_params import All_In_1_Params
from constants import ITALIANS_TECH_DISCOUNT, CHRONICLE_CIV_IDS
from custom_civ_bonus import deal_custom_bonus
from deal_requirement import deal_tech_requrirement
from ftt import move_unit_button, move_tech_button
from utils import disable_tech, get_new_unit, get_civ_name, set_require_techs, set_tech_cost, \
    set_unit_attribute, set_resource, append_tech, force_research_tech, set_tech_time, set_tech_discount
from utils import enable_tech
from utils import enable_unit
from utils import force_tech
from utils import get_new_effect
from utils import get_new_tech
from utils import replace_tuple
from utils import research_tech

TECH_TO_REMOVE = [70, 95, 223, 224, 225, 226, 227, 228, 259, 260, 261, 286, 287, 323, 324, 326, 354, 399, 431, 466, 500,
                  609, 641, 649, 664, 699, 700, 701, 702, 788, 789, 792, 809, 810, 811, 806, 807, 808, 856, 957,
                  510, 721, 731, 732, 733, 288, 388, 323, 324, 326, 299, 303, 305, 310, 449, 867, 868, 1071,
                  869, 241, 242, 1134, 1114, 1124, 1136, 1169, 1103, 354, 1077, 1079, 1058, 1059, 995, 1067, 1004, 355,
                  1397]


def filter_vietnam_bonus(effect_command: EffectCommand):
    match effect_command.type:
        case 103:
            if effect_command.a in (65, 315):
                return True
            else:
                return False
        case _:
            return True

def filter_dravadian_bonus(effect_command: EffectCommand):
    match effect_command.type:
        case 101:
            return False
        case _:
            return True


def add_civ_bonuses(data: DatFile, params: All_In_1_Params):
    print('Adding civ bonuses...')
    techs = data.techs
    effects = data.effects
    civs = data.civs
    current_civ_num = len(civs)

    civ_tech_tree_tech_num = dict()
    civ_tb_tech_num = dict()
    all_team_bonus_effect_commands = list()
    for i, effect in enumerate(effects):
        if effect.name.endswith('Tech Tree'):
            civ_name = effect.name[0: -10]
            civ_tech_tree_tech_num[civ_name] = i
        if effect.name.endswith('Team Bonus'):
            civ_name = effect.name[0:-11]
            civ_tb_tech_num[civ_name] = i
            all_team_bonus_effect_commands += effect.effect_commands

    name = 'All Team Bonus'
    tech = get_new_tech()
    tech.name = name
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect()
    effect.effect_commands = all_team_bonus_effect_commands
    effect.name = name
    append_tech(data, tech, effect)

    civ_bonus_ids = list()
    civ_feudal_bonus_ids = list()
    civ_castle_bonus_ids = list()
    civ_imp_bonus_ids = list()
    civ_custom_bonus_ids = list()
    civ_ut_ids = list()
    for i in range(len(civs) + 1):
        civ_bonus_ids.append(list())
        civ_feudal_bonus_ids.append(list())
        civ_castle_bonus_ids.append(list())
        civ_imp_bonus_ids.append(list())
        civ_custom_bonus_ids.append(list())
        civ_ut_ids.append(list())
    for i, tech in enumerate(techs):
        if tech.civ == -1:
            continue
        if tech.effect_id == -1:
            continue
        research_location = tech.research_locations[0]
        if research_location.location_id == constants.CASTLE_NUM and (
                research_location.button_id in (7, 8) or (research_location.button_id in (12, 13) and tech.civ in constants.CHRONICLE_CIV_IDS)):
            civ_ut_ids[tech.civ].append(i)
            continue
        if research_location.location_id >= 0:
            continue
        if research_location.research_time > 0:
            continue
        if tech.name.endswith('(make avail)'):
            continue
        if tech.name.find('post-imp') > -1:
            continue
        if i in TECH_TO_REMOVE:
            continue
        tech_required_tech_count = tech.required_tech_count
        required_techs = tech.required_techs
        if tech_required_tech_count == 0:
            civ_bonus_ids[tech.civ].append(i)
        elif tech_required_tech_count == 1:
            match required_techs[0]:
                case 101:
                    civ_feudal_bonus_ids[tech.civ].append(i)
                case 102:
                    civ_castle_bonus_ids[tech.civ].append(i)
                case 103:
                    civ_imp_bonus_ids[tech.civ].append(i)
                case 104:
                    civ_bonus_ids[tech.civ].append(i)
                case _:
                    civ_custom_bonus_ids[tech.civ].append(i)
        else:
            civ_custom_bonus_ids[tech.civ].append(i)

    all_in_1_civ_bonus_tech_ids = dict()
    all_in_1_civ_imp_bonus_tech_ids = dict()
    all_in_1_civ_feudal_bonus_tech_ids = dict()
    all_in_1_civ_castle_bonus_tech_ids = dict()
    all_in_1_reverse_tech_ids = dict()
    for i in range(1, current_civ_num):
        civ_name = get_civ_name(civs, i)
        tech = get_new_tech('----' + civ_name + '----')
        effect = get_new_effect('----' + civ_name + '----')
        append_tech(data, tech, effect)

        reverse_name = 'Reverse ' + civ_name
        reverse_effect = get_new_effect(reverse_name)
        tech_tree_effect = effects[civ_tech_tree_tech_num[civ_name]]
        tech_tree_bonus_effect_commands = list()
        for effect_command in tech_tree_effect.effect_commands:
            if effect_command.type == 102:
                if effect_command.d != 15.0:  # guilds
                    enable_tech(reverse_effect, int(effect_command.d))
            elif effect_command.type == 101:
                if effect_command.c == 1:  # tech discount
                    continue
                else:
                    tech_tree_bonus_effect_commands.append(effect_command)
            else:
                tech_tree_bonus_effect_commands.append(effect_command)

        tech = get_new_tech(reverse_name)
        set_require_techs(tech, params.switch_tech_id)
        tech.civ = i
        tech_id, effect_id = append_tech(data, tech, reverse_effect)
        all_in_1_reverse_tech_ids[civ_name] = tech_id

        bonus_ids = civ_bonus_ids[i]
        if len(bonus_ids) > 0 or len(tech_tree_bonus_effect_commands) > 0:
            name = civ_name + " Bonus"
            effect = get_new_effect(name)
            effect.effect_commands = tech_tree_bonus_effect_commands
            for bonus_id in bonus_ids:
                force_research_tech(effect, bonus_id)

            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            tech.civ = -1

            tech_id, effect_id = append_tech(data, tech, effect)
            disable_tech(reverse_effect, tech_id)
            all_in_1_civ_bonus_tech_ids[civ_name] = tech_id

        bonus_ids = civ_feudal_bonus_ids[i]
        if len(bonus_ids) > 0:
            name = civ_name + " Feudal Bonus"
            effect = get_new_effect(name)
            for bonus_id in bonus_ids:
                research_tech(effect, bonus_id)

            tech = get_new_tech(name)
            set_require_techs(tech, params.feudal_duplicate_tech_id, params.switch_tech_id)
            tech.civ = -1

            tech_id, effect_id = append_tech(data, tech, effect)
            disable_tech(reverse_effect, tech_id)
            all_in_1_civ_feudal_bonus_tech_ids[civ_name] = tech_id

        bonus_ids = civ_castle_bonus_ids[i]
        if len(bonus_ids) > 0:
            name = civ_name + " Castle Bonus"
            effect = get_new_effect(name)
            for bonus_id in bonus_ids:
                research_tech(effect, bonus_id)

            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            tech.civ = -1

            tech_id, effect_id = append_tech(data, tech, effect)
            disable_tech(reverse_effect, tech_id)
            all_in_1_civ_castle_bonus_tech_ids[civ_name] = tech_id

        bonus_ids = civ_imp_bonus_ids[i]
        if len(bonus_ids) > 0:
            name = civ_name + " Imp Bonus"
            effect = get_new_effect(name)
            for bonus_id in bonus_ids:
                research_tech(effect, bonus_id)

            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            tech.civ = -1

            tech_id, effect_id = append_tech(data, tech, effect)
            disable_tech(reverse_effect, tech_id)
            all_in_1_civ_imp_bonus_tech_ids[civ_name] = tech_id

        bonus_ids = civ_custom_bonus_ids[i]
        if len(bonus_ids) > 0:
            for tech_id in bonus_ids:
                tech = copy.deepcopy(techs[tech_id])
                tech.name = tech.name.replace('C-Bonus, ', '')
                tech.name = tech.name.replace('C-Bonus ', '')
                tech.civ = -1
                required_techs = tech.required_techs
                if 101 in required_techs:
                    required_techs = replace_tuple(required_techs, 101, params.feudal_duplicate_tech_id)
                elif 1209 in required_techs:
                    required_techs = replace_tuple(required_techs, 1209, params.feudal_duplicate_tech_id)
                elif 102 in required_techs:
                    required_techs = replace_tuple(required_techs, 102, params.castle_duplicate_tech_id)
                elif 113 in required_techs:
                    required_techs = replace_tuple(required_techs, 113, params.castle_duplicate_tech_id)
                elif 103 in required_techs:
                    required_techs = replace_tuple(required_techs, 103, params.imp_duplicate_tech_id)
                required_techs = replace_tuple(required_techs, -1, params.switch_tech_id)
                tech.required_tech_count += 1
                tech.required_techs = required_techs
                disable_tech(reverse_effect, append_tech(data, tech))

                # Incas + Khitans/Romans Blacksmith upgrade
                if tech_id in (474, 475, 476, 477, 478, 479):
                    append_tech(data, tech)
                # Macedonians + Romans Blacksmith upgrade
                if tech_id in (1271, 1272, 1273):
                    append_tech(data, tech)

        # reverse tb
        tb = effects[civ_tb_tech_num[civ_name]]
        for command in tb.effect_commands:
            command = copy.deepcopy(command)
            match command.type:
                case 4:
                    command.d = -command.d
                case 5:
                    command.d = 1 / command.d
                case 6:
                    command.d = 1 / command.d
                case 1:
                    if command.b != 0:
                        command.d = -command.d
                case 0:
                    continue
                case 8:
                    continue
                case 101:
                    continue
                case 102:
                    continue
                case 103:
                    continue
                case 18:
                    continue
                case _:
                    print(civ_name, effect.name, command)
                    continue

            reverse_effect.effect_commands.append(command)

        # ban uts
        for tech_id in civ_ut_ids[i]:
            disable_tech(reverse_effect, tech_id)
        reverse_tech_ids = deal_custom_bonus(data, params, civ_name)
        for tech_id in reverse_tech_ids:
            disable_tech(reverse_effect, tech_id)
        for j in range(5):
            append_tech(data, get_new_tech(), get_new_effect())
    deal_tech_requrirement(data, params)

    name = 'Enable Unique Warships'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
    effect = get_new_effect(name)
    enable_unit(effect, 250)
    enable_unit(effect, 831)
    enable_unit(effect, 1004)
    move_unit_button(effect, 250, 21)
    move_unit_button(effect, 533, 21)
    move_unit_button(effect, 831, 22)
    move_unit_button(effect, 832, 22)
    move_unit_button(effect, 1004, 23)
    move_unit_button(effect, 1006, 23)
    append_tech(data, tech, effect)
    name = 'Enable Imperial Unique Warships'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    enable_unit(effect, 1750)
    enable_unit(effect, 1948)
    move_unit_button(effect, 1750, 24)
    force_tech(effect, 372)
    move_tech_button(effect, 372, 26)
    force_tech(effect, 448)
    move_tech_button(effect, 448, 27)
    force_tech(effect, 597)
    move_tech_button(effect, 597, 28)
    append_tech(data, tech, effect)

    name = 'Bohemians Cumans Saracens Cheap Buildings'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, 595)
    effect = get_new_effect(name)
    set_resource(effect, 78, 0.05)
    for i in (84, 116, 137):  # market
        set_unit_attribute(effect, i, -1, 104, 175 * 0.85 - 100)
    for i in (10, 14, 87, 86, 101, 153):  # stable archery
        set_unit_attribute(effect, i, -1, 104, 175 * 0.85 - 75)
    for i in (18, 19, 103, 105):  # blacksmith
        set_unit_attribute(effect, i, -1, 104, 175 * 0.85 - 100)
    for i in (209, 210):  # university
        set_unit_attribute(effect, i, -1, 104, 200 * 0.85 - 100)
    append_tech(data, tech, effect)

    BYZANTINES_AGE_DISCOUNT = 0.67
    ITALIANS_AGE_DISCOUNT = 0.85
    MUISCA_AGE_DISCOUNT = 0.5
    name = 'Byzantines + Italians + Muisca Age Discount'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    set_tech_cost(effect, 102, 2, 200 * ITALIANS_AGE_DISCOUNT * MUISCA_AGE_DISCOUNT)
    set_tech_cost(effect, 103, 0, 1000 * BYZANTINES_AGE_DISCOUNT * ITALIANS_AGE_DISCOUNT)
    set_tech_cost(effect, 103, 2, 800 * BYZANTINES_AGE_DISCOUNT * ITALIANS_AGE_DISCOUNT * MUISCA_AGE_DISCOUNT)
    append_tech(data, tech, effect)

    JURCHENS_TECH_DISCOUNT = 0.25
    name = 'Italians + Jurchens Univ'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i in (377, 50, 51, 54, 608):
        for cost in techs[i].resource_costs:
            if cost.type == 1:
                set_tech_cost(effect, i, 1, cost.amount * JURCHENS_TECH_DISCOUNT * ITALIANS_TECH_DISCOUNT)
    append_tech(data, tech, effect)

    TURKS_TECH_DISCOUNT = 0.5
    name = 'Italians + Turks elite cannon galleon'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    cannon_galleon_tech_id = 376
    for cost in techs[cannon_galleon_tech_id].resource_costs:
        if cost.type in (0, 2):
            set_tech_cost(effect, cannon_galleon_tech_id, cost.type, cost.amount * TURKS_TECH_DISCOUNT * ITALIANS_TECH_DISCOUNT)

    name = 'Burgundians + Poles stable tech'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i in [435]:
        for cost in techs[i].resource_costs:
            if cost.type == 0:
                set_tech_cost(effect, i, cost.type, cost.amount * 0.5 * 0.5)
    append_tech(data, tech, effect)

    BULGARIANS_TECH_DISCOUNT = 0.5
    name = 'Bulgarians + Turks houfnice'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i in [787]:
        for cost in techs[i].resource_costs:
            if cost.type == 0:
                set_tech_cost(effect, i, cost.type, cost.amount * TURKS_TECH_DISCOUNT * BULGARIANS_TECH_DISCOUNT)
    append_tech(data, tech, effect)

    name = 'Bulgarians + Jurchens heavy scorpion'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i in [239]:
        for cost in techs[i].resource_costs:
            if cost.type == 0:
                set_tech_cost(effect, i, cost.type, cost.amount * JURCHENS_TECH_DISCOUNT * BULGARIANS_TECH_DISCOUNT)
    append_tech(data, tech, effect)

    name = 'Turks + Jurchens heavy rocket cart'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i in [980]:
        for cost in techs[i].resource_costs:
            set_tech_cost(effect, i, cost.type, cost.amount * JURCHENS_TECH_DISCOUNT * TURKS_TECH_DISCOUNT)
    append_tech(data, tech, effect)

    TUPI_TECH_DISCOUNT = 0.5
    SHU_ARCHERS_TECH_DISCOUNT = 0.75
    KHITANS_CA_DISCOUNT = 0.5
    name = 'Shu + Khitans + Tupi Archery'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    hca_tech_id = 218
    free_archery_techs = (98, 436, 437)
    shu_cheap_range_techs = (100, 237, 437, 199, 200, 201, 211, 212, 219, 436, 218)
    for i, tech in enumerate(techs):
        if i > constants.TECH_NUM:
            break
        if len(tech.research_locations) == 0:
            continue
        research_location_id = tech.research_locations[0].location_id
        if research_location_id == constants.ARCHERY_RANGE_NUM:
            if i == hca_tech_id:
                for cost in tech.resource_costs:
                    if cost.type == -1:
                        continue
                    if cost.type == 0:
                        set_tech_cost(effect, hca_tech_id, cost.type, cost.amount * SHU_ARCHERS_TECH_DISCOUNT * KHITANS_CA_DISCOUNT * TUPI_TECH_DISCOUNT)
                    else:
                        set_tech_cost(effect, hca_tech_id, cost.type, cost.amount * SHU_ARCHERS_TECH_DISCOUNT * KHITANS_CA_DISCOUNT)
                continue
            if i in free_archery_techs: # free
                continue
            if i in shu_cheap_range_techs: # shu
                for cost in tech.resource_costs:
                    if cost.type == -1:
                        continue
                    if cost.type == 0:
                        set_tech_cost(effect, i, cost.type, cost.amount * SHU_ARCHERS_TECH_DISCOUNT * TUPI_TECH_DISCOUNT)
                    else:
                        set_tech_cost(effect, i, cost.type, cost.amount * SHU_ARCHERS_TECH_DISCOUNT)
                continue
            for cost in tech.resource_costs:
                if cost.type == 0:
                    set_tech_cost(effect, i, cost.type, cost.amount * TUPI_TECH_DISCOUNT)

    append_tech(data, tech, effect)

    shu_lumberjack_food = effects[1071].effect_commands[0].d
    athenians_lumberjack_food = 0.0
    for command in effects[1119].effect_commands:
        if command.type == 1 and command.a == 502:
            athenians_lumberjack_food = command.d

    name = 'Athenians + Shu + Romans + Celts + Armenians Lumberjack food'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    set_resource(effect, 502, (athenians_lumberjack_food + shu_lumberjack_food) * 1.15 * 1.05 * (1 + 0.2 * 1.4) / 1.2)
    append_tech(data, tech, effect)

    name = 'Cheap Barrack Techs (Tupi + Dravidians)'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i, tech in enumerate(techs):
        if i > constants.TECH_NUM:
            break
        if len(tech.research_locations) == 0:
            continue
        research_location_id = tech.research_locations[0].location_id
        if research_location_id == constants.BARRACK_NUM:
            if i in (197, 207, 217, 222, 264, 716, 875, 885, 602, 1173, 1174):
                continue
            for j in tech.resource_costs:
                if j.type == -1:
                    continue
                if j.type == 0:
                    set_tech_cost(effect, i, j.type, j.amount * 0.5 * 0.5)
                else:
                    set_tech_cost(effect, i, j.type, j.amount * 0.5)
    append_tech(data, tech, effect)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    for effect in effects:
        match effect.name:
            case 'Vietnamese Bonus':
                effect.effect_commands = list(
                    filter(lambda effect_command: filter_vietnam_bonus(effect_command), effect.effect_commands))
            case 'Dravidians Bonus':
                effect.effect_commands = list(
                    filter(lambda effect_command: filter_dravadian_bonus(effect_command), effect.effect_commands))

    # port button
    for i in (13, 545, 17):
        for civ_id,civ in enumerate(civs):
            creatable = civ.units[i].creatable
            creatable.train_locations.append(copy.deepcopy(creatable.train_locations[0]))
            creatable.train_locations[1].unit_id = 2172
            if civ_id in CHRONICLE_CIV_IDS:
                creatable.train_locations[0].unit_id = 45
    sample_units = data.civs[0].units
    split_line_unit = get_new_unit(sample_units)
    for civ in data.civs:
        for i in range(10):
            civ.units.append(get_new_unit(sample_units))
        civ.units.append(split_line_unit)
    print('Civ Bonuses added.')
