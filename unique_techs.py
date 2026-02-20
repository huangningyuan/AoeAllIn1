import copy

from genieutils.datfile import DatFile
from genieutils.unit import ResourceCost

import constants
from all_in_1_params import All_In_1_Params
from constants import DONJON_ID, MAYAN_AGE3_DISCOUNT, SQUIRES_ICON_ID, siege_units, siege_workshop_units, \
    elephant_units, \
    KOREANS_SOLDIER_DISCOUNT, PORTGUESE_DISCOUNT, MAYAN_AGE4_DISCOUNT, TECH_NUM
from ftt import move_tech_building, move_unit_button
from ftt import move_tech_button
from mutex import Mutex, add_mutex
from utils import append_tech, extend_effect
from utils import disable_tech
from utils import force_tech
from utils import get_new_effect, set_require_techs
from utils import get_new_tech
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
    # UT in castles
    append_tech(data, get_new_tech('----Castle UTs----'), get_new_effect('----Castle UTs----'))

    vedic_teaching_id = 1309
    vedic_effect_id = techs[vedic_teaching_id].effect_id
    name = 'Vedic Teachings'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 266)
    effect = get_new_effect(name)
    force_tech(effect, vedic_teaching_id)
    move_tech_button(effect, vedic_teaching_id, 7)
    append_tech(data, tech, effect)

    effect = effects[vedic_effect_id]
    multiply_resource(effect, 502, 1.02) # Shu+Athenians
    multiply_resource(effect, 267, 1.02) # Portuguese
    multiply_resource(effect, 241, 1.02) # Poles
    multiply_resource(effect, 512, 1.02) # Puru

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


    # Kasbah
    tech = get_ut(data, params, 578, True)
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.CONSCRIPTION_ICON_ID
    append_tech(data, tech)
    name = 'Grand Trunk Road'
    tech = get_ut(data, params, 506, True)
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.BANKING_ICON_ID
    effect = get_new_effect(name)
    effect.effect_commands = list(filter(lambda command: command.type != 1, effects[562].effect_commands))
    multiply_resource(effect, 213, 1.1)
    multiply_resource(effect, 241, 1.1)
    grand_trunk_road_id, effect_id = append_tech(data, tech, effect)
    name = 'Paper Money'
    tech = get_ut(data, params, 629, True)
    tech.research_locations[0].button_id = 7
    effect = get_new_effect(name)
    paper_money_factor = 1.5 * 1.15 * (1 + (0.2 * 1.4)) * (1 + (0.2 * 1.4)) * (1 + (0.1 * 1.4)) * 1.05
    set_resource(effect, 266, paper_money_factor)
    paper_money_tech_id, effect_id = append_tech(data, tech, effect)
    name = 'Paper Money + Grand Trunk Road'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, paper_money_tech_id, grand_trunk_road_id)
    effect = get_new_effect(name)
    paper_money_factor *= 1.1
    set_resource(effect, 266, paper_money_factor)
    append_tech(data, tech, effect)
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

    name = 'Burgundian Vineyards'
    tech = get_ut(data, params, 754, True)
    effect = get_new_effect(name)
    tech.research_locations[0].button_id = 7
    bv_factor = 2 * 1.15 * 1.05
    set_resource(effect, 236, bv_factor)
    bv_tech_id, effect_id = append_tech(data, tech, effect)
    name = 'Burgundian Vineyards + Grand Trunk Road'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, bv_tech_id, grand_trunk_road_id)
    effect = get_new_effect(name)
    bv_factor *= 1.1
    set_resource(effect, 236, bv_factor)
    append_tech(data, tech, effect)
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

    # Mahayana
    tech = get_ut(data, params, 834, True)
    tech.research_locations[0].button_id = 7
    append_tech(data, tech)

    # Peloponnesian League
    pl_id = 1133
    tech = get_ut(data, params, pl_id, True)
    tech.name = 'Peloponnesian League'
    tech.research_locations[0].button_id = 7
    pl_castle_id = append_tech(data, tech)
    # Wootz Steel
    wootz_steel_id = 832
    tech = get_ut(data, params, wootz_steel_id, True)
    tech.research_locations[0].button_id = 8
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)
    # Kshatriyas
    kshatriyas = get_ut(data, params, 835, True)
    kshatriyas.research_locations[0].button_id = 8
    ksha_id = append_tech(data, kshatriyas)
    # Tuntian
    tuntian_id = 1061
    tech = get_ut(data, params, tuntian_id, True)
    tech.research_locations[0].button_id = 8
    append_tech(data, tech)
    # Odomantian Raiders
    od_id = 1296
    tech = get_ut(data, params, od_id, True)
    tech.research_locations[0].button_id = 8
    or_castle_id = append_tech(data, tech)
    or_effect_id = tech.effect_id
    # Kataparuto
    kataparuto_id = 59
    tech = get_ut(data, params, kataparuto_id, True)
    tech.research_locations[0].button_id = 13
    append_tech(data, tech)
    # Warwolf
    warwolf_id = 461
    tech = get_ut(data, params, warwolf_id, True)
    tech.research_locations[0].button_id = 13
    append_tech(data, tech)
    # Timurid Siegecraft
    tech = get_ut(data, params, 688, True)
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.SIEGE_ENGINEERS_ICON_ID
    append_tech(data, tech)
    # name = 'Counterweights'
    cw_id = 454
    tech = get_ut(data, params, cw_id, True)
    tech.research_locations[0].button_id = 13
    cw_effect_id = tech.effect_id
    cw_castle_id = append_tech(data, tech)
    # name = 'Crenellations'
    tech = get_ut(data, params, 11, True)
    tech.research_locations[0].button_id = 11
    append_tech(data, tech)
    # name = 'Stronghold'
    sh_id = 482
    tech = get_ut(data, params, sh_id, True)
    tech.research_locations[0].button_id = 11
    sh_effect_id = tech.effect_id
    sh_castle_id = append_tech(data, tech)
    # stronghold + Thracian
    effect = effects[sh_effect_id]
    multiply_unit_attribute(effect, 2418, -1, 10, 0.75)
    plus_unit_attribute(effect, 82, -1, 63, -32)
    plus_unit_attribute(effect, 2418, -1, 63, -32)
    # name = 'Citadels'
    tech = get_ut(data, params, 7, True)
    tech.research_locations[0].button_id = 11
    append_tech(data, tech)
    effect = effects[tech.effect_id]
    plus_unit_attack(effect, 2418, -1, 4, 3)
    plus_unit_attack(effect, 2418, -1, 3, 1)
    plus_unit_attack(effect, 2418, -1, 3, 17)
    # name = 'Svan Towers'
    st_id = 923
    tech = get_ut(data, params, st_id, True)
    tech.research_locations[0].button_id = 11
    st_effect_id = tech.effect_id
    effect = effects[tech.effect_id]
    plus_unit_attack(effect, 1830, -1, 2, 3)
    for i in (2275, 2276, 2277):
        plus_unit_attack(effect, i, -1, 2, 3)
    st_castle_id = append_tech(data, tech)
    # Curare
    cur_id = 1393
    tech = get_ut(data, params, cur_id, True)
    tech.research_locations[0].button_id = 11
    cur_effect_id = tech.effect_id
    cur_castle_id = append_tech(data, tech)
    cur_effect = effects[cur_effect_id]
    citadel_projectile_id = 1830
    set_unit_attribute(cur_effect, citadel_projectile_id, -1, 145, 2610)
    set_unit_attribute(cur_effect, citadel_projectile_id, -1, 146, 2)
    set_unit_attribute(cur_effect, citadel_projectile_id, -1, 147, 0.05)

    # name = 'First Crusade'
    tech = get_ut(data, params, 756, True)
    tech.research_locations[0].button_id = 21
    append_tech(data, tech)
    # name = 'Cuman Mercenaries'
    tech = get_ut(data, params, 690, True)
    tech.research_locations[0].button_id = 9
    append_tech(data, tech)
    # name = 'Atheism'
    tech = get_ut(data, params, 21, True)
    tech.research_locations[0].button_id = 22
    append_tech(data, tech)

    name = '[FTT] Flemish Revolution'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    force_tech(effect, 755)
    move_tech_button(effect, 755, 23)
    append_tech(data, tech, effect)
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

    name = 'Double Crossbow'
    dc_id = 623
    tech = get_ut(data, params, dc_id, True)
    dc_effect_id = tech.effect_id
    dc_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = dc_castle_id
    name = 'Comitatenses'
    comitatenses_id = 884
    tech = get_ut(data, params, comitatenses_id, True)
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    comitatenses_effect_id = tech.effect_id
    comitatenses_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = comitatenses_castle_id
    name = 'Fabric Shields'
    fs_id = 517
    tech = get_ut(data, params, fs_id, True)
    tech.icon_id = constants.INFANTRY_ARMOR_ICON_ID
    fs_effect_id = tech.effect_id
    fs_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = fs_castle_id
    name = 'Paiks'
    paiks_id = 833
    tech = get_ut(data, params, paiks_id, True)
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    paiks_effect_id = tech.effect_id
    paiks_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = paiks_castle_id
    effect = effects[paiks_effect_id]
    original_units = set(map(lambda command: command.a, effect.effect_commands))
    extend_units = []
    for unit in elephant_units:
        if unit not in original_units:
            extend_units.append(unit)
    extend_effect(effect, extend_units)
    name = 'Royal Heirs'
    ro_he_id = 574
    tech = get_ut(data, params, ro_he_id, True)
    tech.icon_id = constants.INFANTRY_ARMOR_ICON_ID
    ro_he_effect_id = tech.effect_id
    ro_he_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = ro_he_castle_id
    name = 'Maghrebi Camels'
    ma_ca_id = 579
    tech = get_ut(data, params, ma_ca_id, True)
    ma_ca_effect_id = tech.effect_id
    effect = effects[ma_ca_effect_id]
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
    ma_ca_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = ma_ca_castle_id
    name = 'Wagenburg Tactics'
    wa_ta_id = 784
    tech = get_ut(data, params, wa_ta_id, True)
    wa_ta_effect_id = tech.effect_id
    wa_ta_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = wa_ta_castle_id
    effect = effects[wa_ta_effect_id]
    gunpowder_units = set(map(lambda command: command.a, effects[410].effect_commands))
    original_units = set(map(lambda command: command.a, effect.effect_commands))
    for unit_id in gunpowder_units - original_units:
        multiply_unit_attribute(effect, unit_id, -1, 5, 1.15)
    name = 'Taxiarchs'
    tax_id = 1120
    tech = get_ut(data, params, tax_id, True)
    tech.name = name
    tax_effect_id = tech.effect_id
    tax_tech_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = tax_tech_id
    # Coiled Serpent Array
    name = 'Coiled Serpent Array'
    csa_id = 1070
    tech = get_ut(data, params, csa_id, True)
    csa_effect_id = tech.effect_id
    csa_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = csa_castle_id
    # Red Cliffs Tactics
    name = 'Red Cliffs Tactics'
    rct_id = 1080
    tech = get_ut(data, params, rct_id, True)
    rct_effect_id = tech.effect_id
    rct_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = rct_castle_id
    name = 'Sarissophoroi'
    sar_id = 1287
    tech = get_ut(data, params, sar_id, True)
    sar_effect_id = tech.effect_id
    sar_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = sar_castle_id
    # Sparabaras
    name = 'Sparabaras'
    sp_id = 1110
    tech.name = name
    tech = get_ut(data, params, sp_id, True)
    sp_effect_id = tech.effect_id
    sp_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = sp_castle_id
    # Bessian Metalworking
    name = 'Bessian Metalworking'
    be_me_id = 1298
    tech = get_ut(data, params, be_me_id, True)
    be_me_effect_id = tech.effect_id
    be_me_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = be_me_castle_id
    # Leaf-Headed Shafts
    name = 'Leaf-Headed Shafts'
    lsh_id = 1308
    tech = get_ut(data, params, lsh_id, True)
    lsh_effect_id = tech.effect_id
    lsh_castle_id = append_tech(data, tech)
    params.ut_in_castle_with_mutex_list[name] = lsh_castle_id

    # Butalmapu
    but_id = 1380
    tech = get_ut(data, params, but_id, True)
    tech.research_locations[0].button_id = 6
    but_effect_id = tech.effect_id
    but_castle_id = append_tech(data, tech)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in barracks
    append_tech(data, get_new_tech('----Barrack UTs----'), get_new_effect('----Barrack UTs----'))
    # name = 'Perfusion'
    tech = get_ut(data, params, 457)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    tech.icon_id = constants.CONSCRIPTION_ICON_ID
    append_tech(data, tech)
    # name = 'Garland Wars'
    tech = get_ut(data, params, 24)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)
    # name = 'Druzhina'
    tech = get_ut(data, params, 513)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)
    # name = 'Chieftains'
    tech = get_ut(data, params, 463)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    tech_id = append_tech(data, tech)
    name = 'Grand Trunk Road + Chieftains'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, grand_trunk_road_id, tech_id)
    effect = get_new_effect(name)
    multiply_resource(effect, 274, 1.1)
    append_tech(data, tech, effect)
    # name = 'Fereters'
    tech = get_ut(data, params, 921)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    effect = effects[tech.effect_id]
    plus_unit_attribute(effect, 1786, -1, 0, -30)
    plus_unit_attribute(effect, 1787, -1, 0, -30)
    plus_unit_attribute(effect, 1788, -1, 0, -30)
    append_tech(data, tech)
    # Lamellar Armor
    la_id = 1006
    tech = get_ut(data, params, la_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    la_effect_id = tech.effect_id
    la_barrack_id = append_tech(data, tech)
    # Dii Plunderers
    dp_id = 1297
    tech = get_ut(data, params, dp_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 11
    dp_effect_id = tech.effect_id
    dp_barrack_id = append_tech(data, tech)
    add_mutex(data, [or_castle_id, dp_barrack_id], [or_effect_id, dp_effect_id])

    name = 'Forced Levy'
    tech = get_ut(data, params, 625)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.GUILDS_ICON_ID
    effect = get_new_effect(name)
    food = constants.MILLITIA_LINE_FOOD * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    gold = 20 * constants.PORTGUESE_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    food += gold
    for id in constants.MILLITIA_LINE_IDS:
        set_unit_attribute(effect, id, -1, 103, food)
        set_unit_attribute(effect, id, -1, 105, 0)
    tech_id, effect_id = append_tech(data, tech, effect)
    name = 'Forced Levy + Kshatriyas'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, tech_id, ksha_id)
    food = constants.MILLITIA_LINE_FOOD * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT * constants.KSHATRIYAS_DISCOUNT + gold
    effect = get_new_effect(name)
    for id in constants.MILLITIA_LINE_IDS:
        set_unit_attribute(effect, id, -1, 103, food)
    append_tech(data, tech, effect)
    # name = 'Bagains'
    tech = get_ut(data, params, 686)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.INFANTRY_ARMOR_ICON_ID
    append_tech(data, tech)
    # Comitatenses
    tech = get_ut(data, params, comitatenses_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    tech.effect_id = comitatenses_effect_id
    comitatenses_barrack_id = append_tech(data, tech)
    # Bessian Metalworking
    tech = get_ut(data, params, be_me_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 6
    be_me_barrack_id = append_tech(data, tech)

    name = 'enable Anarchy'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, CASTLE_BUILT_TECH_ID)
    effect = get_new_effect(name)
    anarchy_tech_id = 16
    force_tech(effect, anarchy_tech_id)
    move_tech_building(effect, anarchy_tech_id, constants.BARRACK_NUM)
    move_tech_button(effect, anarchy_tech_id, 29)
    for i in (41, 555):
        move_unit_button(effect, i, 24, 1)
    append_tech(data, tech, effect)
    name = 'move elite_huskarl_button'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, anarchy_tech_id)
    effect = get_new_effect(name)
    move_tech_button(effect, 365, 29, 1)
    append_tech(data, tech, effect)

    # name = 'El Dorado'
    tech = get_ut(data, params, 4)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 9
    tech.icon_id = constants.IUT_ICON_ID
    append_tech(data, tech)

    # Fabric Shields
    tech = get_ut(data, params, fs_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 34
    tech.icon_id = constants.INFANTRY_ARMOR_ICON_ID
    tech.effect_id = fs_effect_id
    fs_barrack_id = append_tech(data, tech)
    # Cacique
    cacique_id = 1392
    tech = get_ut(data, params, cacique_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 34
    cacique_effect_id = tech.effect_id
    cacique_barrack_id = append_tech(data, tech)

    # Herbalism
    herb_id = 1365
    tech = get_ut(data, params, herb_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 34
    tech.icon_id = constants.SQUIRES_ICON_ID
    herb_effect_id = tech.effect_id
    herb_barrack_id = append_tech(data, tech)

    # name = 'Tower Shields'
    ts_id = 692
    tech = get_ut(data, params, ts_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.INFANTRY_ARMOR_ICON_ID
    ts_effect_id = tech.effect_id
    ts_barrack_id = append_tech(data, tech)
    # Coiled Serpent Array
    tech = get_ut(data, params, csa_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 7
    csa_barrack_id = append_tech(data, tech)
    add_mutex(data, [csa_castle_id, csa_barrack_id], [csa_effect_id])
    # Helot Levies
    hl_id = 1130
    name = 'Helot Levies'
    tech = get_ut(data, params, hl_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 7
    hl_effect_id = tech.effect_id
    hl_barrack_id = append_tech(data, tech)
    # Sparabaras
    name = 'Sparabaras'
    tech.name = name
    tech = get_ut(data, params, sp_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 7
    sp_barrack_id = append_tech(data, tech)

    # Xyphos
    xyphos_id = 1132
    tech = get_ut(data, params, xyphos_id)
    tech.name = 'Xyphos'
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 8
    xyphos_barrack_id = append_tech(data, tech)
    # Eisphora
    tech = get_ut(data, params, 1122)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 8
    effect = get_new_effect('Eisphora')
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
    eis_tech_id, eis_effect_id = append_tech(data, tech, effect)
    name = 'Eisphora + Kshatriyas'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, eis_tech_id, ksha_id)
    effect = get_new_effect(name)
    new_food = new_food * constants.KSHATRIYAS_DISCOUNT
    for i in (hoplite_id, e_hoplite_id):
        set_unit_attribute(effect, i, -1, 103, new_food + new_gold * 0.33)
        set_unit_attribute(effect, i, -1, 105, new_gold * 0.67)
    append_tech(data, tech, effect)

    # Agoge
    name = 'Agoge'
    ago_id = 1131
    tech = get_ut(data, params, ago_id)
    tech.name = name
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 8
    ago_effect_id = tech.effect_id
    ago_barrack_id = append_tech(data, tech)

    # arquebus
    arq_id = 573
    tech = get_ut(data, params, arq_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 27
    tech.icon_id = constants.BALLISTICS_ICON_ID
    arq_effect_id = tech.effect_id
    effect = effects[arq_effect_id]
    origin_units = set(map(lambda command: command.a, effect.effect_commands))
    target_units = set(map(lambda command: command.a, effects[410].effect_commands))
    append_units = set()
    for i in target_units:
        projectile_unit = units[i].type_50.projectile_unit_id
        if projectile_unit != -1 and projectile_unit not in origin_units and projectile_unit not in append_units:
            plus_unit_attribute(effect, projectile_unit, -1, 5, 0.5)
            set_unit_attribute(effect, projectile_unit, -1, 19, 1)
            append_units.add(projectile_unit)
        second_projectile = units[i].creatable.secondary_projectile_unit
        if second_projectile and second_projectile != -1 and second_projectile not in origin_units and second_projectile not in append_units:
            plus_unit_attribute(effect, second_projectile, -1, 5, 0.5)
            plus_unit_attribute(effect, second_projectile, -1, 19, 3)
            append_units.add(second_projectile)
        charge_projectile_unit = units[i].creatable.charge_projectile_unit
        if charge_projectile_unit and charge_projectile_unit != -1 and charge_projectile_unit not in origin_units and charge_projectile_unit not in append_units:
            plus_unit_attribute(effect, charge_projectile_unit, -1, 5, 0.5)
            plus_unit_attribute(effect, charge_projectile_unit, -1, 19, 3)
            append_units.add(charge_projectile_unit)
    arq_barrack_id = append_tech(data, tech)
    # Wagenburg Tactics
    tech = get_ut(data, params, wa_ta_id)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    tech.research_locations[0].button_id = 27
    tech.icon_id = SQUIRES_ICON_ID
    wa_ta_barrack_id = append_tech(data, tech)

    # Pezhetairoi
    name = 'Pezhetairoi'
    tech = get_ut(data, params, 1286)
    tech.research_locations[0].location_id = constants.BARRACK_NUM
    pez_tech_id = append_tech(data, tech)
    pez_effect_id = tech.effect_id
    add_mutex(data, [sar_castle_id, pez_tech_id], [sar_effect_id, pez_effect_id])
    params.other_params['pez_tech_id'] = pez_tech_id

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in stable
    append_tech(data, get_new_tech('----Stable UTs----'), get_new_effect('----Stable UTs----'))
    # name = 'Chivalry'
    tech = get_ut(data, params, 493)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    tech.icon_id = constants.CONSCRIPTION_ICON_ID
    append_tech(data, tech)
    # name = 'Farimba'
    tech = get_ut(data, params, 577)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)
    # name = 'Stirrups'
    tech = get_ut(data, params, 685)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)
    # Ming Guang Armor
    mga_id = 1062
    tech = get_ut(data, params, mga_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    mga_effect_id = tech.effect_id
    mga_stable_id = append_tech(data, tech)
    # name = 'Manipur Cavalry'
    tech = get_ut(data, params, 627)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    append_tech(data, tech)
    # Aznauri Cavalry
    azn_id = 924
    tech = get_ut(data, params, azn_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    azn_effect_id = tech.effect_id
    azn_stable_id = append_tech(data, tech)
    # Sagaris
    sagaris_id = 1113
    tech = get_ut(data, params, sagaris_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    sagaris_effect_id = tech.effect_id
    sagaris_stable_id = append_tech(data, tech)
    # Ordo Cavalry
    oc_id = 1007
    tech = get_ut(data, params, oc_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 12
    append_tech(data, tech)

    # name = 'Tusk Swords'
    tech = get_ut(data, params, 622)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 14
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)
    # name = 'Howdah'
    tech = get_ut(data, params, 626)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 14
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    append_tech(data, tech)
    # name = 'Chatras'
    tech = get_ut(data, params, 628)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 14
    tech.icon_id = constants.BLOODLINE_ICON_ID
    append_tech(data, tech)

    # medical corps
    me_co_id = 831
    tech = get_ut(data, params, me_co_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 9
    me_co_effect_id = tech.effect_id
    effect = effects[me_co_effect_id]
    original_units = set(map(lambda command: command.a, effect.effect_commands))
    extend_units = []
    for unit in elephant_units:
        if unit not in original_units:
            extend_units.append(unit)
    extend_effect(effect, extend_units)
    me_co_stable_id = append_tech(data, tech)
    # Paiks
    tech = get_ut(data, params, paiks_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 9
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    tech.effect_id = paiks_effect_id
    paiks_stable_id = append_tech(data, tech)


    # name = 'Lechitic Legacy'
    tech = get_ut(data, params, 783)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    append_tech(data, tech)

    # Silk Armor
    si_ar_id = 687
    tech = get_ut(data, params, si_ar_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 11
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    si_ar_effect_id = tech.effect_id
    si_ar_stable_id = append_tech(data, tech)
    # Steppe Husbandry
    st_hu_id = 689
    tech = get_ut(data, params, st_hu_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 11
    tech.icon_id = constants.CONSCRIPTION_ICON_ID
    st_hu_effect_id = tech.effect_id
    st_hu_stable_id = append_tech(data, tech)

    # Frontier Guards
    fr_gu_id = 836
    tech = get_ut(data, params, fr_gu_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 8
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    fr_gu_effect_id = tech.effect_id
    fr_gu_stable_id = append_tech(data, tech)

    # Maghrebi Camels
    tech = get_ut(data, params, ma_ca_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 13
    tech.effect_id = ma_ca_effect_id
    ma_ca_stable_id = append_tech(data, tech)
    add_mutex(data, [ma_ca_stable_id, ma_ca_castle_id], [ma_ca_effect_id])
    # Royal Heirs
    tech = get_ut(data, params, ro_he_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    tech.effect_id = ro_he_effect_id
    ro_he_stable_id = append_tech(data, tech)
    add_mutex(data, [ro_he_castle_id, ro_he_stable_id], [ro_he_effect_id])

    # name = 'Hauberk'
    tech = get_ut(data, params, 757)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    append_tech(data, tech)
    # name = 'Szlachta Privileges'
    tech = get_ut(data, params, 782)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 7
    append_tech(data, tech)
    # Comitatenses
    tech = get_ut(data, params, comitatenses_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 7
    tech.effect_id = comitatenses_effect_id
    comitatenses_stable_id = append_tech(data, tech)
    add_mutex(data, [comitatenses_castle_id, comitatenses_barrack_id, comitatenses_stable_id], [comitatenses_effect_id])
    # Bessian Metalworking
    tech = get_ut(data, params, be_me_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 7
    be_me_stable_id = append_tech(data, tech)

    name = 'enable Marauders'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, 266)
    effect = get_new_effect(name)
    tech_id = 483
    force_tech(effect, tech_id)
    move_tech_building(effect, tech_id, constants.STABLE_NUM)
    for i in (755, 757):
        move_unit_button(effect, i, 21, 1)
    append_tech(data, tech, effect)

    # Scythed Chariots
    sc_id = 1112
    tech = get_ut(data, params, sc_id)
    tech.name = 'Scythed Chariots'
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 32
    sc_effect_id = tech.effect_id
    sc_tech_id = append_tech(data, tech)
    add_mutex(data, [sagaris_stable_id, sc_tech_id], [sc_effect_id, sagaris_effect_id])

    # Vadhavadha
    vad_id = 1307
    tech = get_ut(data, params, vad_id)
    tech.research_locations[0].location_id = constants.STABLE_NUM
    tech.research_locations[0].button_id = 28
    vad_effect_id = tech.effect_id
    vad_stable_id = append_tech(data, tech)
    add_mutex(data, [lsh_castle_id, vad_stable_id], [lsh_effect_id, vad_effect_id])

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in archery ranges
    append_tech(data, get_new_tech('----Archery UTs----'), get_new_effect('----Archery UTs----'))
    # name = 'Recurve Bow'
    tech = get_ut(data, params, 515)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.BRACER_ICON_ID
    append_tech(data, tech)
    # Silk Armor
    tech = get_ut(data, params, si_ar_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.CAVALRY_ARMOR_ICON_ID
    tech.effect_id = si_ar_effect_id
    si_ar_archery_id = append_tech(data, tech)
    add_mutex(data, [si_ar_stable_id, si_ar_archery_id], [si_ar_effect_id])
    # name = 'Sipahi'
    tech = get_ut(data, params, 491)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.BLOODLINE_ICON_ID
    append_tech(data, tech)
    # Ming Guang Armor
    tech = get_ut(data, params, mga_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.ARCHER_ARMOR_ICON_ID
    tech.effect_id = mga_effect_id
    mga_archery_id = append_tech(data, tech)
    add_mutex(data, [mga_stable_id, mga_archery_id], [mga_effect_id])
    # Aznauri Cavalry
    tech = get_ut(data, params, azn_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 13
    tech.effect_id = azn_effect_id
    azn_archery_id = append_tech(data, tech)
    add_mutex(data, [azn_stable_id, azn_archery_id], [azn_effect_id])

    # Paiks
    tech = get_ut(data, params, paiks_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 28
    tech.icon_id = constants.BRACER_ICON_ID
    tech.effect_id = paiks_effect_id
    paiks_archery_id = append_tech(data, tech)
    # Medical corps
    tech = get_ut(data, params, me_co_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 28
    tech.effect_id = me_co_effect_id
    me_co_archery_id = append_tech(data, tech)
    # Frontier Guards
    tech = get_ut(data, params, fr_gu_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 28
    tech.icon_id = constants.ARCHER_ARMOR_ICON_ID
    tech.effect_id = fr_gu_effect_id
    fr_gu_archery_id = append_tech(data, tech)
    add_mutex(data, [fr_gu_stable_id, fr_gu_archery_id], [fr_gu_effect_id])

    # arquebus
    tech = get_ut(data, params, arq_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 14
    tech.icon_id = constants.BALLISTICS_ICON_ID
    arq_archery_id = append_tech(data, tech)
    # Wagenburg Tactics
    tech = get_ut(data, params, wa_ta_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 14
    tech.effect_id = wa_ta_effect_id
    wa_ta_archery_id = append_tech(data, tech)

    # name = 'Shatagni'
    tech = get_ut(data, params, 507)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 9
    tech.icon_id = constants.BRACER_ICON_ID
    append_tech(data, tech)
    # Pirotechnia
    tech = get_ut(data, params, 902)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 9
    append_tech(data, tech)

    name = 'Kamandaran'
    tech = get_ut(data, params, 488)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.GUILDS_ICON_ID
    effect = get_new_effect(name)
    wood = 25 * MAYAN_AGE3_DISCOUNT * KOREANS_SOLDIER_DISCOUNT  # Mayans, Koreans
    gold = 45 * MAYAN_AGE3_DISCOUNT * PORTGUESE_DISCOUNT  # Mayans, Portuguese
    kama_effect = effects[tech.effect_id]
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
    tech_id, effect_id = append_tech(data, tech, effect)
    name = 'Kamandaran Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, tech_id)
    effect = get_new_effect(name)
    wood = 25 * MAYAN_AGE4_DISCOUNT * KOREANS_SOLDIER_DISCOUNT  # Mayans, Koreans
    gold = 45 * MAYAN_AGE4_DISCOUNT * PORTGUESE_DISCOUNT  # Mayans, Portuguese
    wood += gold * wood_cost / gold_cost
    set_unit_attribute(effect, 4, -1, 104, wood)
    set_unit_attribute(effect, 24, -1, 104, wood)
    set_unit_attribute(effect, 492, -1, 104, wood)
    append_tech(data, tech, effect)
    # Bogsveigar
    bog_id = 49
    tech = get_ut(data, params, bog_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.BRACER_ICON_ID
    bog_effect_id = tech.effect_id
    bog_archery_id = append_tech(data, tech)

    # Bolt Magazine
    bm_id = 1069
    tech = get_ut(data, params, bm_id)
    bm_effect_id = tech.effect_id
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.BRACER_ICON_ID
    bm_archery_id = append_tech(data, tech)

    # Yeomen
    yeo_id = 3
    tech = get_ut(data, params, yeo_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 11
    tech.icon_id = constants.BRACER_ICON_ID
    yeo_effect_id = tech.effect_id
    yeo_archery_id = append_tech(data, tech)
    # Curare
    tech = get_ut(data, params, cur_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 11
    cur_archery_id = append_tech(data, tech)
    # Herbalism
    tech = get_ut(data, params, herb_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 11
    herb_archery_id = append_tech(data, tech)
    add_mutex(data, [herb_barrack_id, herb_archery_id], [herb_effect_id])

    name = 'Reed Arrows'
    ra_id = 1111
    tech = get_ut(data, params, ra_id)
    tech.name = name
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 11
    effect = effects[tech.effect_id]
    unique_foot_archer_ids = list(map(lambda x: x.id, filter(
        lambda x: x and x.class_ == 0 and x.creatable and constants.CASTLE_NUM in list(
            map(lambda x: x.unit_id, x.creatable.train_locations)),
        units)))
    for i in unique_foot_archer_ids:
        if i not in (2174, 2175):
            multiply_unit_attribute(effect, i, -1, 10, 0.8)
    ra_effect_id = tech.effect_id
    ra_archery_id = append_tech(data, tech)

    # Steppe Husbandry
    tech = get_ut(data, params, st_hu_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 8
    tech.icon_id = constants.CONSCRIPTION_ICON_ID
    tech.effect_id = st_hu_effect_id
    st_hu_archery_id = append_tech(data, tech)
    add_mutex(data, [st_hu_stable_id, st_hu_archery_id], [st_hu_effect_id])

    # Huaracas
    hua_id = 1366
    tech = get_ut(data, params, hua_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 26
    tech.icon_id = constants.BRACER_ICON_ID
    append_tech(data, tech)
    # Cacique
    tech = get_ut(data, params, cacique_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 26
    cacique_archery_id = append_tech(data, tech)
    add_mutex(data, [cacique_barrack_id, cacique_archery_id], [cacique_effect_id])
    # Fabric Shields
    tech = get_ut(data, params, fs_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 26
    tech.icon_id = constants.ARCHER_ARMOR_ICON_ID
    tech.effect_id = fs_effect_id
    fs_archery_id = append_tech(data, tech)
    add_mutex(data, [fs_castle_id, fs_barrack_id, fs_archery_id], [fs_effect_id])

    # name = 'Atlatl'
    tech = get_ut(data, params, 460)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.BRACER_ICON_ID
    append_tech(data, tech)
    # name = "Hul'che Javelineers"
    tech = get_ut(data, params, 485)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.BRACER_ICON_ID
    append_tech(data, tech)
    # Peltasts
    tech = get_ut(data, params, 1299)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.BRACER_ICON_ID
    pel_archery_id = append_tech(data, tech)
    pel_effect_id = tech.effect_id
    add_mutex(data, [be_me_castle_id, be_me_barrack_id, be_me_stable_id, pel_archery_id], [be_me_effect_id, pel_effect_id])
    # Tower Shields
    tech = get_ut(data, params, ts_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.ARCHER_ARMOR_ICON_ID
    tech.effect_id = ts_effect_id
    ts_archery_id = append_tech(data, tech)
    add_mutex(data, [ts_barrack_id, ts_archery_id], [ts_effect_id])
    # Lamellar Armor
    tech = get_ut(data, params, la_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 7
    la_archery_id = append_tech(data, tech)
    add_mutex(data, [la_barrack_id, la_archery_id], [la_effect_id])
    # Helot Levies
    tech = get_ut(data, params, hl_id)
    tech.name = 'Helot Levies'
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 7
    hl_archery_id = append_tech(data, tech)

    # name = 'Andean Sling'
    tech = get_ut(data, params, 516)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 12
    append_tech(data, tech)

    # Malon
    malon_id = 1379
    tech = get_ut(data, params, malon_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 12
    append_tech(data, tech)

    # Thunderclap Bombs
    tb_id = 997
    tech = get_ut(data, params, tb_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 32
    tb_effect_id = tech.effect_id
    tb_archery_id = append_tech(data, tech)

    # Butalmapu
    tech = get_ut(data, params, but_id)
    tech.research_locations[0].location_id = constants.ARCHERY_RANGE_NUM
    tech.research_locations[0].button_id = 34
    but_archery_id = append_tech(data, tech)
    add_mutex(data, [but_castle_id, but_archery_id], [but_effect_id])

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in siege workshop
    append_tech(data, get_new_tech('----Siege UTs----'), get_new_effect('----Siege UTs----'))
    # Paiks
    tech = get_ut(data, params, paiks_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 31
    tech.icon_id = constants.BLAST_FURNACE_ICON_ID
    tech.effect_id = paiks_effect_id
    paiks_siege_id = append_tech(data, tech)
    add_mutex(data, [paiks_castle_id, paiks_archery_id, paiks_stable_id, paiks_siege_id], [paiks_effect_id])
    # Medical Corps
    tech = get_ut(data, params, me_co_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 31
    tech.effect_id = me_co_effect_id
    me_co_siege_id = append_tech(data, tech)
    add_mutex(data, [me_co_archery_id, me_co_stable_id, me_co_siege_id], [me_co_effect_id])

    # name = 'Torsion Engines'
    tech = get_ut(data, params, 575)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 11
    effect = effects[tech.effect_id]
    for i in (1744, 1746, 1263, 1923):
        plus_unit_attribute(effect, i, -1, 22, 0.05)
    for i in (1962, 1980):
        plus_unit_attribute(effect, i, -1, 3, 0.3)
        plus_unit_attribute(effect, i, -1, 4, 0.3)
    append_tech(data, tech)
    # name = 'Drill'
    tech = get_ut(data, params, 6)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 11
    effect = effects[tech.effect_id]
    origin_class = set(map(lambda command: command.b, effect.effect_commands))
    origin_units = set(map(lambda command: command.a, effect.effect_commands))
    for i in siege_workshop_units:
        if units[i].class_ not in origin_class and i not in origin_units:
            multiply_unit_attribute(effect, i, -1, 5, 1.5)
    append_tech(data, tech)

    # Furor Celtica
    fc_tech = get_ut(data, params, 5)
    fc_tech.research_locations[0].location_id = constants.SIEGE_NUM
    fc_tech.research_locations[0].button_id = 11
    fc_effect = effects[fc_tech.effect_id]
    origin_units = set(map(lambda command: command.a, fc_effect.effect_commands))
    origin_class = set(map(lambda command: command.b, fc_effect.effect_commands))
    for i in siege_units:
        if i not in origin_units and units[i].class_ not in origin_class:
            multiply_unit_attribute(fc_effect, i, -1, 0, 1.4)
    append_tech(data, fc_tech)

    # name = 'Ironclad'
    tech = get_ut(data, params, 489)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 11
    effect = effects[tech.effect_id]
    origin_class = set(map(lambda command: command.b, effect.effect_commands))
    origin_units = set(map(lambda command: command.a, effect.effect_commands))
    for i in siege_units:
        if units[i].class_ not in origin_class and i not in origin_units:
            plus_unit_armor(effect, i, -1, 4, 4)
    append_tech(data, tech)

    # Artillery
    art_id = 10
    tech = get_ut(data, params, art_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 9
    tech.icon_id = constants.SIEGE_ENGINEERS_ICON_ID
    art_effect_id = tech.effect_id
    art_siege_id = append_tech(data, tech)

    # Arquebus
    tech = get_ut(data, params, arq_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 32
    tech.icon_id = constants.BALLISTICS_ICON_ID
    tech.effect_id = arq_effect_id
    arq_siege_id = append_tech(data, tech)
    add_mutex(data, [arq_barrack_id, arq_archery_id, arq_siege_id], [arq_effect_id])
    # Wagenburg Tactics
    tech = get_ut(data, params, wa_ta_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 32
    tech.effect_id = wa_ta_effect_id
    wa_ta_siege_id = append_tech(data, tech)
    add_mutex(data, [wa_ta_castle_id, wa_ta_barrack_id, wa_ta_archery_id, wa_ta_siege_id], [wa_ta_effect_id])

    # name = 'Shinkichon'
    shin_id = 445
    tech = get_ut(data, params, shin_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 27
    tech.icon_id = constants.SIEGE_ENGINEERS_ICON_ID
    shin_effect_id = tech.effect_id
    shin_siege_id = append_tech(data, tech)
    # Thunderclap Bombs
    tech = get_ut(data, params, tb_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 27
    tb_siege_id = append_tech(data, tech)

    # Counterweights
    tech = get_ut(data, params, cw_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 7
    tech.effect_id = cw_effect_id
    cw_siege_id = append_tech(data, tech)
    add_mutex(data, [cw_castle_id, cw_siege_id], [cw_effect_id])

    # Double Crossbow
    tech = get_ut(data, params, dc_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 8
    tech.effect_id = dc_effect_id
    dc_siege_id = append_tech(data, tech)
    add_mutex(data, [dc_castle_id, dc_siege_id], [dc_effect_id])
    # Rocketry
    roc_id = 52
    tech = get_ut(data, params, roc_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 8
    roc_effect_id = tech.effect_id
    roc_siege_id = append_tech(data, tech)
    # Ballistas
    bal_id = 883
    tech = get_ut(data, params, bal_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 8
    tech.icon_id = constants.SIEGE_ENGINEERS_ICON_ID
    bal_effect_id = tech.effect_id
    bal_siege_id = append_tech(data, tech)

    # Bolt Magazine
    tech = get_ut(data, params, bm_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 28
    bm_siege_id = append_tech(data, tech)

    # Sitting Tiger
    sit_t_id = 1081
    tech = get_ut(data, params, sit_t_id)
    tech.research_locations[0].location_id = constants.SIEGE_NUM
    tech.research_locations[0].button_id = 29
    sit_t_siege_id = append_tech(data, tech)
    sit_t_effect_id = tech.effect_id

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in University
    append_tech(data, get_new_tech('----University UTs----'), get_new_effect('----University UTs----'))
    name = 'Detinets'
    tech = get_ut(data, params, 455)
    tech.research_locations[0].location_id = constants.UNIV_NUM
    tech.research_locations[0].button_id = 7
    tech.icon_id = constants.GUILDS_ICON_ID
    inca_discount = 0.85
    malian_discount = 0.85
    effect = get_new_effect(name)
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
    tech_id, effect_id = append_tech(data, tech, effect)

    unit = units[constants.DONJON_ID]
    costs = unit.creatable.resource_costs
    stone = costs[0].amount * inca_discount
    wood = costs[1].amount * malian_discount
    new_stone = stone * 0.6
    new_wood = wood + stone * 0.4
    set_unit_attribute(effect, DONJON_ID, -1, 104, new_wood)
    set_unit_attribute(effect, DONJON_ID, -1, 106, new_stone)

    name = 'Detinets Imp'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, tech_id)
    effect = get_new_effect(name)
    stone = 650 * inca_discount * 0.75
    set_unit_attribute(effect, 82, -1, 104, stone * 0.4)
    set_unit_attribute(effect, 82, -1, 106, stone * 0.6)
    append_tech(data, tech, effect)

    # Fortified Bastions
    fb_tech_id = 996
    tech = get_ut(data, params, fb_tech_id)
    tech.research_locations[0].location_id = constants.UNIV_NUM
    tech.research_locations[0].button_id = 1
    append_tech(data, tech)
    effect = effects[tech.effect_id]
    origin_units = list(map(lambda command: command.a, effect.effect_commands))

    # Circumnavigation
    circum_tech_id = 1404
    tech = get_ut(data, params, circum_tech_id)
    tech.research_locations[0].location_id = constants.UNIV_NUM
    tech.research_locations[0].button_id = 13
    tech.icon_id = constants.SHIPWRIGHT_ICON_ID
    append_tech(data, tech)
    for i in constants.TC_IDS:
        if i not in origin_units:
            plus_unit_attribute(effect, i, -1, 109, 500)
    if 1251 not in origin_units:
        plus_unit_attribute(effect, 1251, -1, 109, 500)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in tower
    append_tech(data, get_new_tech('----Tower UTs----'), get_new_effect('----Tower UTs----'))
    # name = 'Eupseong'
    tech = get_ut(data, params, 486)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 1
    tech.icon_id = constants.BRACER_ICON_ID
    append_tech(data, tech)
    # name = 'Yasama'
    tech = get_ut(data, params, 484)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 2
    tech.icon_id = constants.ARROWSLITS_ICON_ID
    append_tech(data, tech)
    # stronghold
    tech = get_ut(data, params, sh_id)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 3
    tech.effect_id = sh_effect_id
    sh_tower_id = append_tech(data, tech)
    add_mutex(data, [sh_castle_id, sh_tower_id], [sh_effect_id])
    # Svan Towers
    tech = get_ut(data, params, st_id)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 4
    tech.icon_id = constants.ARROWSLITS_ICON_ID
    tech.effect_id = st_effect_id
    st_tower_id = append_tech(data, tech)
    add_mutex(data, [st_castle_id, st_tower_id], [st_effect_id])
    name = 'Fortified Church + Svan Towers'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, st_castle_id, st_tower_id)
    tech.required_tech_count = 2
    tech.effect_id = 943
    append_tech(data, tech)
    name = 'Svan Towers + Chemistry'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, st_castle_id, st_tower_id)
    tech.required_tech_count = 2
    tech.effect_id = 940
    append_tech(data, tech)
    # Yeomen
    tech = get_ut(data, params, yeo_id)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 6
    tech.icon_id = constants.ARROWSLITS_ICON_ID
    tech.effect_id = yeo_effect_id
    yeo_tower_id = append_tech(data, tech)
    add_mutex(data, [yeo_archery_id, yeo_tower_id], [yeo_effect_id])
    # Great Wall
    tech = get_ut(data, params, 462)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 7
    gw_effect_id = tech.effect_id
    gw_tower_id = append_tech(data, tech)
    # Curare
    tech = get_ut(data, params, cur_id)
    tech.research_locations[0].location_id = constants.WATCH_TOWER_ID
    tech.research_locations[0].button_id = 8
    cur_tower_id = append_tech(data, tech)
    add_mutex(data, [cur_castle_id, cur_archery_id, cur_tower_id], [cur_effect_id])


    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in Bombard Tower
    append_tech(data, get_new_tech('----Bombard Tower UTs----'), get_new_effect('----Bombard Tower UTs----'))
    # Artillery
    tech = get_ut(data, params, art_id)
    tech.research_locations[0].location_id = constants.BOMBARD_TOWER_ID
    tech.research_locations[0].button_id = 1
    tech.icon_id = constants.SIEGE_ENGINEERS_ICON_ID
    tech.effect_id = art_effect_id
    art_bbt_id = append_tech(data, tech)
    # Greek Fire
    gre_id = 464
    tech = get_ut(data, params, gre_id)
    tech.research_locations[0].location_id = constants.BOMBARD_TOWER_ID
    tech.research_locations[0].button_id = 2
    gre_effect_id = tech.effect_id
    gre_bbt_id = append_tech(data, tech)
    # Great Wall
    tech = get_ut(data, params, 462)
    tech.research_locations[0].location_id = constants.BOMBARD_TOWER_ID
    tech.research_locations[0].button_id = 3
    gw_bbt_id = append_tech(data, tech)
    add_mutex(data, [gw_tower_id, gw_bbt_id], [gw_effect_id])

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in TC
    append_tech(data, get_new_tech('----TC UTs----'), get_new_effect('----TC UTs----'))
    name = 'Hill Forts'
    tech = get_ut(data, params, 691)
    tech.research_locations[0].location_id = constants.TC_NUM
    tech.research_locations[0].button_id = 10
    tech.icon_id = constants.BRACER_ICON_ID
    effect = get_new_effect(name)
    for i in constants.TC_IDS:
        plus_unit_attribute(effect, i, -1, 1, 3)
        plus_unit_attribute(effect, i, -1, 12, 3)
        plus_unit_attribute(effect, i, -1, 23, 3)
    append_tech(data, tech, effect)
    name = 'Tigui'
    tech = get_ut(data, params, 576)
    tech.research_locations[0].location_id = constants.TC_NUM
    tech.research_locations[0].button_id = 10
    tech.icon_id = constants.BRACER_ICON_ID
    effect = get_new_effect(name)
    for i in constants.TC_IDS:
        plus_unit_attribute(effect, i, -1, 102, 8)
        plus_unit_attribute(effect, i, -1, 107, 8)
    append_tech(data, tech, effect)

    # name = 'Supremacy'
    tech = get_ut(data, params, 440)
    tech.research_locations[0].location_id = constants.TC_NUM
    tech.research_locations[0].button_id = 11
    append_tech(data, tech)

    # Helot Levies
    tech = get_ut(data, params, hl_id)
    tech.research_locations[0].location_id = constants.TC_NUM
    tech.research_locations[0].button_id = 10
    hl_tc_id = append_tech(data, tech)
    name = '[FTT] helot levies and loom'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    move_tech_button(effect, hl_tc_id, 11)
    move_tech_button(effect, 22, 11)
    append_tech(data, tech, effect)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in Monastery
    append_tech(data, get_new_tech('----Monastery UTs----'),
                get_new_effect('----Monastery UTs----'))
    name = 'Hussite Reforms'
    tech = get_ut(data, params, 785)
    tech.research_locations[0].location_id = constants.MONESTARY_NUM
    tech.research_locations[0].button_id = 21
    tech.icon_id = constants.GUILDS_ICON_ID
    effect = get_new_effect(name)
    for i, tech1 in enumerate(techs):
        if len(tech1.research_locations) == 0:
            continue
        research_location_id = tech1.research_locations[0].location_id
        research_button_id = tech1.research_locations[0].button_id
        if research_location_id == constants.MONESTARY_NUM and research_button_id > 0:
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
    for civ in data.civs:
        civ.units[775].creatable.resource_costs = (
            ResourceCost(3, 100, 1), ResourceCost(0, 0, 1), ResourceCost(4, 1, 1))
    set_unit_attribute(effect, 125, -1, 105, 0)
    set_unit_attribute(effect, 125, -1, 103, 80)
    set_unit_attribute(effect, 775, -1, 105, 0)
    set_unit_attribute(effect, 775, -1, 103, 80)
    cost = units[1811].creatable.resource_costs
    food = cost[0].amount * constants.INCA_AGE4_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    gold = cost[1].amount * constants.PORTGUESE_DISCOUNT * constants.GOTH_AGE4_DISCOUNT
    set_unit_attribute(effect, 1811, -1, 105, 0)
    set_unit_attribute(effect, 1811, -1, 103, food + gold)
    tech_id, effect_id = append_tech(data, tech, effect)
    name = 'Kshatriyas + Hussite Reforms'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, tech_id, ksha_id)
    effect = get_new_effect(name)
    food = food * constants.KSHATRIYAS_DISCOUNT
    set_unit_attribute(effect, 1811, -1, 103, food + gold)
    append_tech(data, tech, effect)

    # name = 'Inquisition'
    tech = get_ut(data, params, 492)
    tech.research_locations[0].location_id = constants.MONESTARY_NUM
    tech.research_locations[0].button_id = 22
    append_tech(data, tech)

    # name = 'Bimaristan'
    tech = get_ut(data, params, 28)
    tech.research_locations[0].location_id = constants.MONESTARY_NUM
    tech.research_locations[0].button_id = 23
    append_tech(data, tech)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in Docks
    append_tech(data, get_new_tech('----Dock UTs----'), get_new_effect('----Dock UTs----'))
    # Greek Fire
    tech = get_ut(data, params, gre_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 31
    tech.effect_id = gre_effect_id
    gre_dock_id = append_tech(data, tech)
    add_mutex(data, [gre_dock_id, gre_bbt_id], [gre_effect_id])
    # Greek Fire + Chemistry
    techs[465].required_techs = (47, 464, gre_bbt_id, gre_dock_id, -1, -1)

    # name = 'Cilician Fleet'
    tech = get_ut(data, params, 922)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 10
    append_tech(data, tech)

    name = 'enable Thalassocracy'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, 266)
    effect = get_new_effect(name)
    tha_tech_id = 624
    force_tech(effect, tha_tech_id)
    move_tech_button(effect, tha_tech_id, 10)
    move_tech_building(effect, tha_tech_id, constants.DOCK_NUM)
    append_tech(data, tech, effect)

    # Artillery
    tech = get_ut(data, params, art_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 14
    tech.icon_id = constants.SIEGE_ENGINEERS_ICON_ID
    tech.effect_id = art_effect_id
    art_dock_id = append_tech(data, tech)
    add_mutex(data, [art_siege_id, art_bbt_id, art_dock_id], [art_effect_id])
    # Bolt Magazine
    tech = get_ut(data, params, bm_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 14
    bm_dock_id = append_tech(data, tech)
    add_mutex(data, [bm_siege_id, bm_archery_id, bm_dock_id], [bm_effect_id])
    params.other_params['bm_dock_id'] = bm_dock_id
    # Rocketry
    tech = get_ut(data, params, roc_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 14
    roc_dock_id = append_tech(data, tech)
    add_mutex(data, [roc_siege_id, roc_dock_id], [roc_effect_id])
    params.other_params['roc_dock_id'] = roc_dock_id
    # rocketry + chemistry
    techs[1015].required_techs = (47, 52, roc_siege_id, roc_dock_id, -1, -1)
    # Sitting Tiger
    tech = get_ut(data, params, sit_t_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 14
    sit_t_dock_id = append_tech(data, tech)
    add_mutex(data, [sit_t_siege_id, sit_t_dock_id], [sit_t_effect_id])
    params.other_params['sit_t_dock_id'] = sit_t_dock_id
    # Thunderclap Bombs
    tech = get_ut(data, params, tb_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 14
    tb_dock_id = append_tech(data, tech)
    effect = effects[tech.effect_id]
    for command in effect.effect_commands:
        if command.type == 0 and command.a == 1948 and command.c == 107:
            command.type = 4
            command.d = 1
    add_mutex(data, [tb_archery_id, tb_siege_id, tb_dock_id], [tb_effect_id])
    params.other_params['tb_dock_id'] = tb_dock_id

    # Ballistas
    tech = get_ut(data, params, bal_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 12
    tech.icon_id = constants.BRACER_ICON_ID
    tech.effect_id = bal_effect_id
    bal_dock_id = append_tech(data, tech)
    add_mutex(data, [bal_siege_id, bal_dock_id], [bal_effect_id])

    # Bogsveigar
    tech = get_ut(data, params, bog_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 26
    tech.icon_id = constants.BRACER_ICON_ID
    tech.effect_id = bog_effect_id
    bog_dock_id = append_tech(data, tech)
    add_mutex(data, [bog_dock_id, bog_archery_id], [bog_effect_id])
    # Shinkichon
    tech = get_ut(data, params, shin_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 27
    shin_dock_id = append_tech(data, tech)
    add_mutex(data, [shin_dock_id, shin_siege_id], [shin_effect_id])

    # Red Cliffs Tactics
    tech = get_ut(data, params, rct_id)
    tech.research_locations[0].location_id = constants.DOCK_NUM
    tech.research_locations[0].button_id = 13
    rct_dock_id = append_tech(data, tech)
    add_mutex(data, [rct_dock_id, rct_castle_id], [rct_effect_id])

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in Market
    append_tech(data, get_new_tech('----Market UTs----'), get_new_effect('----Market UTs----'))
    # name = 'Silk Road'
    tech = get_ut(data, params, 499)
    tech.research_locations[0].location_id = constants.MARKET_NUM
    tech.research_locations[0].button_id = 4
    append_tech(data, tech)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UTs in Shipyard
    append_tech(data, get_new_tech('----Shipyard UTs----'), get_new_effect('----Shipyard UTs----'))
    # Reed Arrows
    tech = get_ut(data, params, ra_id)
    tech.name = 'Reed Arrows'
    tech.research_locations[0].location_id = constants.SHIPYARD_ID
    tech.research_locations[0].button_id = 7
    ra_shipyard_id = append_tech(data, tech)
    add_mutex(data, [ra_shipyard_id, ra_archery_id, sp_castle_id, sp_barrack_id], [ra_effect_id, sp_effect_id])

    # Xyphos
    tech = get_ut(data, params, xyphos_id)
    tech.name = 'Xyphos'
    tech.research_locations[0].location_id = constants.SHIPYARD_ID
    tech.research_locations[0].button_id = 6
    xyphos_shipyard_id = append_tech(data, tech)
    add_mutex(data, [xyphos_shipyard_id, xyphos_barrack_id, hl_barrack_id, hl_archery_id, hl_tc_id],
              [tech.effect_id, hl_effect_id])

    # Trierarchies
    tech = get_ut(data, params, 1121)
    tech.name = 'Trierarchies'
    tech.research_locations[0].location_id = constants.SHIPYARD_ID
    tech.research_locations[0].button_id = 6
    trier_shipyard_id = append_tech(data, tech)
    add_mutex(data, [trier_shipyard_id, tax_tech_id], [tech.effect_id, tax_effect_id])

    # Delian League
    delian_id = 1123
    tech = get_ut(data, params, delian_id)
    tech.name = 'Delian League'
    tech.research_locations[0].location_id = constants.SHIPYARD_ID
    tech.research_locations[0].button_id = 10
    tech_id = append_tech(data, tech)
    add_mutex(data, [eis_tech_id, tech_id], [eis_effect_id, tech.effect_id])

    # Peloponnesian League
    tech = get_ut(data, params, pl_id)
    tech.name = 'Peloponnesian League'
    tech.research_locations[0].location_id = constants.SHIPYARD_ID
    tech.research_locations[0].button_id = 11
    pl_shipyard_id = append_tech(data, tech)
    add_mutex(data, [pl_shipyard_id, pl_castle_id, ago_barrack_id], [tech.effect_id, ago_effect_id])
    name = 'Peloponnesian League + Grand Trunk Road'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, pl_castle_id, pl_shipyard_id, grand_trunk_road_id)
    tech.required_tech_count = 2
    effect = get_new_effect(name)
    multiply_resource(effect, 521, 1.1)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # UT in OutPost
    append_tech(data, get_new_tech('----OutPost UTs----'), get_new_effect('----OutPost UTs----'))
    # Ends of the World
    tech = get_ut(data, params, 1285)
    tech.research_locations[0].location_id = constants.OUTPOST_ID
    tech.research_locations[0].button_id = 6
    append_tech(data, tech)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())
    print('Unique tech added.')
