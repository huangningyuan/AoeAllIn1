from genieutils.datfile import DatFile
from genieutils.tech import ResearchLocation

import constants
from all_in_1_params import All_In_1_Params
from utils import append_tech, plus_resource, force_research_tech
from utils import get_new_effect, set_require_techs
from utils import get_new_tech
from utils import get_new_unit


# All in 1 switch
def adding_switch(data: DatFile):
    print('Adding switch...')
    techs = data.techs
    # add split area
    SPLIT_NAME = '----All in 1 Start----'
    for i in range(50):
        techs.append(get_new_tech())

    split_line_tech = get_new_tech()
    split_line_tech.name = SPLIT_NAME
    techs.append(split_line_tech)
    effects = data.effects
    for i in range(50):
        effects.append(get_new_effect())
    split_line_effect = get_new_effect()
    split_line_effect.name = SPLIT_NAME

    sample_units = data.civs[0].units
    split_line_unit = get_new_unit(sample_units)
    split_line_unit.name = SPLIT_NAME
    effects.append(split_line_effect)
    for civ in data.civs:
        for i in range(50):
            civ.units.append(get_new_unit(sample_units))
        civ.units.append(split_line_unit)

    params = All_In_1_Params()
    params.ut_in_castle_with_mutex_list = dict()
    params.other_params = dict()
    tech = get_new_tech('All in 1 Switch')
    tech.civ = constants.LARGE_CIV_ID
    switch_tech_id = append_tech(data, tech)
    params.switch_tech_id = switch_tech_id

    tech = get_new_tech('feudal switch')
    set_require_techs(tech, switch_tech_id, 101)
    params.feudal_duplicate_tech_id = append_tech(data, tech)

    tech = get_new_tech('castle switch')
    set_require_techs(tech, switch_tech_id, 102)
    params.castle_duplicate_tech_id = append_tech(data, tech)

    tech = get_new_tech('imp switch')
    set_require_techs(tech, switch_tech_id, 103)
    params.imp_duplicate_tech_id = append_tech(data, tech)

    ACTIVATE_SWITCH_NAME = 'Activate switch'
    activate_switch_tech = get_new_tech(ACTIVATE_SWITCH_NAME, True)
    activate_switch_tech.icon_id = constants.IUT_ICON_ID
    activate_switch_tech.language_dll_description = 6800
    activate_effect = get_new_effect(ACTIVATE_SWITCH_NAME)
    plus_resource(activate_effect, 3, -20)
    activate_switch_tech.research_locations.append(ResearchLocation(constants.TC_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.BARRACK_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.STABLE_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.ARCHERY_RANGE_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.SIEGE_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.CASTLE_NUM, 1, 10, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.WONDER_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.OUTPOST_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.BLACKSMITH_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.MARKET_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.UNIV_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.MONESTARY_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.MILL_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.LUMBER_CAMP_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.MULE_CART_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.DOCK_NUM, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.MINING_CAMP_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.KREPOST_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.FOLWALK_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(constants.SETTLEMENT_ID, 1, 14, -1))

    for i in constants.PAVILIONS_IDS:
        activate_switch_tech.research_locations.append(ResearchLocation(i, 1, 14, -1))

    force_research_tech(activate_effect, switch_tech_id)
    append_tech(data, activate_switch_tech, activate_effect)

    print('Switch added.')
    return params
