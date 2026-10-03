from genieutils.datfile import DatFile
from genieutils.tech import ResearchLocation
from constants import \
    ARCHERY_RANGE_ID, BARRACK_ID, BLACKSMITH_ID, CASTLE_ID, DOCK_ID, FOLWALK_ID, \
    HUTS_IDS, IUT_ICON_ID, KREPOST_ID, LARGE_CIV_ID, LUMBER_CAMP_ID, MARKET_ID, \
    MILL_ID, MINING_CAMP_ID, MONESTARY_ID, MULE_CART_ID, OUTPOST_ID, PAVILIONS_IDS, \
    SETTLEMENT_ID, SIEGE_ID, STABLE_ID, TC_ID, UNIV_ID, WONDER_ID, \
    YURT_IDS, TENTS_IDS

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
    params.civ_index_to_additional_uts = dict()
    params.other_params = dict()
    tech = get_new_tech('All in 1 Switch')
    tech.civ = LARGE_CIV_ID
    switch_tech_id = append_tech(data, tech)
    params.switch_tech_id = switch_tech_id

    tech = get_new_tech('Early Feudal')
    set_require_techs(tech, switch_tech_id, 101)
    tech.required_tech_count = 1
    params.early_feudal_tech_id = append_tech(data, tech)

    tech = get_new_tech('feudal switch')
    set_require_techs(tech, switch_tech_id, 101)
    params.feudal_duplicate_tech_id = append_tech(data, tech)

    tech = get_new_tech('Early Castle')
    set_require_techs(tech, params.feudal_duplicate_tech_id, 102)
    tech.required_tech_count = 1
    params.early_castle_tech_id = append_tech(data, tech)

    tech = get_new_tech('castle switch')
    set_require_techs(tech, switch_tech_id, 102)
    params.castle_duplicate_tech_id = append_tech(data, tech)

    tech = get_new_tech('Early Imp')
    set_require_techs(tech, params.castle_duplicate_tech_id, 103, 115)
    tech.required_tech_count = 1
    params.early_imp_duplicate_tech_id = append_tech(data, tech)

    tech = get_new_tech('imp switch')
    set_require_techs(tech, switch_tech_id, 103)
    params.imp_duplicate_tech_id = append_tech(data, tech)

    ACTIVATE_SWITCH_NAME = 'Activate switch'
    activate_switch_tech = get_new_tech(ACTIVATE_SWITCH_NAME, True)
    activate_switch_tech.icon_id = IUT_ICON_ID
    activate_switch_tech.language_dll_description = 6800
    activate_effect = get_new_effect(ACTIVATE_SWITCH_NAME)
    plus_resource(activate_effect, 3, -20)
    activate_switch_tech.research_locations.append(ResearchLocation(TC_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(BARRACK_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(STABLE_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(ARCHERY_RANGE_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(SIEGE_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(CASTLE_ID, 1, 10, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(WONDER_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(OUTPOST_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(BLACKSMITH_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(MARKET_ID, 1, 4, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(UNIV_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(MONESTARY_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(MILL_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(LUMBER_CAMP_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(MULE_CART_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(DOCK_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(MINING_CAMP_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(KREPOST_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(FOLWALK_ID, 1, 14, -1))
    activate_switch_tech.research_locations.append(ResearchLocation(SETTLEMENT_ID, 1, 14, -1))

    for i in PAVILIONS_IDS:
        activate_switch_tech.research_locations.append(ResearchLocation(i, 1, 14, -1))

    for i in YURT_IDS:
        activate_switch_tech.research_locations.append(ResearchLocation(i, 1, 14, -1))

    for i in HUTS_IDS:
        activate_switch_tech.research_locations.append(ResearchLocation(i, 1, 14, -1))

    for i in TENTS_IDS:
        activate_switch_tech.research_locations.append(ResearchLocation(i, 1, 14, -1))

    force_research_tech(activate_effect, switch_tech_id)
    append_tech(data, activate_switch_tech, activate_effect)

    print('Switch added.')
    return params