import copy

from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost
from genieutils.unit import BuildingAnnex

import constants
from all_in_1_params import All_In_1_Params
from constants import \
    BARRACK_ID, BLOODLINE_ID, CASTLE_ID, FRANKS_FORAGER_WORK_RATE, HOUSE_ID, \
    MAPUCHE_FORAGER_WORK_RATE, ROMAN_CIV_WORK_RATE, WP_WITH_RELIC_ID, PAPHOS_SHADOW_TECH_ID
from deal_requirement import FLEMISH_REVOLUTION_TECH_ID
from ftt import move_tech_button
from ftt import move_unit_button
from utils import add_require_tech
from utils import check_effect
from utils import disable_tech, extend_effect, force_research_tech, disable_unit
from utils import enable_unit
from utils import force_tech
from utils import get_new_effect
from utils import get_new_tech
from utils import replace_require_tech
from utils import set_require_techs, get_tech_id_by_name, plus_resource, multiply_unit_cost, multiply_unit_attack, \
    multiply_unit_hp, multiply_unit_attribute, multiply_resource, \
    set_unit_attribute, plus_unit_armor, set_resource, upgrade_unit, research_tech, plus_unit_attribute, \
    append_tech


def deal_custom_bonus(data: DatFile, params: All_In_1_Params, civ_name):
    reverse_tech_ids = list()
    techs = data.techs
    effects = data.effects
    units = data.civs[0].units
    match civ_name:
        case 'Achaemenids':
            achaemenids_tech_id = 1103
            name = 'Achaemenids or All in 1'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, achaemenids_tech_id)
            tech.required_tech_count = 1
            tech_id = append_tech(data, tech)
            # enable Achaemenids TC techs
            for i in range(1195, 1198):
                replace_require_tech(techs[i], PAPHOS_SHADOW_TECH_ID, -1)
                replace_require_tech(techs[i], achaemenids_tech_id, tech_id)
                techs[i].required_tech_count -= 1
        case 'Armenians':
            name = 'Mule Cart'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            tech.effect_id = 944
            append_tech(data, tech)
            for i in range(942, 948):
                add_require_tech(techs[i], params.switch_tech_id)
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
            research_tech(effect, 1202)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
            # Athenians lumberjack
            effect = check_effect(effects, 1119)
            for command in effect.effect_commands:
                if command.type == 1 and command.a == 502 and command.b == 0:
                    command.b = 1
                    break
        case 'Aztecs':
            effect = check_effect(effects, 447)
            original_class = set()
            for command in effect.effect_commands:
                if command.type == 5 and command.a == -1 and command.c == 101:
                    original_class.add(command.b)
            for i in {23, 44, 47} - original_class:
                multiply_unit_attribute(effect, -1, i, 101, 1 / 1.15)
        case 'Bengalis':
            effect = check_effect(effects, 865)
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            extend_units = []
            for unit in constants.elephant_units:
                if unit not in original_units:
                    extend_units.append(unit)
            extend_effect(effect, extend_units)
        case 'Berbers':
            name = 'genitour'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 601)
            append_tech(data, tech, effect)
            name = 'Elite Genitour'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 599)
            append_tech(data, tech, effect)
        case 'Bohemians':
            name = 'enable houfnice'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 787)
            append_tech(data, tech, effect)
        case 'Bulgarians':
            name = 'enable konnik'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 1254)
            append_tech(data, tech, effect)
        case 'Burgundians':
            effect = check_effect(effects, 794)
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in constants.gunpowder_units:
                if i in origin_units:
                    continue
                for attack in data.civs[0].units[i].type_50.attacks:
                    multiply_unit_attack(effect, i, -1, 125, attack.class_)
            name = 'Feudal Gillnets'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id, 906)
            effect = get_new_effect(name)
            force_tech(effect, 65)
            append_tech(data, tech, effect)
            name = 'Feudal eco tech requirement'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 758)
            append_tech(data, tech, effect)
            name = 'Burgundians Khitan Domestication'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1014)
            append_tech(data, tech, effect)
            name = 'Burgundians Khitan Pastoralism'
            tech = get_new_tech(name)
            set_require_techs(tech, params.feudal_duplicate_tech_id, 1014)
            effect = get_new_effect(name)
            force_research_tech(effect, 1013)
            append_tech(data, tech, effect)
            name = 'Burgundians Khitan Transhumance'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, 1013)
            effect = get_new_effect(name)
            force_research_tech(effect, 1012)
            append_tech(data, tech, effect)
            name = 'enable Flemish Revolution'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, FLEMISH_REVOLUTION_TECH_ID)
            append_tech(data, tech, effect)
        case 'Burmese':
            name = 'Burmese TB'
            tech = get_new_tech(name)
            tech.effect_id = 651
            append_tech(data, tech)
        case 'Byzantines':
            name = 'Byzantines Imperial Camel Discount'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            multiply_unit_cost(effect, 207, -1, 0.75)
            append_tech(data, tech, effect)
        case 'Chinese':
            name = 'enable Dragon Ship'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, 246)
            tech.effect_id = 1010
            append_tech(data, tech)
        case 'Georgians':
            # Cavalry regeneration ext
            for i in (954, 961):
                extend_effect(check_effect(effects, i), [1263])
        case 'Gurjaras':
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
            effect = check_effect(effects, 843)
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            extend_units = []
            for unit in constants.elephant_units:
                if unit not in original_units:
                    extend_units.append(unit)
            extend_effect(effect, extend_units)
        case 'Hindustanis':
            # gunpowder +armor ext
            effect = check_effect(effects, 576)
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            extend_units = list()
            for i in constants.gunpowder_units:
                if i not in origin_units:
                    extend_units.append(i)
            extend_effect(effect, extend_units)
            name = 'enable Imperial Camel Rider'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 236)
            effect = get_new_effect(name)
            force_tech(effect, 521)
            append_tech(data, tech, effect)
        case 'Huns':
            techs[241].civ = -1
            techs[242].civ = -1
            effect = check_effect(effects, 231)
            disable_tech(effect, get_tech_id_by_name(data, 'Start w/ Horse'))
            name = 'disable house'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            disable_unit(effect, HOUSE_ID)
            append_tech(data, tech, effect)
        case 'Incas':
            name = 'Incas Team Tech Tree'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            tech.effect_id = 678
            tech_id = append_tech(data, tech)
            reverse_tech_ids.append(tech_id)
            name = 'enable settlement'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            enable_unit(effect, 2556)
            enable_unit(effect, 68)
            disable_tech(effect, 1353)
            move_unit_button(effect, 2556, 1)
            append_tech(data, tech, effect)
            for i in (1354, 1355, 1356):
                add_require_tech(techs[i], params.switch_tech_id)
        case 'Italians':
            # cheap gunpowder units ext
            effect = check_effect(effects, 555)
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in constants.gunpowder_units:
                if i in original_units:
                    continue
                multiply_unit_cost(effect, i, -1, 0.8)
            name = 'Condottiero'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 522)
            append_tech(data, tech, effect)
        case 'Khitans':
            name = 'enable farm'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            tech.civ = 53
            effect = get_new_effect(name)
            enable_unit(effect, 50)
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
            add_require_tech(techs[786], params.imp_duplicate_tech_id)
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
            effect = check_effect(effects, 1220)
            original_classes = set(map(lambda command: command.b, effect.effect_commands))
            for i in constants.siege_units:
                if units[i].class_ not in original_classes:
                    plus_unit_armor(effect, i, -1, 1, 3)
                    multiply_unit_attack(effect, i, -1, 130, 11)
            # Druzhina + Phalangite
            effect = check_effect(effects, 569)
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in (2384, 2385):
                if i not in original_units:
                    plus_unit_attribute(effect, i, -1, 22, -0.5)

        case 'Malians':
            # barrack unit +1 p armor ext
            origin_units = set(map(lambda command: command.a, effects[618].effect_commands))
            target_units = []
            for i, unit in enumerate(units):
                if unit and unit.creatable and BARRACK_ID in list(
                        map(lambda x: x.unit_id, unit.creatable.train_locations)) and i not in origin_units:
                    target_units.append(i)
            for i in (618, 619, 620):
                effect = check_effect(effects, i)
                for j in target_units:
                    plus_unit_armor(effect, j, -1, 1, 3)
        case 'Mapuche':
            effect = check_effect(effects, 1383)
            b_wp_with_relic = False
            for command in effect.effect_commands:
                if command.a == WP_WITH_RELIC_ID:
                    b_wp_with_relic = True
                    break
            if not b_wp_with_relic:
                extend_effect(effect, [WP_WITH_RELIC_ID])
        case 'Mayans':
            # Cheap Archers ext
            origin_units = (763, 765)
            ext_units = list()
            for i, unit in enumerate(data.civs[1].units):
                if unit and unit.class_ == 0 and unit.creatable and CASTLE_ID in list(
                        map(lambda x: x.unit_id, unit.creatable.train_locations)) and i not in origin_units:
                    ext_units.append(i)
            effect = check_effect(effects, 449)
            for i in ext_units:
                multiply_unit_cost(effect, i, -1, 0.9)
            effect = check_effect(effects, 485)
            for i in ext_units:
                multiply_unit_cost(effect, i, -1, 0.8 / 0.9)
            effect = check_effect(effects, 486)
            for i in ext_units:
                multiply_unit_cost(effect, i, -1, 0.7 / 0.8)
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
            check_effect(effects, effect_with_bl_id)
            tech.effect_id = effect_with_bl_id
            tech_with_bl_id = append_tech(data, tech)
            disable_tech(effects[effect_with_bl_id], tech_with_bl_id)
            name = 'Light Cavalry +20% HP'
            tech = get_new_tech(name)
            set_require_techs(tech, params.castle_duplicate_tech_id, params.switch_tech_id)
            effect_id = 288
            check_effect(effects, effect_id)
            tech.effect_id = effect_id
            tech_id = append_tech(data, tech)
            disable_tech(effects[effect_id], tech_id)
            disable_tech(effects[effect_id], tech_with_bl_id)
            disable_tech(effects[effect_with_bl_id], tech_id)
            name = 'Light Cavalry +30% HP + BL'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id, BLOODLINE_ID)
            effect_with_bl_id = 287
            check_effect(effects, effect_with_bl_id)
            tech.effect_id = effect_with_bl_id
            tech_with_bl_id = append_tech(data, tech)
            disable_tech(effects[effect_with_bl_id], tech_with_bl_id)
            name = 'Light Cavalry +30% HP'
            tech = get_new_tech(name)
            set_require_techs(tech, params.imp_duplicate_tech_id, params.switch_tech_id)
            effect_id = 387
            check_effect(effects, effect_id)
            tech.effect_id = effect_id
            tech_id = append_tech(data, tech)
            disable_tech(effects[effect_id], tech_id)
            disable_tech(effects[effect_id], tech_with_bl_id)
            disable_tech(effects[effect_with_bl_id], tech_id)

        case 'Muisca':
            # archer armor ext
            _e = check_effect(effects, 1369)
            for i in (2301, 2302):
                plus_unit_attribute(_e, i, -1, 4, 1)
        case 'Persians':
            name = 'enable Savar'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, 209)
            effect = get_new_effect(name)
            force_tech(effect, 526)
            append_tech(data, tech, effect)
            disable_tech(check_effect(effects, 253), 526)
            disable_tech(check_effect(effects, 581), 265)
        case 'Poles':
            name = 'Reverse Poles Stone Mining Gold'
            tech = get_new_tech(name)
            set_require_techs(tech, 806, params.switch_tech_id)
            tech.civ = 38
            effect = get_new_effect(name)
            multiply_resource(effect, 241, 1 / 1.15)
            append_tech(data, tech, effect)
        case 'Portuguese':
            name = 'Foraging Wood'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            forager_wood_prod_rate = effects[510].effect_commands[0].d
            set_resource(effect, 267, forager_wood_prod_rate * ROMAN_CIV_WORK_RATE * FRANKS_FORAGER_WORK_RATE * MAPUCHE_FORAGER_WORK_RATE)
            append_tech(data, tech, effect)
            # cheap conquisidator
            effect = check_effect(effects, 33)
            multiply_unit_cost(effect, -1, 23, 0.8)
        case 'Puru':
            # Remove Puru Emplacement
            _e = check_effect(effects, 1266)
            _e.effect_commands.pop(-1)
            _e = check_effect(effects, 1267)
            _e.effect_commands.pop(-1)
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
            # siege move speed ext
            original_classes = set(map(lambda command: command.b, effects[1072].effect_commands))
            original_units = set(map(lambda command: command.a, effects[1072].effect_commands))
            for i in (420, 691, 1795, 2140): # siege warships
                if i not in original_units and units[i].class_ not in original_classes:
                    multiply_unit_attribute(check_effect(effects, 1068), i, -1, 5, 1.1)
                    multiply_unit_attribute(check_effect(effects, 1072), i, -1, 5, 1.1)
            for i in constants.siege_units:
                if i not in original_units and units[i].class_ not in original_classes:
                    multiply_unit_attribute(check_effect(effects, 1068), i, -1, 5, 1.1)
                    multiply_unit_attribute(check_effect(effects, 1072), i, -1, 5, 1.1)
            name = 'Enable Traction Trebuchets'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            effect = get_new_effect(name)
            research_tech(effect, 1025)
            move_unit_button(effect, 1942, 24)
            append_tech(data, tech, effect)
        case 'Slavs':
            # Siege Unit Cheaper ext
            effect = check_effect(effects, 567)
            original_classes = set(map(lambda command: command.b, effect.effect_commands))
            original_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in constants.siege_workshop_units:
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
            # wheelbarrow, double-bit axe, horse collar, gold/stone mining, Transhumance
            plus_resource(effect, 3, 120)
            append_tech(data, tech, effect)
            name = 'Tech Reward Age2'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
            effect = get_new_effect(name)
            # handcart, bow-saw, heavy plow, gold/stone shaft mining, town watch, arson, inf atk/def, arc def, maa,
            # longswordsman, pikeman, Pastoralism
            plus_resource(effect, 3, 260)
            append_tech(data, tech, effect)
            name = 'Tech Reward Age3'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            effect = get_new_effect(name)
            # two-man saw, crop rotation, thumb ring, pathian tactics, town patrol, gambeson, two-handed swordsman,
            # champion, legionary, light cavalry, arc def, inf atk/def, guard tower, murder hole, herble medicine,
            # chemistry, elite skirm, careening, caravan, Domestication
            plus_resource(effect, 3, 380)
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
            for i in constants.gunpowder_units:
                if i in origin_units or data.civs[0].units[i].class_ == 44:
                    continue
                multiply_unit_attribute(effect, i, -1, 10, 0.85)
            append_tech(data, tech, effect)
        case 'Spartans':
            if params.bug_compat:
                techs[1226].civ = -1
            # elite Stratego ext
            upgrade_unit(check_effect(effects, 1128), 2227, 2228)
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
            sheep_annex1.building.tech_id = 1498
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
            upgrade_unit(effect, 2717, sheep_annex1_id)
            set_unit_attribute(effect, sheep_annex1_id, -1, 0, -1)
            append_tech(data, tech, effect)
        case 'Saxons':
            effect = check_effect(effects, 1469)
            castle_building = copy.deepcopy(units[2717])
            castle_building_id = len(units)
            castle_building.copy_id = castle_building_id
            castle_building.base_id = castle_building_id
            castle_building.id = castle_building_id
            for civ in data.civs:
                civ.units.append(castle_building)
            for command in effect.effect_commands:
                if command.type == 3 and command.a == 2718 and command.b == 2717:
                    command.b = castle_building_id
            for civ in data.civs:
                new_castle = civ.units[2418]
                new_castle.building.annexes = (BuildingAnnex(2718, 2, 2), BuildingAnnex(-1, 0, 0),
                                               BuildingAnnex(-1, 0, 0), BuildingAnnex(-1, 0, 0))

            name = 'discount for initial tc'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_research_tech(effect, 1498)
            tech_id, effect_id = append_tech(data, tech, effect)
            reverse_tech_ids.append(tech_id)
        case 'Turks':
            # Gunpowder +20% HP ext
            effect = check_effect(effects, 296)
            origin_units = set(map(lambda command: command.a, effect.effect_commands))
            for i in constants.gunpowder_units:
                if i in origin_units:
                    continue
                multiply_unit_hp(effect, i, -1, 1.25)
        case 'Vietnamese':
            # Archers + 20%HP ext
            effect = check_effect(effects, 672)
            extend_effect(effect, [2101, 2102])
        case 'Wei':
            name = 'free vils age1'
            tech = get_new_tech(name)
            set_require_techs(tech, params.switch_tech_id)
            effect = get_new_effect(name)
            force_tech(effect, 1039)
            force_tech(effect, 1042)
            force_tech(effect, 1042) # Khitans
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
            force_tech(effect, 1043) # Khitans
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
            force_tech(effect, 1044) # Khitans
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
            castle_hc_hp_bl_effect = check_effect(effects, tech.effect_id)
            castle_hc_hp_bl_tech_id = append_tech(data, tech)
            tech = copy.deepcopy(techs[1057])
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, BLOODLINE_ID)
            tech.civ = -1
            imp_hc_hp_bl_effect = check_effect(effects, tech.effect_id)
            imp_hc_hp_bl_tech_id = append_tech(data, tech)
            tech = copy.deepcopy(techs[1058])
            set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
            tech.civ = -1
            castle_hc_hp_effect = check_effect(effects, tech.effect_id)
            castle_hc_hp_tech_id = append_tech(data, tech)
            disable_tech(castle_hc_hp_effect, castle_hc_hp_bl_tech_id)
            disable_tech(castle_hc_hp_bl_effect, castle_hc_hp_tech_id)
            tech = copy.deepcopy(techs[1059])
            set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
            tech.civ = -1
            imp_hc_hp_effect = check_effect(effects, tech.effect_id)
            imp_hc_hp_tech_id = append_tech(data, tech)
            disable_tech(imp_hc_hp_effect, imp_hc_hp_bl_tech_id)
            disable_tech(imp_hc_hp_bl_effect, imp_hc_hp_tech_id)
        case 'Wu':
            # regeneration of wp with relic
            for i in range(1085, 1087):
                effect = check_effect(effects, i)
                b_wp_with_relic = False
                for command in effect.effect_commands:
                    if command.a == WP_WITH_RELIC_ID:
                        b_wp_with_relic = True
                        break
                if not b_wp_with_relic:
                    extend_effect(effect, WP_WITH_RELIC_ID)
    return reverse_tech_ids