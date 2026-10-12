import copy

from genieutils.datfile import DatFile

from all_in_1_params import All_In_1_Params
from constants import DOCK_ID, PORT_ID, SHIPYARD_ID, CHRONICLE_CIV_IDS
from ftt import move_tech_button
from utils import (
    append_tech,
    disable_tech,
    enable_tech,
    enable_unit,
    force_research_tech,
    force_tech,
    get_new_effect,
    get_new_tech,
    replace_require_tech,
    research_tech,
    set_require_techs,
    set_unit_attribute,
)


def deal_with_chronicle_issues(data: DatFile, params: All_In_1_Params):
    append_tech_tech_id = 1138
    chronicle_tech_id_list = list()
    for i in CHRONICLE_CIV_IDS:
        tech = get_new_tech(data.civs[i].name)
        tech.civ = i
        chronicle_tech_id_list.append(append_tech(data, tech))

    name = 'Chronicle civs requirement'
    tech = get_new_tech(name)
    set_require_techs(tech, *chronicle_tech_id_list)
    tech.required_tech_count = 1
    chronicle_civs_requirement = append_tech(data, tech)
    params.other_params['chronicle_civs_requirement'] = chronicle_civs_requirement
    name = 'enable dock, port'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id)
    effect = get_new_effect(name)
    enable_unit(effect, DOCK_ID)
    set_unit_attribute(effect, PORT_ID, -1, 58, -1)
    enable_unit(effect, PORT_ID)
    force_tech(effect, 1143)
    research_tech(effect, 1143)
    append_tech(data, tech, effect)
    name = 'enable dock techs'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, append_tech_tech_id)
    effect = get_new_effect(name)
    for command in data.effects[1145].effect_commands:
        if command.type == 102:
            enable_tech(effect, int(command.d))
    append_tech_dock_tech_id, effect_id = append_tech(data, tech, effect)
    name = 'enable Feudal units'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.feudal_duplicate_tech_id)
    effect = get_new_effect(name)
    enable_unit(effect, SHIPYARD_ID)
    force_research_tech(effect, 1147)
    force_research_tech(effect, 1150)
    force_research_tech(effect, 1153)
    force_tech(effect, 384)
    append_tech(data, tech, effect)
    name = 'enable Castle units'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id)
    effect = get_new_effect(name)
    force_research_tech(effect, 1158)
    force_research_tech(effect, 426)
    append_tech(data, tech, effect)

    name = 'append_tech Gambesons'
    gambeson_tech_id = 875
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, chronicle_civs_requirement)
    effect = get_new_effect(name)
    force_research_tech(effect, gambeson_tech_id)
    append_tech(data, tech, effect)
    name = 'free append_tech paragons'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.castle_duplicate_tech_id, chronicle_civs_requirement)
    effect = get_new_effect(name)
    research_tech(effect, 1173)
    research_tech(effect, 1174)
    append_tech(data, tech, effect)
    name = 'append_tech siege onagers'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, 257, chronicle_civs_requirement)
    effect = get_new_effect(name)
    force_tech(effect, 320)
    append_tech(data, tech, effect)

    name = 'enable Imp units'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id)
    effect = get_new_effect(name)
    # Leviathan
    research_tech(effect, 1160)
    # bombard tower
    research_tech(effect, 64)
    # bombard cannon
    research_tech(effect, 188)
    # elite battle elephant
    force_tech(effect, 631)
    # elite elephant archer
    force_tech(effect, 481)
    # elite sannahya
    force_tech(effect, 1328)
    # loom
    move_tech_button(effect, 22, 11)
    append_tech(data, tech, effect)

    name = 'enable Imp units for Chronical'
    tech = get_new_tech(name)
    set_require_techs(tech, params.switch_tech_id, params.imp_duplicate_tech_id, chronicle_civs_requirement)
    effect = get_new_effect(name)
    # elite steppe lancer
    force_tech(effect, 689)
    # elite fire lancer
    force_tech(effect, 982)
    append_tech(data, tech, effect)
    append_tech_ship_upgrade_tech_ids = [1144, 1145, 1146, 1148, 1149, 1151, 1152, 1154, 1155, 1159]

    for i in append_tech_ship_upgrade_tech_ids:
        tech = copy.deepcopy(data.techs[i])
        tech.civ = -1
        replace_require_tech(tech, append_tech_tech_id, params.switch_tech_id)
        if 101 in tech.required_techs:
            replace_require_tech(tech, 101, params.feudal_duplicate_tech_id)
        elif 102 in tech.required_techs:
            replace_require_tech(tech, 102, params.castle_duplicate_tech_id)
        elif 103 in tech.required_techs:
            replace_require_tech(tech, 103, params.imp_duplicate_tech_id)
        effect = get_new_effect(tech.name)
        force_research_tech(effect, i)
        tech_id, effect_id = append_tech(data, tech, effect)
        disable_tech(data.effects[data.techs[append_tech_dock_tech_id].effect_id], tech_id)