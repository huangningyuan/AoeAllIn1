import copy

from genieutils.datfile import DatFile
from genieutils.unit import ResourceCost

import constants
from all_in_1_params import All_In_1_Params
from constants import DONJON_ID, MAYAN_AGE3_DISCOUNT, SQUIRES_ICON_ID, siege_units, siege_workshop_units, \
    elephant_units, \
    KOREANS_SOLDIER_DISCOUNT, PORTGUESE_DISCOUNT, MAYAN_AGE4_DISCOUNT, SAXON_DISCOUNT, TECH_NUM
from ftt import move_tech_building, move_unit_button
from ftt import move_tech_button
from unique_techs_config_loader import apply_mutex_groups
from utils import append_tech, bind_effect, extend_effect
from utils import force_tech
from utils import get_new_effect, set_require_techs
from utils import get_new_tech
from utils import check_effect
from utils import set_resource, set_unit_attribute, plus_unit_attack, multiply_resource, \
    plus_unit_attribute, multiply_unit_attribute, plus_unit_armor, set_tech_cost, upgrade_unit

CASTLE_BUILT_TECH_ID = 266

def get_ut(data: DatFile, params: All_In_1_Params, tech_id: int, in_castle=False):
    tech = copy.deepcopy(data.techs[tech_id])
    research_button_id = tech.research_locations[0].button_id
    if research_button_id == 7 or (research_button_id == 8 and tech.civ in constants.CHRONICLE_CIV_IDS):
        if in_castle:
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
        else:
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, 266)
    elif research_button_id == 8 or (research_button_id in (12, 13) and tech.civ in constants.CHRONICLE_CIV_IDS):
        if in_castle:
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
        else:
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 266)
    else:
        print('Wrong tech id:', tech_id)
    if in_castle:
        tech.research_locations[0].button_id = 0
    tech.civ = -1
    tech.research_locations[0].hot_key_id = -1
    return tech

