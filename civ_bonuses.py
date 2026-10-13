import copy

from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost

import constants
from all_in_1_params import All_In_1_Params
from chronicle_issues import deal_with_chronicle_issues
from constants import \
    BARRACK_ID, CASTLE_ID, CHRONICLE_CIV_IDS, \
    ELITE_TEMPLE_GUARD_TECH_ID, MONESTARY_ID, TEMPLE_GUARD_IDS
from custom_civ_bonus import deal_custom_bonus
from deal_requirement import deal_tech_requrirement
from ftt import move_unit_button, move_tech_button
from regional_units import activate_all_regional_units
from utils import add_require_tech, make_require_age_earlier
from utils import disable_tech, get_new_unit, get_civ_name, set_require_techs, set_unit_attribute, set_resource, \
    append_tech, force_research_tech, multiply_resource, \
    check_effect, multiply_unit_attribute, disable_unit
from utils import enable_tech
from utils import enable_unit
from utils import force_tech
from utils import get_new_effect
from utils import get_new_tech
from utils import replace_require_tech

TECH_TO_REMOVE = [286, 287, 500,
                  641, 649, 664,
                  699, 700, 701, 702, 788, 789,
                  806, 807, 808, 957,
                  721, 288, 388,
                  323, 324, 326, 299, 303, 305,
                  310, 867, 868, 869, 1071,
                  241, 242, 1058, 885,
                  1059, 995, 1067, 1004, 355,
                  1397, 1353,
                  1136, 1137,
                  1169, 1170, 1171,
                  1195, 1196, 1197,
                  1012, 1013, 1014]


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
    AGE_TECH_IDS = (101, 102, 103, 104, 113, 1209)
    for i in range(constants.ORIGINAL_TECH_NUM):
        tech = techs[i]
        required_techs = tech.required_techs
        research_location = tech.research_locations[0]
        if tech.civ == -1:
            continue
        reqs = [
            rt for rt in tech.required_techs[:tech.required_tech_count]
            if rt != -1
        ]
        has_only_age_reqs = len(reqs) > 0 and all(
            rt in AGE_TECH_IDS for rt in reqs
        )
        if research_location.location_id == CASTLE_ID and (
                research_location.button_id in (6, 7, 8) or (
                research_location.button_id in (12, 13) and tech.civ in CHRONICLE_CIV_IDS)):
            civ_ut_ids[tech.civ].append(i)
            continue
        elif research_location.location_id > 0 and not has_only_age_reqs:
            civ_custom_bonus_ids[tech.civ].append(i)
            continue
        elif research_location.research_time > 0 and not has_only_age_reqs:
            continue
        elif tech.name.find('post-imp') > -1:
            continue
        elif tech.effect_id == -1 and required_techs[0] == 104 and tech.required_tech_count == 1:
            continue
        elif i in TECH_TO_REMOVE:
            continue
        if has_only_age_reqs:
            if 103 in reqs:
                civ_imp_bonus_ids[tech.civ].append(i)
            elif 102 in reqs or 113 in reqs:
                civ_castle_bonus_ids[tech.civ].append(i)
            elif 101 in reqs or 1209 in reqs:
                civ_feudal_bonus_ids[tech.civ].append(i)
            else:
                civ_bonus_ids[tech.civ].append(i)
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
                continue
            elif effect_command.type == 103:
                continue
            elif effect_command.type == 2 and effect_command.b == 0:
                enable_unit(reverse_effect, effect_command.a)
                continue
            elif effect_command.type == 18:
                continue
            else:
                tech_tree_bonus_effect_commands.append(effect_command)

        _seen = set()
        deduped = []
        for _cmd in tech_tree_bonus_effect_commands:
            _key = (_cmd.type, _cmd.a, _cmd.b, _cmd.c, round(_cmd.d, 3))
            if _key not in _seen:
                _seen.add(_key)
                deduped.append(_cmd)
        tech_tree_bonus_effect_commands = deduped

        tech = get_new_tech(reverse_name)
        set_require_techs(tech, params.switch_tech_id)
        tech.civ = i
        tech_id, effect_id = append_tech(data, tech, reverse_effect)
        all_in_1_reverse_tech_ids[civ_name] = tech_id

        def _force_by_researchable(effect_, bid):
            rl = techs[bid].research_locations[0]
            if rl.location_id > 0:
                force_tech(effect_, bid)
            else:
                force_research_tech(effect_, bid)

        def _make_bonus_group(prefix, req_ids, bonus_ids, extra_effect_commands=None):
            if len(bonus_ids) == 0 and not extra_effect_commands:
                return None
            name = civ_name + prefix
            effect = get_new_effect(name)
            if extra_effect_commands:
                effect.effect_commands = extra_effect_commands
            for bid in bonus_ids:
                _force_by_researchable(effect, bid)
            tech = get_new_tech(name)
            set_require_techs(tech, *req_ids)
            tech.civ = -1
            new_tid, _ = append_tech(data, tech, effect)
            disable_tech(reverse_effect, new_tid)
            return new_tid

        tid = _make_bonus_group(" Bonus", (params.switch_tech_id,),
                                civ_bonus_ids[i], tech_tree_bonus_effect_commands)
        if tid is not None:
            all_in_1_civ_bonus_tech_ids[civ_name] = tid

        tid = _make_bonus_group(" Feudal Bonus", (params.feudal_duplicate_tech_id, params.switch_tech_id),
                                civ_feudal_bonus_ids[i])
        if tid is not None:
            all_in_1_civ_feudal_bonus_tech_ids[civ_name] = tid

        tid = _make_bonus_group(" Castle Bonus", (params.castle_duplicate_tech_id, params.switch_tech_id),
                                civ_castle_bonus_ids[i])
        if tid is not None:
            all_in_1_civ_castle_bonus_tech_ids[civ_name] = tid

        tid = _make_bonus_group(" Imp Bonus", (params.imp_duplicate_tech_id, params.switch_tech_id),
                                civ_imp_bonus_ids[i])
        if tid is not None:
            all_in_1_civ_imp_bonus_tech_ids[civ_name] = tid

        bonus_ids = civ_custom_bonus_ids[i]
        if len(bonus_ids) > 0:
            for tech_id in bonus_ids:
                tech = copy.deepcopy(techs[tech_id])
                tech.name = tech.name.replace('C-Bonus, ', '')
                tech.name = tech.name.replace('C-Bonus ', '')
                tech.civ = -1
                if 101 in tech.required_techs:
                    replace_require_tech(tech, 101, params.feudal_duplicate_tech_id)
                elif 1209 in tech.required_techs:
                    replace_require_tech(tech, 1209, params.feudal_duplicate_tech_id)
                elif 102 in tech.required_techs:
                    replace_require_tech(tech, 102, params.castle_duplicate_tech_id)
                elif 113 in tech.required_techs:
                    replace_require_tech(tech, 113, params.castle_duplicate_tech_id)
                elif 103 in tech.required_techs:
                    replace_require_tech(tech, 103, params.imp_duplicate_tech_id)
                add_require_tech(tech, params.switch_tech_id, update_count=True)
                if tech.effect_id == -1:
                    first_command = None
                else:
                    effect = effects[tech.effect_id]
                    if len(effect.effect_commands) > 0:
                        first_command = effect.effect_commands[0]
                    else:
                        first_command = None
                if first_command and first_command.type == 1 and first_command.a in (91, 92, 93, 94):
                    new_effect = copy.deepcopy(effect)
                    for command in new_effect.effect_commands:
                        if command.type == 1:
                            match command.a:
                                case 91:
                                    command.a = 0
                                case 92:
                                    command.a = 1
                                case 93:
                                    command.a = 2
                                case 94:
                                    command.a = 3
                    new_tech_id, effect_id = append_tech(data, tech, new_effect)
                    disable_tech(reverse_effect, new_tech_id)
                else:
                    effect = get_new_effect(tech.name)
                    if len(tech.research_locations) > 0 and tech.research_locations[0].location_id > 0:
                        name = 'force ' + tech.name
                        tech.name = name
                        effect.name = name
                        if tech.research_locations[0].location_id == BARRACK_ID:
                            new_age_tech_id = make_require_age_earlier(tech, params)
                            add_require_tech(techs[tech_id], new_age_tech_id)
                        tech.research_locations = []
                        tech.resource_costs = (ResearchResourceCost(-1, 0, 0), ResearchResourceCost(-1, 0, 0), ResearchResourceCost(-1, 0, 0))
                        # early barrack techs
                        force_tech(effect, tech_id)
                    else:
                        name = 'force research ' + tech.name
                        tech.name = name
                        effect.name = name
                        force_research_tech(effect, tech_id)
                    new_tech_id, effect_id = append_tech(data, tech, effect)
                    disable_tech(reverse_effect, new_tech_id)

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

    activate_all_regional_units(data, params)
    deal_tech_requrirement(data, params)

    # Catapult Galleon requirements
    name = 'Catapult Requirements'
    tech = get_new_tech(name)
    set_require_techs(tech, 1350, 433, 675)
    tech.required_tech_count = 1
    tech_id = append_tech(data, tech)
    set_require_techs(techs[913], 115, tech_id)

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

    name = 'Puru + Koreans + Romans Stone Mining food generation'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    multiply_resource(effect, 512, 1.2 * 1.05)
    append_tech(data, tech, effect)

    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
    effect = get_new_effect(name)
    move_tech_button(effect, ELITE_TEMPLE_GUARD_TECH_ID, 32, 0)
    elite_temple_guard_tech = techs[ELITE_TEMPLE_GUARD_TECH_ID]
    elite_temple_guard_tech.research_locations.append(elite_temple_guard_tech.research_locations[0])
    elite_temple_guard_tech.research_locations[1].location_id = MONESTARY_ID
    elite_temple_guard_tech.research_locations[1].button_id = 32
    for i in TEMPLE_GUARD_IDS:
        move_unit_button(effect, i, 31, 0)
        move_unit_button(effect, i, 24, 1)
    append_tech(data, tech, effect)

    additional_tc_ids = [2275, 2276, 2277]
    effect = check_effect(effects, 421)
    for i in additional_tc_ids:
        multiply_unit_attribute(effect, i, -1, 13,  1.1)

    name = 'Persians + Achemenids TC Age3'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
    effect = get_new_effect(name)
    for i in additional_tc_ids:
        multiply_unit_attribute(effect, i, -1, 13, 1.15 / 1.1)
    append_tech(data, tech, effect)

    name = 'Persians + Achemenids TC Age4'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    for i in additional_tc_ids:
        multiply_unit_attribute(effect, i, -1, 13, 1.2 / 1.15)
    append_tech(data, tech, effect)

    deal_with_chronicle_issues(data, params)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())

    # port button
    for i in (13, 545, 17):
        for civ_id, civ in enumerate(civs):
            creatable = civ.units[i].creatable
            creatable.train_locations.append(copy.deepcopy(creatable.train_locations[0]))
            creatable.train_locations[1].unit_id = 2172
            if civ_id in CHRONICLE_CIV_IDS:
                creatable.train_locations[0].unit_id = 45

    name = 'Disable units'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    for i in (562, 584):
        disable_unit(effect, i)
    append_tech(data, tech, effect)

    name = 'Enable Feudal Units'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
    effect = get_new_effect(name)
    # stable
    force_research_tech(effect, 25)
    append_tech(data, tech, effect)

    sample_units = data.civs[0].units
    split_line_unit = get_new_unit(sample_units)
    for civ in data.civs:
        for i in range(10):
            civ.units.append(get_new_unit(sample_units))
        civ.units.append(split_line_unit)
    print('Civ Bonuses added.')