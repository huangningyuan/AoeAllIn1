import copy

from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost
from genieutils.unit import BuildingAnnex, AttackOrArmor

import constants
from all_in_1_params import All_In_1_Params
from constants import BLOODLINE_ID, TC_IDS, gunpowder_units, siege_workshop_units, siege_units, \
    ELITE_TEMPLE_GUARD_TECH_ID, ROMAN_CIV_WORK_RATE, FRANKS_FORAGER_WORK_RATE, MAPUCHE_FORAGER_WORK_RATE, MONESTARY_NUM
from ftt import move_tech_button
from ftt import move_unit_button
from utils import disable_tech, extend_effect, force_research_tech, disable_unit
from utils import enable_unit
from utils import force_tech
from utils import get_new_effect
from utils import get_new_tech
from utils import replace_tuple
from utils import set_require_techs, get_tech_id_by_name, set_tech_cost, plus_resource, set_tech_time, \
    multiply_unit_cost, multiply_unit_attack, multiply_unit_hp, multiply_unit_attribute, multiply_resource, \
    set_unit_attribute, plus_unit_armor, set_resource, upgrade_unit, research_tech, plus_unit_attribute, enable_tech, \
    set_tech_discount, set_tech_time_discount, append_tech


def deal_custom_bonus(data: DatFile, params: All_In_1_Params, civ_name):
    reverse_tech_ids = list()
    techs = data.techs
    effects = data.effects
    units = data.civs[0].units
    match civ_name:
        case 'Achaemenids':
            name = 'Achaemenids Bonuses'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for command in effects[1103].effect_commands:
                if command.a not in (254, 428):
                    effect.effect_commands.append(command)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'enable War Chariot'
            e_war_chariot_tech_id = 1171
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1169)
            research_tech(effect, 1169)
            disable_tech(effect, e_war_chariot_tech_id)
            append_tech(data, tech, effect)
            append_tech_tech_id = 1138
            achaemenids_tech_id = 1103
            name = 'Achaemenids or All in 1'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, achaemenids_tech_id)
            tech.required_tech_count = 1
            tech_id = append_tech(data, tech)
            # enable Achaemenids TC techs
            for i in range(1195, 1198):
                techs[i].required_techs = replace_tuple(techs[i].required_techs, append_tech_tech_id, -1)
                techs[i].required_techs = replace_tuple(techs[i].required_techs, achaemenids_tech_id, tech_id)
                techs[i].required_tech_count -= 1
            name = 'Elite War Chariot'
            tech = copy.deepcopy(techs[e_war_chariot_tech_id])
            tech.civ = -1
            tech.research_locations[0].button_id = 32
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, e_war_chariot_tech_id)
            research_tech(effect, e_war_chariot_tech_id)
            append_tech(data, tech, effect)
            name = 'enable dock, port'
            append_tech_ship_upgrade_tech_ids = [1144, 1145, 1146, 1148, 1149, 1151, 1152, 1154, 1155, 1159]
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, constants.DOCK_NUM)
            set_unit_attribute(effect, constants.PORT_NUM, -1, 58, -1)
            enable_unit(effect, constants.PORT_NUM)
            force_tech(effect, 1143)
            research_tech(effect, 1143)
            append_tech(data, tech, effect)
            name = 'enable dock techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, append_tech_tech_id)
            effect = get_new_effect(name)
            for command in effects[1145].effect_commands:
                if command.type == 102:
                    enable_tech(effect, int(command.d))
            append_tech_dock_tech_id, effect_id = append_tech(data, tech, effect)
            name = 'enable Feudal units'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, constants.SHIPYARD_ID)
            force_tech(effect, 1147)
            research_tech(effect, 1147)
            force_tech(effect, 1150)
            research_tech(effect, 1150)
            force_tech(effect, 1153)
            research_tech(effect, 1153)
            force_tech(effect, 384)
            append_tech(data, tech, effect)
            name = 'enable Castle units'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1158)
            force_research_tech(effect, 426)
            force_research_tech(effect, 630)
            force_research_tech(effect, 837)
            force_research_tech(effect, 480)
            append_tech(data, tech, effect)
            tech = get_new_tech('Macedonians')
            tech.civ = 54
            macedonians_id = append_tech(data, tech)
            tech = get_new_tech('Thracians')
            tech.civ = 55
            thracians_id = append_tech(data, tech)
            tech = get_new_tech('Puru')
            tech.civ = 56
            puru_id = append_tech(data, tech)
            name = 'any append_tech civ'
            tech = get_new_tech(name)
            set_require_techs(tech, 1258, 1259, 1260, macedonians_id, thracians_id, puru_id)
            tech.required_tech_count = 1
            any_append_tech_civ_tech_id = append_tech(data, tech)
            name = 'append_tech Gambesons'
            gambeson_tech_id = 875
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, any_append_tech_civ_tech_id)
            tech.required_tech_count = 3
            effect = get_new_effect(name)
            force_research_tech(effect, gambeson_tech_id)
            append_tech(data, tech, effect)
            name = 'free append_tech paragons'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, any_append_tech_civ_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1173)
            research_tech(effect, 1174)
            append_tech(data, tech, effect)
            name = 'append_tech siege onagers'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, 257, any_append_tech_civ_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 320)
            append_tech(data, tech, effect)

            name = 'enable Imp units'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1160)
            research_tech(effect, 172)
            research_tech(effect, 188)
            enable_tech(effect, 481)
            force_tech(effect, 631)
            enable_tech(effect, 837)
            force_tech(effect, 236)
            force_tech(effect, 481)
            force_tech(effect, 838)
            force_research_tech(effect, 64)
            append_tech(data, tech, effect)
            for i in append_tech_ship_upgrade_tech_ids:
                tech = copy.deepcopy(techs[i])
                tech.civ = -1
                tech.required_techs = replace_tuple(techs[i].required_techs, append_tech_tech_id, params.switch_tech_id)
                if 101 in tech.required_techs:
                    tech.required_techs = replace_tuple(tech.required_techs, 101, params.feudal_duplicate_tech_id)
                elif 102 in tech.required_techs:
                    tech.required_techs = replace_tuple(tech.required_techs, 102, params.castle_duplicate_tech_id)
                elif 103 in tech.required_techs:
                    tech.required_techs = replace_tuple(tech.required_techs, 103, params.imp_duplicate_tech_id)
                effect = get_new_effect(tech.name)
                force_tech(effect, i)
                research_tech(effect, i)
                tech_id, effect_id = append_tech(data, tech, effect)
                disable_tech(effects[techs[append_tech_dock_tech_id].effect_id], tech_id)
            disable_tech(effect, 1167)
        case 'Armenians':
            name = 'Mule Cart'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            tech.effect_id = 944
            append_tech(data, tech)
            for i in range(942, 948):
                techs[i].required_techs = replace_tuple(techs[i].required_techs, -1, params.switch_tech_id)
            techs[957].civ = -1
            name = 'enable Priest Warrior'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1811)
            move_unit_button(effect, 1811, 13)
            append_tech(data, tech, effect)
        case 'Athenians':
            name = 'enable Athenians TC techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1202)
            force_tech(effect, 1203)
            force_tech(effect, 1204)
            append_tech(data, tech, effect)

            name = 'Athenians + Armenians Age2'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            multiply_resource(effect, 502, (1 + 0.2 * 1.4) / 1.2)
            append_tech(data, tech, effect)
            name = 'Athenians + Armenians Age3'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            multiply_resource(effect, 502, (1 + 0.1 * 1.4) / 1.1)
            append_tech(data, tech, effect)
            # Athenians lumberjack
            effect = effects[1119]
            for command in effect.effect_commands:
                if command.type == 1 and command.a == 502 and command.b == 0:
                    command.b = 1
                    break
        case 'Aztecs':
            name = '+50g'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 3, 50)
            tech_id, effect_id = append_tech(data, tech, effect)
            # reverse_tech_ids.append(tech_id)
            name = 'military units train faster ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (23, 44, 47):
                multiply_unit_attribute(effect, -1, i, 101, 1 / 1.15)
            append_tech(data, tech, effect)
            name = 'enable Eagle Warrior'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 433)
            append_tech(data, tech, effect)
            name = 'append_tech elite eagle warrior'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, 384)
            effect = get_new_effect(name)
            force_tech(effect, 434)
            append_tech(data, tech, effect)
        case 'Bengalis':
            effect = effects[865]
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            extend_units = []
            for unit in constants.elephant_units:
                if unit not in original_units:
                    extend_units.append(unit)
            extend_effect(effect, extend_units)
        case 'Berbers':
            name = 'ftt elite genitour'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            move_tech_button(effect, 599, 29)
            append_tech(data, tech, effect)
        case 'Bohemians':
            name = 'enable houfnice'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 787)
            append_tech(data, tech, effect)
        case 'Bulgarians':
            name = 'Free Champion'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            set_tech_cost(effect, 264, 0, 0)
            set_tech_cost(effect, 264, 3, 0)
            set_tech_time(effect, 264, 0)
            set_tech_cost(effect, 1174, 0, 0)
            set_tech_cost(effect, 1174, 3, 0)
            set_tech_time(effect, 1174, 0)
            append_tech(data, tech, effect)
            name = 'Cheap Siege Techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i, tech1 in enumerate(techs):
                if i > constants.TECH_NUM:
                    break
                if len(tech1.research_locations) == 0:
                    continue
                research_location_id = tech1.research_locations[0].location_id
                if research_location_id == constants.SIEGE_NUM:
                    set_tech_discount(effect, i, 0, 0.5)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'Cheap archery attack (Shu + Bulgarians)'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (199, 200, 201):
                for cost in techs[i].resource_costs:
                    if cost.type == 0:
                        set_tech_cost(effect, i, cost.type, cost.amount * 0.75 * 0.5)
            append_tech(data, tech, effect)
            name = 'Cheap cavalry armor'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (80, 81, 82):
                set_tech_discount(effect, i, 0, 0.5)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'enable konnik'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1254)
            append_tech(data, tech, effect)
        case 'Burgundians':
            effect = effects[794]
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in gunpowder_units:
                if i in origin_units:
                    continue
                for attack in data.civs[0].units[i].type_50.attacks:
                    multiply_unit_attack(effect, i, -1, 125, attack.class_)
            name = 'Cheap Stable Techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i, tech1 in enumerate(techs):
                if i > constants.TECH_NUM:
                    break
                if len(tech1.research_locations) == 0:
                    continue
                research_location_id = tech1.research_locations[0].location_id
                if research_location_id == constants.STABLE_NUM:
                    if i in (254, 428):
                        continue
                    set_tech_discount(effect, i, -1, 0.5)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'Cheap Eco Techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (1012, 1013, 1014):
                set_tech_discount(effect, i, 0, 0.67)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'Enable Flemish Millitia'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 773)
            move_unit_button(effect, 1699, 31)
            append_tech(data, tech, effect)
            name = 'Feudal Gillnets'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id, 906)
            effect = get_new_effect(name)
            force_tech(effect, 65)
            append_tech(data, tech, effect)
        case 'Burmese':
            name = 'Cheap Monastery Techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i, tech1 in enumerate(techs):
                if len(tech1.research_locations) == 0:
                    continue
                research_location_id = tech1.research_locations[0].location_id
                if research_location_id == constants.MONESTARY_NUM and i != 441:
                    set_tech_discount(effect, i, -1, 0.5)
            append_tech(data, tech, effect)
            name = 'Burmese TB'
            tech = get_new_tech(name)
            tech.effect_id = 651
            append_tech(data, tech)
            # attack type for manipur
            archer_armor_class = 15
            addtional_attack = AttackOrArmor(archer_armor_class, 0)
            for unit in units:
                if unit and unit.creatable and unit.class_ == 12 and len(unit.creatable.train_locations) > 0:
                    archer_attack_flag = False
                    for attack in unit.type_50.attacks:
                        if attack.class_ == archer_armor_class:
                            archer_attack_flag = True
                            break
                    if not archer_attack_flag:
                        for civ in data.civs:
                            civ.units[unit.id].type_50.attacks.append(addtional_attack)
        case 'Byzantines':
            name = 'Byzantines Imperial Camel Discount'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            multiply_unit_cost(effect, 207, -1, 0.75)
            append_tech(data, tech, effect)
        case 'Celts':
            # siege fire rate
            effect = effects[385]
            original_classes = set(map(lambda command: command.b, effect.effect_commands))
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in siege_units:
                if i not in original_units and units[i].class_ not in original_classes:
                    multiply_unit_attribute(effect, i, -1, 10, 0.8)
        case 'Chinese':
            name = '-200f, -50w'
            tech = get_new_tech(name)
            set_require_techs(tech, 639, 307, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 0, -200)
            plus_resource(effect, 1, -50)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'TC Pop and LoS ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (2275, 2276, 2277):
                set_unit_attribute(effect, i, -1, 21, 15)
                plus_unit_attribute(effect, i, -1, 1, 7)
                plus_unit_attribute(effect, i, -1, 23, 7)
            append_tech(data, tech, effect)
            name = 'enable Rocket Cart'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 979)
            move_unit_button(effect, 1904, 22)
            move_unit_button(effect, 1907, 22)
            move_tech_button(effect, 980, 27)
            append_tech(data, tech, effect)
            name = 'enable Dragon Ship'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, 246)
            tech.effect_id = 1010
            append_tech(data, tech)
            name = 'enable fire lancer'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 981)
            move_unit_button(effect, 1901, 22)
            move_unit_button(effect, 1903, 22)
            move_tech_button(effect, 982, 27)
            append_tech(data, tech, effect)
            name = 'Elite Fire Lancer'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 982)
            append_tech(data, tech, effect)

        case 'Cumans':
            name = 'Feudal Siege'
            tech = get_new_tech(name)
            set_require_techs(tech, params.feudal_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 49)
            append_tech(data, tech, effect)
        case 'Georgians':
            # Cavalry regeneration ext
            for i in (954, 961):
                extend_effect(effects[i], [1263])
        case 'Gurjaras':
            name = 'enable camel scout'
            tech = get_new_tech(name)
            set_require_techs(tech, params.feudal_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1755)
            append_tech(data, tech, effect)
            name = 'enable shrivamsha'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1751)
            move_unit_button(effect, 1751, 22)
            move_unit_button(effect, 1753, 22)
            move_tech_button(effect, 843, 27)
            append_tech(data, tech, effect)
            name = 'enable elite shrivamsha'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 843)
            append_tech(data, tech, effect)
            name = 'Herdable Garrison'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            effect.effect_commands = effects[871].effect_commands
            set_unit_attribute(effect, 1711, -1, 30, 16)
            set_unit_attribute(effect, 1720, -1, 30, 16)
            set_unit_attribute(effect, 1734, -1, 30, 16)
            set_unit_attribute(effect, 1711, -1, 2, 10)
            set_unit_attribute(effect, 1720, -1, 2, 10)
            set_unit_attribute(effect, 1734, -1, 2, 10)
            append_tech(data, tech, effect)
            # tb elephant ext
            effect = effects[843]
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            extend_units = []
            for unit in constants.elephant_units:
                if unit not in original_units:
                    extend_units.append(unit)
            extend_effect(effect, extend_units)
        case 'Hindustanis':
            # gunpowder +armor ext
            effect = effects[576]
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            extend_units = list()
            for i in gunpowder_units:
                if i not in origin_units:
                    extend_units.append(i)
                    # plus_unit_armor(effect, i, -1, 1, 3)
                    # plus_unit_armor(effect, i, -1, 1, 4)
            extend_effect(effect, extend_units)
            name = 'enable Imperial Camel Rider'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 236)
            effect = get_new_effect(name)
            force_tech(effect, 521)
            append_tech(data, tech, effect)
        case 'Huns':
            name = '-100w'
            tech = get_new_tech(name)
            set_require_techs(tech, 639, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 1, -100)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            techs[241].civ = -1
            techs[242].civ = -1
            effect = effects[231]
            disable_tech(effect, get_tech_id_by_name(data, 'Start w/ Horse'))
        case 'Incas':
            name = 'enable slinger'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 185)
            move_unit_button(effect, 185, 21)
            append_tech(data, tech, effect)
            name = 'enable settlement'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 2556)
            enable_unit(effect, 68)
            disable_tech(effect, 1353)
            move_unit_button(effect, 2556, 1)
            append_tech(data, tech, effect)
            name = 'Settlement Age2 upgrade'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1354)
            append_tech(data, tech, effect)
            name = 'Settlement Age3 upgrade'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1355)
            append_tech(data, tech, effect)
            name = 'Settlement Age4 upgrade'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1356)
            append_tech(data, tech, effect)
            name = 'enable Champi'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 2550)
            enable_unit(effect, 74)
            move_unit_button(effect, 2550, 33)
            move_unit_button(effect, 2588, 33)
            move_unit_button(effect, 2552, 33)
            move_unit_button(effect, 2554, 33)
            append_tech(data, tech, effect)
            name = 'Champi Runner'
            champi_runner_tech_id = 1402
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, champi_runner_tech_id)
            move_tech_button(effect, champi_runner_tech_id, 34)
            append_tech(data, tech, effect)
            name = 'Champi Warrior'
            champi_warrior_tech_id = 1351
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, champi_runner_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, champi_warrior_tech_id)
            move_tech_button(effect, champi_warrior_tech_id, 34)
            append_tech(data, tech, effect)
            name = 'Elite Champi Warrior'
            elite_champi_warrior_tech_id = 1352
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, champi_runner_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, elite_champi_warrior_tech_id)
            move_tech_button(effect, elite_champi_warrior_tech_id, 34)
            append_tech(data, tech, effect)
        case 'Italians':
            # cheap gunpowder units ext
            effect = effects[555]
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in gunpowder_units:
                if i in original_units:
                    continue
                multiply_unit_cost(effect, i, -1, 0.8)
        case 'Japanese':
            name = 'Cheap Gather Building ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            multiply_unit_cost(effect, 1808, -1, 0.5)
            multiply_unit_cost(effect, 1711, -1, 0.5)
            multiply_unit_cost(effect, 1720, -1, 0.5)
            multiply_unit_cost(effect, 1734, -1, 0.5)
            append_tech(data, tech, effect)
        case 'Jurchens':
            name = 'enable Grenadier'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 992)
            move_unit_button(effect, 1911, 31)
            append_tech(data, tech, effect)
            name = 'cheap Siege and Defensive techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (239, 980, 321, 379):
                set_tech_discount(effect, i, 1, 0.25)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'cheap Siege techs ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (257, 320):
                set_tech_discount(effect, i, 1, 0.25)
            append_tech(data, tech, effect)
        case 'Khitans':
            name = '[FTT] pastures'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            move_unit_button(effect, 1889, 1)
            set_unit_attribute(effect, 1889, -1, 58, -1)
            append_tech(data, tech, effect)
            name = 'enable Mounted Trebuchet'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1005)
            move_unit_button(effect, 1923, 34)
            append_tech(data, tech, effect)
            name = 'enable Domestication'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1014)
            append_tech(data, tech, effect)
            name = 'enable Pastoralism'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1013)
            append_tech(data, tech, effect)
            name = 'enable Transhumance'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1012)
            append_tech(data, tech, effect)
        case 'Lithuanians':
            name = '+100f'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 0, 100)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            # relic attack
            tech = techs[699]
            set_require_techs(tech, 676, 107, params.switch_tech_id)
            tech.required_tech_count = 2
            tech.civ = -1
            techs[700].civ = -1
            techs[701].civ = -1
            techs[702].civ = -1
            # winged hussar
            techs[786].required_techs = replace_tuple(techs[786].required_techs, -1, params.imp_duplicate_tech_id)
        case 'Macedonians':
            # doctrines
            name = 'disable doctrines'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            tech.civ = 54
            effect = get_new_effect(name)
            for i in range(1275, 1284):
                disable_tech(effect, i)
                move_tech_button(effect, i, -1)
            append_tech(data, tech, effect)
            # siege ext
            effect = effects[1220]
            original_classes = set(map(lambda command: command.b, effect.effect_commands))
            for i in siege_units:
                if units[i].class_ not in original_classes:
                    plus_unit_armor(effect, i, -1, 1, 3)
                    multiply_unit_attack(effect, i, -1, 130, 11)
            name = 'enable Phalangite'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1290)
            move_unit_button(effect, 2384, 31)
            append_tech(data, tech, effect)
            name = 'enable Elite Phalangite'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1291)
            move_tech_button(effect, 1291, -1)
            append_tech(data, tech, effect)
            # Druzhina + Phalangite
            effect = effects[569]
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in (2384, 2385):
                if i not in original_units:
                    plus_unit_attribute(effect, i, -1, 22, -0.5)

        case 'Malians':
            # barrack unit +1 p armor ext
            origin_units = set(map(lambda command: command.a, effects[618].effect_commands))
            target_units = []
            for i, unit in enumerate(units):
                if unit and unit.creatable and constants.BARRACK_NUM in list(
                        map(lambda x: x.unit_id, unit.creatable.train_locations)) and i not in origin_units:
                    target_units.append(i)
            for i in (618, 619, 620):
                effect = effects[i]
                for j in target_units:
                    plus_unit_armor(effect, j, -1, 1, 3)
        case 'Mayans':
            origin_units = (763, 765)
            ext_units = list()
            name = 'Cheap Archers ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i, unit in enumerate(data.civs[1].units):
                if unit and unit.class_ == 0 and unit.creatable and constants.CASTLE_NUM in list(
                        map(lambda x: x.unit_id, unit.creatable.train_locations)) and i not in origin_units:
                    multiply_unit_cost(effect, i, -1, 0.9)
                    ext_units.append(i)
            append_tech(data, tech, effect)
            name = 'Cheap Archers castle ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in ext_units:
                multiply_unit_cost(effect, i, -1, 0.8 / 0.9)
            append_tech(data, tech, effect)
            name = 'Cheap Archers imp ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in ext_units:
                multiply_unit_cost(effect, i, -1, 0.7 / 0.8)
            append_tech(data, tech, effect)
            name = '-50f'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 0, -50)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
        case 'Mongols':
            name = 'remove origin Light Cavalry HP + BL'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_tech(effect, 286)
            disable_tech(effect, 287)
            disable_tech(effect, 288)
            disable_tech(effect, 388)
            append_tech(data, tech, effect)

            name = 'Light Cavalry +20% HP + BL'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id, BLOODLINE_ID)
            effect_with_bl_id = 286
            tech.effect_id = effect_with_bl_id
            tech_with_bl_id = append_tech(data, tech)
            disable_tech(effects[effect_with_bl_id], tech_with_bl_id)
            name = 'Light Cavalry +20% HP'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect_id = 288
            tech.effect_id = effect_id
            tech_id = append_tech(data, tech)
            disable_tech(effects[effect_id], tech_id)
            disable_tech(effects[effect_id], tech_with_bl_id)
            disable_tech(effects[effect_with_bl_id], tech_id)
            name = 'Light Cavalry +30% HP + BL'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id, BLOODLINE_ID)
            effect_with_bl_id = 287
            tech.effect_id = effect_with_bl_id
            tech_with_bl_id = append_tech(data, tech)
            disable_tech(effects[effect_with_bl_id], tech_with_bl_id)
            name = 'Light Cavalry +30% HP'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            effect_id = 387
            tech.effect_id = effect_id
            tech_id = append_tech(data, tech)
            disable_tech(effects[effect_id], tech_id)
            disable_tech(effects[effect_id], tech_with_bl_id)
            disable_tech(effects[effect_with_bl_id], tech_id)

        case 'Muisca':
            name = 'enable Bolas Rider'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 2569)
            move_unit_button(effect, 2569, 33)
            move_unit_button(effect, 2571, 33)
            append_tech(data, tech, effect)
            name = 'Elite Bolas Rider'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1378)
            move_tech_button(effect, 1378, 34)
            append_tech(data, tech, effect)
            name = 'enable Temple Guard'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1400)
            move_tech_button(effect, ELITE_TEMPLE_GUARD_TECH_ID, 32, 0)
            elite_temple_guard_tech = techs[ELITE_TEMPLE_GUARD_TECH_ID]
            elite_temple_guard_tech.research_locations.append(elite_temple_guard_tech.research_locations[0])
            elite_temple_guard_tech.research_locations[1].location_id = MONESTARY_NUM
            elite_temple_guard_tech.research_locations[1].button_id = 29
            for i in constants.TEMPLE_GUARD_IDS:
                move_unit_button(effect, i, 31, 0)
                move_unit_button(effect, i, 24, 1)
            append_tech(data, tech, effect)
            name = 'Elite Temple Guard'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, ELITE_TEMPLE_GUARD_TECH_ID)
            append_tech(data, tech, effect)
            # archer armor ext
            for i in (2301, 2302):
                plus_unit_attribute(effects[1369], i, -1, 4, 1)
        case 'Persians':
            name = '+50f +50w'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, 639, 307)
            effect = get_new_effect(name)
            plus_resource(effect, 0, 50)
            plus_resource(effect, 1, 50)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'Super Harbor'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            multiply_unit_hp(effect, 1189, -1, 2)
            append_tech(data, tech, effect)
            name = 'Castle Harbor +15%'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            multiply_unit_attribute(effect, 1189, -1, 13, 1.15)
            tech_id, effect_id = append_tech(data, tech, effect)
            name = 'Imp Harbor +20%'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, tech_id)
            effect = get_new_effect(name)
            multiply_unit_attribute(effect, 1189, -1, 13, 1.2 / 1.15)
            append_tech(data, tech, effect)
            name = 'enable Savar'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 209)
            effect = get_new_effect(name)
            force_tech(effect, 526)
            append_tech(data, tech, effect)
            disable_tech(effects[253], 526)
            disable_tech(effects[581], 265)
            name = 'enable Caravanserai'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1754)
            move_unit_button(effect, 1754, 3)
            append_tech(data, tech, effect)
            name = 'Super TC ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in range(2275, 2278):
                multiply_unit_hp(effect, i, -1, 2)
            append_tech(data, tech, effect)
        case 'Poles':
            name = 'Armenians + Poles Age1'
            tech = get_new_tech(name)
            set_require_techs(tech, 278, params.switch_tech_id)
            effect = get_new_effect('Armenians + Poles + Romans + Koreans Mining')
            multiply_resource(effect, 241, (1 + (0.15 * 1.4) / 1.15) * 1.05 * 1.2)
            disable_tech(effect, 806)
            disable_tech(effect, 807)
            tech_id, effect_id = append_tech(data, tech, effect)
            name = 'Armenians + Poles Age2'
            tech = get_new_tech(name)
            set_require_techs(tech, 279, params.switch_tech_id)
            tech.effect_id = effect_id
            append_tech(data, tech)
            name = 'Reverse Poles Stone Mining Gold'
            tech = get_new_tech(name)
            set_require_techs(tech, 806, params.switch_tech_id)
            tech.civ = 38
            effect = get_new_effect(name)
            multiply_resource(effect, 241, 1 / 1.15)
            append_tech(data, tech, effect)
            name = 'Disable origin Villager Regeneration'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_tech(effect, 792)
            disable_tech(effect, 809)
            disable_tech(effect, 810)
            disable_tech(effect, 811)
            append_tech(data, tech, effect)
            name = 'Villager Regeneration Feudal'
            tech = get_new_tech(name)
            set_require_techs(tech, params.feudal_duplicate_tech_id, params.switch_tech_id)
            tech.effect_id = 815
            append_tech(data, tech)
            append_tech(data, tech)
            name = 'Villager Regeneration Castle'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            tech.effect_id = 815
            append_tech(data, tech)
            name = 'Villager Regeneration Imp'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            tech.effect_id = 815
            append_tech(data, tech)
        case 'Portuguese':
            name = 'Foraging Wood'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            forager_wood_prod_rate = effects[510].effect_commands[0].d
            set_resource(effect, 267, forager_wood_prod_rate * ROMAN_CIV_WORK_RATE * FRANKS_FORAGER_WORK_RATE * MAPUCHE_FORAGER_WORK_RATE)
            append_tech(data, tech, effect)
            name = 'enable Feitoria'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1021)
            append_tech(data, tech, effect)
            # cheap conquisidator
            effect = effects[33]
            multiply_unit_cost(effect, -1, 23, 0.8)
        case 'Puru':
            name = 'Enable Sannahya'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1327)
            move_unit_button(effect, 2390, 23)
            move_unit_button(effect, 2391, 23)
            append_tech(data, tech, effect)
            name = 'elite Sannahya'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1328)
            move_tech_button(effect, 1328, 28)
            append_tech(data, tech, effect)
            # Remove Puru Emplacement
            effects[1266].effect_commands.pop(-1)
            effects[1267].effect_commands.pop(-1)
            name = 'Puru Defensive Emplacement'
            tech = get_new_tech(name)
            set_require_techs(tech, 1323)
            tech.civ = 56
            tech.repeatable = 1
            effect = get_new_effect(name)
            plus_unit_attribute(effect, 82, -1, 71, 1, 1)
            append_tech(data, tech, effect)
            name = 'Puru Offensive Emplacement'
            tech = get_new_tech(name)
            set_require_techs(tech, 1324)
            tech.civ = 56
            tech.repeatable = 1
            effect = get_new_effect(name)
            plus_unit_attribute(effect, 82, -1, 71, 2, 1)
            append_tech(data, tech, effect)
            name = 'Puru + Koreans + Romans Stone Mining food generation'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            multiply_resource(effect, 512, 1.2 * 1.05)
            append_tech(data, tech, effect)
            name = 'Cavalry Auras'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            for unit in units:
                if unit and unit.class_ == 12 and unit.type_50 and unit.type_50.break_off_combat > 0:
                    plus_unit_attribute(effect, unit.id, -1, 63, unit.type_50.break_off_combat)
            append_tech(data, tech, effect)
        case 'Romans':
            name = 'Legionary'
            tech = copy.deepcopy(techs[885])
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            tech.research_locations[0].button_id = 26
            tech.civ = -1
            tech.research_locations[0].research_time = 1
            tech.resource_costs = (
                ResearchResourceCost(-1, 0, 0), ResearchResourceCost(-1, 0, 0), ResearchResourceCost(-1, 0, 0))
            effect = get_new_effect(name)
            upgrade_unit(effect, 74, 1793, 0)
            upgrade_unit(effect, 75, 1793, 0)
            upgrade_unit(effect, 473, 1793, 0)
            upgrade_unit(effect, 77, 1793, 0)
            upgrade_unit(effect, 567, 1793, 0)
            plus_resource(effect, 3, -20)
            append_tech(data, tech, effect)
            name = 'enable Legionary'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1793)
            move_unit_button(effect, 1793, 21)
            disable_tech(effect, 885)
            append_tech(data, tech, effect)
        case 'Saracens':
            name = 'Disable Guilds'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_tech(effect, 15)
            append_tech(data, tech, effect)
        case 'Shu':
            name = 'Enable Shu War Chariot'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1962)
            move_unit_button(effect, 1962, 23)
            append_tech(data, tech, effect)
            name = 'Enable Liu Bei'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1066)
            research_tech(effect, 1066)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            # siege move speed ext
            original_classes = set(map(lambda command: command.b, effects[1072].effect_commands))
            original_units = set(map(lambda command: command.a, effects[1072].effect_commands))
            for i in (420, 691, 1795, 2140): # siege warships
                if i not in original_units and units[i].class_ not in original_classes:
                    multiply_unit_attribute(effects[1068], i, -1, 5, 1.1)
                    multiply_unit_attribute(effects[1072], i, -1, 5, 1.15 / 1.1)
            for i in siege_units:
                if i not in original_units and units[i].class_ not in original_classes:
                    multiply_unit_attribute(effects[1068], i, -1, 5, 1.1)
                    multiply_unit_attribute(effects[1072], i, -1, 5, 1.15 / 1.1)
            name = 'Enable Traction Trebuchets'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1025)
            move_unit_button(effect, 1942, 24)
            append_tech(data, tech, effect)
            name = 'cheaper archer upgrade'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (100, 237, 218, 437):
                set_tech_discount(effect, i, -1, 0.75)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'enable Hei Guang Cavalry'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1944)
            append_tech(data, tech, effect)
            name = 'Heavy Hei Guang Cavalry'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1033)
            append_tech(data, tech, effect)
        case 'Sicilians':
            name = '+100s'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 2, 100)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'enable Serjant'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1660)
            append_tech(data, tech, effect)
        case 'Slavs':
            # Siege Unit Cheaper ext
            effect = effects[567]
            original_classes = set(map(lambda command: command.b, effect.effect_commands))
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in siege_workshop_units:
                if i not in original_units and units[i].class_ not in original_classes:
                    multiply_unit_cost(effect, i, -1, 0.85)

        case 'Spanish':
            name = 'Tech Reward'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_tech(effect, 323)
            disable_tech(effect, 324)
            disable_tech(effect, 326)
            # wheelbarrow, double-bit axe, horse collar, gold/stone mining
            plus_resource(effect, 3, 100)
            append_tech(data, tech, effect)
            name = 'Tech Reward Age2'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            # handcart, bow-saw, heavy plow, gold/stone shaft mining, town watch, arson, inf atk/def, arc def, maa,
            # longswordsman, pikeman
            plus_resource(effect, 3, 240)
            append_tech(data, tech, effect)
            name = 'Tech Reward Age3'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            # two-man saw, crop rotation, thumb ring, pathian tactics, town patrol, gambeson, two-handed swordsman,
            # champion, legionary, light cavalry, arc def, inf atk/def, guard tower, murder hole, herble medicine,
            # chemistry, elite skirm, careening, caravan
            plus_resource(effect, 3, 360)
            append_tech(data, tech, effect)
            name = 'Tech Reward Age4'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            # winged hussar, arc def, inf atk/def, keep, bombard tower, conscription, dry dock, guilds
            plus_resource(effect, 3, 140)
            append_tech(data, tech, effect)
            name = 'gunpowder units fire faster ext'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            origin_units = list(
                map(lambda command: command.a,
                    filter(lambda command: command.type == 5 and command.c == 10, effects[446].effect_commands)))
            effect = get_new_effect(name)
            for i in gunpowder_units:
                if i in origin_units or data.civs[0].units[i].class_ == 44:
                    continue
                multiply_unit_attribute(effect, i, -1, 10, 0.85)
            append_tech(data, tech, effect)
        case 'Spartans':
            name = 'enable Hoplite'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1136)
            research_tech(effect, 1136)
            e_hoplite_tech_id = 1137
            disable_tech(effect, e_hoplite_tech_id)
            append_tech(data, tech, effect)
            name = 'Elite Hoplite'
            tech = copy.deepcopy(techs[e_hoplite_tech_id])
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            tech.civ = -1
            tech.research_locations[0].button_id = 8
            effect = get_new_effect(name)
            force_tech(effect, e_hoplite_tech_id)
            research_tech(effect, e_hoplite_tech_id)
            append_tech(data, tech, effect)

            name = 'enable Spartans TC Techs'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1225)
            force_tech(effect, 1223)
            force_tech(effect, 1224)
            append_tech(data, tech, effect)
            name = 'Hippagretai'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 1225)
            effect = get_new_effect(name)
            force_tech(effect, 1226)
            append_tech(data, tech, effect)
            techs[1179].civ = -1
            # elite Stratego ext
            upgrade_unit(effects[1128], 2227, 2228)
        case 'Tatars':
            name = 'reverse Tatars Sheep'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_tech(effect, 299)
            disable_tech(effect, 303)
            disable_tech(effect, 305)
            disable_tech(effect, 310)
            set_unit_attribute(effect, 890, -1, 0, -1)
            set_unit_attribute(effect, 1694, -1, 0, -1)
            append_tech(data, tech, effect)

            units = data.civs[0].units
            sheep_building1 = copy.deepcopy(units[1693])
            sheep_annex1 = copy.deepcopy(units[1694])
            sheep_annex2 = copy.deepcopy(units[1696])
            sheep_building1_id = len(units)
            sheep_annex1_id = sheep_building1_id + 1
            sheep_annex2_id = sheep_annex1_id + 1
            sheep_building1.dead_unit_id = 1695
            sheep_building1.copy_id = sheep_building1_id
            sheep_building1.base_id = sheep_building1_id
            sheep_building1.id = sheep_building1_id
            sheep_annex1.copy_id = sheep_annex1_id
            sheep_annex1.base_id = sheep_annex1_id
            sheep_annex1.id = sheep_annex1_id
            sheep_annex2.copy_id = sheep_annex2_id
            sheep_annex2.base_id = sheep_annex2_id
            sheep_annex2.id = sheep_annex2_id

            sheep_building1.building.head_unit = sheep_annex2_id
            sheep_annex1.dead_unit_id = sheep_annex2_id
            sheep_annex2.building.annexes = (
                BuildingAnnex(sheep_building1_id, 0.5, 0), BuildingAnnex(sheep_building1_id, 0, -0.5),
                BuildingAnnex(888, 0, 0), BuildingAnnex(-1, 0, 0))
            for civ in data.civs:
                civ.units.append(sheep_building1)
                civ.units.append(sheep_annex1)
                civ.units.append(sheep_annex2)
            name = 'Extra Sheep from TC'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            upgrade_unit(effect, 890, sheep_annex1_id)
            upgrade_unit(effect, 1694, sheep_annex1_id)
            set_unit_attribute(effect, sheep_annex1_id, -1, 0, -1)
            append_tech(data, tech, effect)
            name = 'Flaming Camel'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 703)
            move_unit_button(effect, 1263, 13)
            append_tech(data, tech, effect)
        case 'Teutons':
            # Inf Cav +1 armor ext
            origin_units = set(map(lambda command: command.a, effects[333].effect_commands))
            ext_units = list()
            for i, unit in enumerate(data.civs[1].units):
                if i in origin_units:
                    continue
                if unit is None or unit.creatable is None or len(unit.creatable.train_locations) == 0:
                    continue
                if unit.creatable.hero_mode == 1:
                    continue
                if bool(set(map(lambda x: x.unit_id, unit.creatable.train_locations)) & {constants.BARRACK_NUM,
                                                                                         constants.STABLE_NUM}) and i not in origin_units:
                    ext_units.append(i)
            for i in (333, 334):
                effect = effects[i]
                for j in ext_units:
                    plus_unit_armor(effect, j, -1, 1, 4)
            # tc +atk
            effect = effects[335]
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in TC_IDS:
                if i in origin_units:
                    continue
                plus_unit_attribute(effect, i, -1, 2, 10)
                plus_unit_attribute(effect, i, -1, 107, 5)
        case 'Turks':
            # Gunpowder +20% HP ext
            effect = effects[296]
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in gunpowder_units:
                if i in origin_units:
                    continue
                multiply_unit_hp(effect, i, -1, 1.25)
            name = 'Free Winged-Hussar'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            set_tech_cost(effect, 786, -1, 0)
            set_tech_time(effect, 786, 0)
            append_tech(data, tech, effect)
        case 'Tupi':
            name = 'enable Ibirapema'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1390)
            move_unit_button(effect, 1699, 31)
            append_tech(data, tech, effect)
            name = 'Elite Ibirapema'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1391)
            move_tech_button(effect, 1391, -1)
            append_tech(data, tech, effect)
            name = '+25 res'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            plus_resource(effect, 0, 25)
            plus_resource(effect, 1, 25)
            plus_resource(effect, 2, 25)
            plus_resource(effect, 3, 25)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
        case 'Vietnamese':
            # Archers +20% HP ext
            effect = effects[672]
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            for i, unit in enumerate(data.civs[0].units):
                if i in origin_units:
                    continue
                if unit is None or unit.creatable is None or len(unit.creatable.train_locations) == 0:
                    continue
                if constants.ARCHERY_RANGE_NUM in list(map(lambda x: x.unit_id,
                                                           unit.creatable.train_locations)) and i not in origin_units:
                    multiply_unit_hp(effect, i, -1, 1.2)
            name = 'Eco Techs no wood, 1/2 time'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            for i in (1012, 1013, 1014):
                set_tech_cost(effect, i, 1, 0)
                set_tech_time_discount(effect, i, 0.5)
            append_tech(data, tech, effect)
        case 'Wei':
            name = 'enable Xianbei Raider'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1037)
            move_unit_button(effect, 1952, 22)
            append_tech(data, tech, effect)
            name = 'enable Cao Cao'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1038)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'free vils age1'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1039)
            force_tech(effect, 1042)
            force_tech(effect, 1045)
            force_tech(effect, 1047)
            force_tech(effect, 1049)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'free vils age2'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1040)
            force_tech(effect, 1043)
            force_tech(effect, 1046)
            force_tech(effect, 1048)
            force_tech(effect, 1050)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            name = 'free vils age3'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1041)
            force_tech(effect, 1044)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            # Pasture tech + vil
            for i in range(1012, 1015):
                tech = get_new_tech(techs[i].name + ' + free vil')
                set_require_techs(tech, params.switch_tech_id, i)
                tech.effect_id = 1039
                append_tech(data, tech)
            name = 'remove origin Heavy Cavalry +HP'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_tech(effect, 1056)
            disable_tech(effect, 1057)
            disable_tech(effect, 1058)
            disable_tech(effect, 1059)
            append_tech(data, tech, effect)
            tech = copy.deepcopy(techs[1056])
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, BLOODLINE_ID)
            tech.civ = -1
            castle_hc_hp_bl_effect = effects[tech.effect_id]
            castle_hc_hp_bl_tech_id = append_tech(data, tech)
            tech = copy.deepcopy(techs[1057])
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, BLOODLINE_ID)
            tech.civ = -1
            imp_hc_hp_bl_effect = effects[tech.effect_id]
            imp_hc_hp_bl_tech_id = append_tech(data, tech)
            tech = copy.deepcopy(techs[1058])
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            tech.civ = -1
            castle_hc_hp_effect = effects[tech.effect_id]
            castle_hc_hp_tech_id = append_tech(data, tech)
            disable_tech(castle_hc_hp_effect, castle_hc_hp_bl_tech_id)
            disable_tech(castle_hc_hp_bl_effect, castle_hc_hp_tech_id)
            tech = copy.deepcopy(techs[1059])
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            tech.civ = -1
            imp_hc_hp_effect = effects[tech.effect_id]
            imp_hc_hp_tech_id = append_tech(data, tech)
            disable_tech(imp_hc_hp_effect, imp_hc_hp_bl_tech_id)
            disable_tech(imp_hc_hp_bl_effect, imp_hc_hp_tech_id)
        case 'Wu':
            name = 'enable Jian'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1075)
            move_unit_button(effect, 1974, 31)
            append_tech(data, tech, effect)
            name = 'enable Sun Jian'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1083)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)

    return reverse_tech_ids