def add_unique_techs(data: DatFile, params: All_In_1_Params):
    techs = data.techs
    effects = data.effects
    units = data.civs[0].units
    name = '----Unique Techs----'
    append_tech(data, get_new_tech(name), get_new_effect(name))
    print('Adding unique techs...')

    # ===== LOADER: generate all config-based unique techs =====
    from unique_techs_config_loader import generate_techs
    result = generate_techs(data, params)
    sid2first = result['source_id_to_first_tech_id']
    sid2all = result['source_id_to_all_tech_ids']
    sid2effect = result['source_id_to_effect_id']
    params.civ_index_to_additional_uts = result['civ_index_to_additional_uts']

    # --- Corvinian Army ---
    cov_tech_id = sid2all[514][0]
    cov_tech = techs[cov_tech_id]
    cov_effect = get_new_effect('Corvinian Army')
    food = 35 * 0.8
    gold = 45 * 0.8
    set_unit_attribute(cov_effect, 869, -1, 105, 0)
    set_unit_attribute(cov_effect, 871, -1, 105, 0)
    set_unit_attribute(cov_effect, 869, -1, 103, food + gold)
    set_unit_attribute(cov_effect, 871, -1, 103, food + gold)
    bind_effect(data, cov_tech, cov_effect)

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
    set_require_techs(tech, params.switch_tech_id, sid2all.get(835, [835])[0], cov_tech_id)
    effect = get_new_effect(name)
    food = 35 * 0.75 * 0.8
    set_unit_attribute(effect, 869, -1, 105, 0)
    set_unit_attribute(effect, 871, -1, 105, 0)
    set_unit_attribute(effect, 869, -1, 103, food + gold)
    set_unit_attribute(effect, 871, -1, 103, food + gold)
    append_tech(data, tech, effect)

    name = 'Corvinian Army + Kshatriyas Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, sid2all.get(835, [835])[0], cov_tech_id)
    effect = get_new_effect(name)
    food = 35 * 0.75 * 0.75
    set_unit_attribute(effect, 869, -1, 105, 0)
    set_unit_attribute(effect, 871, -1, 105, 0)
    set_unit_attribute(effect, 869, -1, 103, food + gold)
    set_unit_attribute(effect, 871, -1, 103, food + gold)
    append_tech(data, tech, effect)

    # ===== FORCE TECH SERIES (complete copy from original) =====
    append_tech(data, get_new_tech('----Exceptions----'), get_new_effect('----Exceptions----'))

    # --- Vedic Teachings ---
    vedic_teaching_id = 1309
    vedic_effect_id = techs[vedic_teaching_id].effect_id
    name = 'Vedic Teachings'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 266)
    effect = get_new_effect(name)
    force_tech(effect, vedic_teaching_id)
    move_tech_button(effect, vedic_teaching_id, 7)
    append_tech(data, tech, effect)

    effect = check_effect(effects, vedic_effect_id)
    multiply_resource(effect, 502, 1.02)
    multiply_resource(effect, 267, 1.02)
    multiply_resource(effect, 241, 1.02)
    multiply_resource(effect, 512, 1.02)

    current_vedic_univ_techs = list()
    for i in range(constants.TECH_NUM):
        required_techs = techs[i].required_techs
        if vedic_teaching_id in required_techs:
            current_vedic_univ_techs.append(required_techs[0])
    print('Current Vedic Univ Techs:', current_vedic_univ_techs)
    for i in constants.university_techs:
        if constants.university_techs[i] not in current_vedic_univ_techs:
            name = f'{i} Researched for Vedic Teachings'
            tech = get_new_tech(name)
            set_require_techs(tech, constants.university_techs[i], vedic_teaching_id)
            tech.effect_id = vedic_effect_id
            append_tech(data, tech)

    # --- Flemish Revolution ---
    name = '[FTT] Flemish Revolution'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    force_tech(effect, 755)
    move_tech_button(effect, 755, 23)
    append_tech(data, tech, effect)

    # --- Skandhavaras ---
    name = 'Skandhavaras'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    ska_id = 1310
    force_tech(effect, ska_id)
    move_tech_button(effect, ska_id, 33)
    move_tech_button(effect, 1323, 33)
    move_tech_button(effect, 1324, 34)
    append_tech(data, tech, effect)

    # --- Helot Levies TC button Imperial adjustment ---
    helot_levies_tc_id = sid2all[1130][-1]
    name = 'Helot Levies Imp Button'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    move_tech_button(effect, helot_levies_tc_id, 11)
    append_tech(data, tech, effect)

    # --- Anarchy + variants ---
    name = 'enable Anarchy'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, CASTLE_BUILT_TECH_ID)
    effect = get_new_effect(name)
    anarchy_tech_id = 16
    huskarl_ids = [41, 555]
    force_tech(effect, anarchy_tech_id)
    move_tech_building(effect, anarchy_tech_id, constants.BARRACK_ID)
    move_tech_button(effect, anarchy_tech_id, 29)
    for i in huskarl_ids:
        move_unit_button(effect, i, 24, 1)
    append_tech(data, tech, effect)
    name = 'move elite_huskarl_button'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, anarchy_tech_id)
    effect = get_new_effect(name)
    move_tech_button(effect, 365, 29, 1)
    append_tech(data, tech, effect)
    name = 'Anarchy + Malians'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, anarchy_tech_id)
    effect = get_new_effect(name)
    for i in huskarl_ids:
        plus_unit_armor(effect, i, -1, 2, 3)
    append_tech(data, tech, effect)
    name = 'Anarchy + Malians + Teutons Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, anarchy_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    for i in huskarl_ids:
        plus_unit_armor(effect, i, -1, 1, 3)
    append_tech(data, tech, effect)

    # --- Marauders + variants ---
    name = 'enable Marauders'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, CASTLE_BUILT_TECH_ID)
    effect = get_new_effect(name)
    marauder_id = 483
    tarkan_ids = [755, 757]
    force_tech(effect, marauder_id)
    move_tech_building(effect, marauder_id, constants.STABLE_ID)
    move_tech_button(effect, marauder_id, 26)
    for i in tarkan_ids:
        move_unit_button(effect, i, 21, 1)
    append_tech(data, tech, effect)

    # --- Thalassocracy ---
    name = 'enable Thalassocracy'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, 266)
    effect = get_new_effect(name)
    tha_tech_id = 624
    force_tech(effect, tha_tech_id)
    move_tech_button(effect, tha_tech_id, 10)
    move_tech_building(effect, tha_tech_id, constants.DOCK_ID)
    append_tech(data, tech, effect)

    # ===== B CLASS: custom effect replacement =====

    # --- Grand Trunk Road source_id=506 ---
    grand_trunk_road_id = sid2first[506]
    name = 'Grand Trunk Road'
    effect = get_new_effect(name)
    effect.effect_commands = list(filter(lambda command: command.type != 1, effects[562].effect_commands))
    multiply_resource(effect, 213, 1.1)
    multiply_resource(effect, 241, 1.1)
    multiply_resource(effect, 297, 1.1)
    multiply_resource(effect, 298, 1.1)
    bind_effect(data, techs[grand_trunk_road_id], effect)

    # --- Paper Money source_id=629 ---
    paper_money_tech_id = sid2first[629]
    name = 'Paper Money'
    paper_money_factor = 1.5 * 1.15 * (1 + (0.2 * 1.4)) * (1 + (0.2 * 1.4)) * (1 + (0.1 * 1.4)) * 1.05
    effect = get_new_effect(name)
    set_resource(effect, 266, paper_money_factor)
    bind_effect(data, techs[paper_money_tech_id], effect)

    # --- Burgundian Vineyards source_id=754 ---
    bv_tech_id = sid2first[754]
    name = 'Burgundian Vineyards'
    effect = get_new_effect(name)
    bv_factor = 2 * 1.15 * 1.05
    set_resource(effect, 236, bv_factor)
    bind_effect(data, techs[bv_tech_id], effect)

    # --- Forced Levy source_id=625 ---
    forced_levy_id = sid2first[625]
    name = 'Forced Levy'
    effect = get_new_effect(name)
    food = constants.MILLITIA_LINE_FOOD * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT * SAXON_DISCOUNT
    gold = 20 * constants.PORTGUESE_DISCOUNT * constants.GOTH_AGE4_DISCOUNT * SAXON_DISCOUNT
    food += gold
    for id in constants.MILLITIA_LINE_IDS:
        set_unit_attribute(effect, id, -1, 103, food)
        set_unit_attribute(effect, id, -1, 105, 0)
    bind_effect(data, techs[forced_levy_id], effect)

    # --- Eisphora source_id=1122 ---
    eis_tech_id = sid2first[1122]
    name = 'Eisphora'
    effect = get_new_effect(name)
    hoplite_id = 2110
    e_hoplite_id = 2111
    hoplite = data.civs[0].units[hoplite_id]
    food = hoplite.creatable.resource_costs[0].amount
    gold = hoplite.creatable.resource_costs[1].amount
    new_food = food * constants.GOTH_AGE4_DISCOUNT * constants.INCA_AGE4_DISCOUNT
    new_gold = gold * constants.GOTH_AGE4_DISCOUNT * constants.PORTGUESE_DISCOUNT
    for i in (hoplite_id, e_hoplite_id):
        set_unit_attribute(effect, i, -1, 103, new_food + new_gold * 0.33)
        set_unit_attribute(effect, i, -1, 105, new_gold * 0.67)
    bind_effect(data, techs[eis_tech_id], effect)

    # --- Kamandaran source_id=488 ---
    kam_id = sid2first[488]
    name = 'Kamandaran'
    effect = get_new_effect(name)
    wood = 25 * MAYAN_AGE3_DISCOUNT * KOREANS_SOLDIER_DISCOUNT * SAXON_DISCOUNT
    gold = 45 * MAYAN_AGE3_DISCOUNT * PORTGUESE_DISCOUNT * SAXON_DISCOUNT
    kama_effect = effects[sid2effect[488]]
    for command in kama_effect.effect_commands:
        if command.c == 105:
            gold_cost = -command.d
        elif command.c == 104:
            wood_cost = command.d
    wood += gold * wood_cost / gold_cost
    print(f'Wood cost: {wood_cost}, gold cost: {gold_cost}, wood: {wood}, gold: {gold}')
    set_unit_attribute(effect, 4, -1, 104, wood)
    set_unit_attribute(effect, 24, -1, 104, wood)
    set_unit_attribute(effect, 492, -1, 104, wood)
    set_unit_attribute(effect, 4, -1, 105, 0)
    set_unit_attribute(effect, 24, -1, 105, 0)
    set_unit_attribute(effect, 492, -1, 105, 0)
    bind_effect(data, techs[kam_id], effect)

    # --- Detinets source_id=455 ---
    det_id = sid2first[455]
    name = 'Detinets'
    effect = get_new_effect(name)
    inca_discount = 0.85
    malian_discount = 0.85
    stone = 125 * inca_discount
    wood = 35 * malian_discount
    new_stone = stone * 0.6
    new_wood = wood + stone * 0.4
    set_unit_attribute(effect, 79, -1, 104, new_wood)
    set_unit_attribute(effect, 79, -1, 106, new_stone)
    set_unit_attribute(effect, 234, -1, 104, new_wood)
    set_unit_attribute(effect, 234, -1, 106, new_stone)
    set_unit_attribute(effect, 235, -1, 104, new_wood)
    set_unit_attribute(effect, 235, -1, 106, new_stone)
    set_unit_attribute(effect, 236, -1, 104, stone * 0.4)
    set_unit_attribute(effect, 236, -1, 106, new_stone)
    stone = 650 * 0.85 * 0.85
    set_unit_attribute(effect, 82, -1, 104, stone * 0.4)
    set_unit_attribute(effect, 82, -1, 106, stone * 0.6)
    bind_effect(data, techs[det_id], effect)

    unit = units[constants.DONJON_ID]
    costs = unit.creatable.resource_costs
    stone = costs[0].amount * inca_discount
    wood = costs[1].amount * malian_discount
    new_stone = stone * 0.6
    new_wood = wood + stone * 0.4
    set_unit_attribute(effect, DONJON_ID, -1, 104, new_wood)
    set_unit_attribute(effect, DONJON_ID, -1, 106, new_stone)

    # --- Hill Forts source_id=691 ---
    hf_id = sid2first[691]
    name = 'Hill Forts'
    effect = get_new_effect(name)
    for i in constants.TC_IDS:
        plus_unit_attribute(effect, i, -1, 1, 3)
        plus_unit_attribute(effect, i, -1, 12, 3)
        plus_unit_attribute(effect, i, -1, 23, 3)
    bind_effect(data, techs[hf_id], effect)

    # --- Tigui source_id=576 ---
    tig_id = sid2first[576]
    name = 'Tigui'
    effect = get_new_effect(name)
    for i in constants.TC_IDS:
        plus_unit_attribute(effect, i, -1, 102, 8)
        plus_unit_attribute(effect, i, -1, 107, 8)
    bind_effect(data, techs[tig_id], effect)

    # --- Hussite Reforms source_id=785 ---
    hr_id = sid2first[785]
    name = 'Hussite Reforms'
    effect = get_new_effect(name)
    for i, tech1 in enumerate(techs):
        if len(tech1.research_locations) == 0:
            continue
        research_location_id = tech1.research_locations[0].location_id
        research_button_id = tech1.research_locations[0].button_id
        if research_location_id == constants.MONESTARY_ID and research_button_id > 0:
            if tech1.name in ('Herbal Medicine'):
                continue
            else:
                food = 0
                for cost in tech1.resource_costs:
                    if cost.type == 0:
                        food = cost.amount / 2
                    elif cost.type == 3:
                        gold = cost.amount / 2
                set_tech_cost(effect, i, 3, 0)
                set_tech_cost(effect, i, 0, food + gold)
    set_unit_attribute(effect, 125, -1, 105, 0)
    set_unit_attribute(effect, 125, -1, 103, 80)
    set_unit_attribute(effect, 775, -1, 105, 0)
    set_unit_attribute(effect, 775, -1, 103, 110)
    cost = units[1811].creatable.resource_costs
    food = cost[0].amount * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    gold = cost[1].amount * constants.PORTGUESE_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    set_unit_attribute(effect, 1811, -1, 105, 0)
    set_unit_attribute(effect, 1811, -1, 103, food + gold)
    bind_effect(data, techs[hr_id], effect)

    # ===== C CLASS: effect modification =====

    # --- Stronghold source_id=482 ---
    sh_effect_id = sid2effect[482]
    effect = check_effect(effects, sh_effect_id)
    multiply_unit_attribute(effect, 2418, -1, 10, 0.75)
    plus_unit_attribute(effect, 82, -1, 63, -32)
    plus_unit_attribute(effect, 2418, -1, 63, -32)

    # --- Citadels source_id=7 ---
    cit_effect_id = sid2effect[7]
    effect = check_effect(effects, cit_effect_id)
    plus_unit_attack(effect, 2418, -1, 4, 3)
    plus_unit_attack(effect, 2418, -1, 3, 1)
    plus_unit_attack(effect, 2418, -1, 3, 17)

    # --- Svan Towers source_id=923 ---
    st_effect_id = sid2effect[923]
    effect = check_effect(effects, st_effect_id)
    plus_unit_attack(effect, 1830, -1, 2, 3)
    for i in (2275, 2276, 2277):
        plus_unit_attack(effect, i, -1, 2, 3)

    # --- Curare source_id=1393 ---
    cur_effect_id = sid2effect[1393]
    effect = check_effect(effects, cur_effect_id)
    citadel_projectile_id = 1830
    set_unit_attribute(effect, citadel_projectile_id, -1, 145, 2610)
    set_unit_attribute(effect, citadel_projectile_id, -1, 146, 2)
    set_unit_attribute(effect, citadel_projectile_id, -1, 147, 0.05)

    # --- Paiks source_id=833 ---
    paiks_effect_id = sid2effect[833]
    effect = check_effect(effects, paiks_effect_id)
    original_units = set(map(lambda command: command.a, effect.effect_commands))
    extend_units = []
    for unit in elephant_units:
        if unit not in original_units:
            extend_units.append(unit)
    extend_effect(effect, extend_units)

    # --- Maghrebi Camels source_id=579 ---
    ma_ca_effect_id = sid2effect[579]
    effect = check_effect(effects, ma_ca_effect_id)
    original_units = set(map(lambda command: command.a, effect.effect_commands))
    camels = []
    for i, unit in enumerate(units):
        if unit and unit.creatable and unit.type_50:
            for armor in unit.type_50.armours:
                if armor.class_ == 30:
                    camels.append(i)
                    break
    extend_units = list()
    for i in camels:
        if i not in original_units:
            extend_units.append(i)
    extend_effect(effect, extend_units)

    # ===== COMBINATION VARIANTS =====

    # --- Paper Money + Grand Trunk Road ---
    name = 'Paper Money + Grand Trunk Road'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, paper_money_tech_id, grand_trunk_road_id)
    effect = get_new_effect(name)
    paper_money_factor *= 1.1
    set_resource(effect, 266, paper_money_factor)
    append_tech(data, tech, effect)

    # --- Paper Money + Vedic Teachings ---
    name = 'Paper Money + Vedic Teachings'
    effect = get_new_effect(name)
    multiply_resource(effect, 266, 1.2)
    effect_id = len(effects)
    effects.append(effect)
    for tech_name, tech_id in constants.university_techs.items():
        tech = get_new_tech(name + " + " + tech_name)
        set_require_techs(tech, params.switch_tech_id, tech_id, vedic_teaching_id, paper_money_tech_id)
        tech.effect_id = effect_id
        append_tech(data, tech)

    # --- Burgundian Vineyards + Grand Trunk Road ---
    name = 'Burgundian Vineyards + Grand Trunk Road'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, bv_tech_id, grand_trunk_road_id)
    effect = get_new_effect(name)
    bv_factor *= 1.1
    set_resource(effect, 236, bv_factor)
    append_tech(data, tech, effect)

    # --- Burgundian Vineyards + Vedic Teachings ---
    name = 'Burgundian Vineyards + Vedic Teachings'
    effect = get_new_effect(name)
    multiply_resource(effect, 236, 1.02)
    effect_id = len(effects)
    effects.append(effect)
    for tech_name, tech_id in constants.university_techs.items():
        tech = get_new_tech(name + " + " + tech_name)
        set_require_techs(tech, params.switch_tech_id, tech_id, vedic_teaching_id, bv_tech_id)
        tech.effect_id = effect_id
        append_tech(data, tech)

    # --- Chronic civs Elite Kipchak ---
    cm_tech_id = sid2first[690]
    name = 'Chronical civs Elite Kipchak'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, cm_tech_id, params.other_params['chronicle_civs_requirement'])
    effect = get_new_effect(name)
    move_unit_button(effect, 1260, 9)
    append_tech(data, tech, effect)

    # --- Forced Levy + Kshatriyas ---
    ksha_id = sid2first[835]
    name = 'Forced Levy + Kshatriyas'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, forced_levy_id, ksha_id)
    gold = constants.MILLITIA_LINE_GOLD * constants.PORTGUESE_DISCOUNT * constants.GOTH_AGE4_DISCOUNT * SAXON_DISCOUNT
    food = constants.MILLITIA_LINE_FOOD * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT * constants.KSHATRIYAS_DISCOUNT * SAXON_DISCOUNT + gold
    effect = get_new_effect(name)
    for id in constants.MILLITIA_LINE_IDS:
        set_unit_attribute(effect, id, -1, 103, food)
    append_tech(data, tech, effect)

    # --- Eisphora + Kshatriyas ---
    name = 'Eisphora + Kshatriyas'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, eis_tech_id, ksha_id)
    effect = get_new_effect(name)
    new_food_k = new_food * constants.KSHATRIYAS_DISCOUNT
    for i in (hoplite_id, e_hoplite_id):
        set_unit_attribute(effect, i, -1, 103, new_food_k + new_gold * 0.33)
        set_unit_attribute(effect, i, -1, 105, new_gold * 0.67)
    append_tech(data, tech, effect)

    # --- Kamandaran Imp ---
    name = 'Kamandaran Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, kam_id)
    effect = get_new_effect(name)
    wood = 25 * MAYAN_AGE4_DISCOUNT * KOREANS_SOLDIER_DISCOUNT * SAXON_DISCOUNT
    gold = 45 * MAYAN_AGE4_DISCOUNT * PORTGUESE_DISCOUNT * SAXON_DISCOUNT
    wood += gold * wood_cost / gold_cost
    set_unit_attribute(effect, 4, -1, 104, wood)
    set_unit_attribute(effect, 24, -1, 104, wood)
    set_unit_attribute(effect, 492, -1, 104, wood)
    append_tech(data, tech, effect)

    # --- Detinets Imp ---
    name = 'Detinets Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, det_id)
    effect = get_new_effect(name)
    stone = 650 * inca_discount * 0.75
    set_unit_attribute(effect, 82, -1, 104, stone * 0.4)
    set_unit_attribute(effect, 82, -1, 106, stone * 0.6)
    set_unit_attribute(effect, 2418, -1, 104, stone * 0.4)
    set_unit_attribute(effect, 2418, -1, 106, stone * 0.6)
    append_tech(data, tech, effect)

    # --- Kshatriyas + Hussite Reforms ---
    cost = units[1811].creatable.resource_costs
    food = cost[0].amount * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    gold = cost[1].amount * constants.PORTGUESE_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    name = 'Kshatriyas + Hussite Reforms'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, hr_id, ksha_id)
    effect = get_new_effect(name)
    food = food * constants.KSHATRIYAS_DISCOUNT
    set_unit_attribute(effect, 1811, -1, 103, food + gold)
    append_tech(data, tech, effect)

    # ===== D CLASS: required_techs modification =====
    gre_bbt_id, gre_dock_id = sid2all[464]
    techs[465].required_techs = (47, 464, gre_bbt_id, gre_dock_id, -1, -1)

    roc_siege_id, roc_dock_id = sid2all[52]
    techs[1015].required_techs = (47, 52, roc_siege_id, roc_dock_id, -1, -1)

    pl_castle_id = sid2all[1133][0]
    pl_shipyard_id = sid2all[1133][-1]

    name = 'Peloponnesian League + Grand Trunk Road'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, pl_castle_id, pl_shipyard_id, grand_trunk_road_id)
    tech.required_tech_count = 2
    effect = get_new_effect(name)
    multiply_resource(effect, 521, 1.1)
    append_tech(data, tech, effect)

    # --- Coiled Serpent Array + Shield Wall ---
    csa_ids = sid2all[1070]
    sw_ids = sid2all[1464]
    csa_aura_infantry_units = [93, 1786, 358, 1787, 359, 1788, 1959, 1961]

    name = 'Coiled Serpent Array + Shield Wall'
    tech = get_new_tech(name)
    all_preqs = csa_ids + sw_ids
    set_require_techs(tech, *all_preqs)
    tech.required_tech_count = 2
    effect = get_new_effect(name)
    for uid in csa_aura_infantry_units:
        plus_unit_attribute(effect, uid, -1, 63, -96)
    append_tech(data, tech, effect)

    # Infantry Aura
    for unit in units:
        if unit and unit.class_ == 6 and unit.creatable and unit.type_50 and unit.type_50.break_off_combat >= 32:
            boc = unit.type_50.break_off_combat
            if boc & 32:
                plus_unit_attribute(effects[1464], unit.id, -1, 63, -32)
            if boc & 64:
                plus_unit_attribute(effects[1464], unit.id, -1, 63, -64)

    # ===== APPLY MUTEX (delayed, after all effect modifications) =====
    apply_mutex_groups(data, result, extra_groups=[[482, 1286]])

    # ===== FOOTER: spacer techs =====
    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())
    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    print('Unique tech added.')