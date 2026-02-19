from all_in_1_params import All_In_1_Params
from genieutils.datfile import DatFile
from utils import append_tech
from utils import get_new_tech
from utils import replace_tuple
from utils import set_require_techs

FEUDAL_REQUIRE_TECH_LIST = [14, 55, 87, 202, 213, 216, 278, 433, 659, 660, 661, 666, 667, 668, 755, 906]
CASTLE_AGE_REQUIRE_TECH_LIST = [13, 48, 65, 162, 182, 197, 203, 207, 249, 279, 384, 1137]
IMPERIAL_AGE_REQUIRE_TECH_LIST = [12, 47, 96, 209, 217, 221, 264, 429, 436, 85, 377, 218]
EAGLE_WARRIOR_TECH_NUM = 384
ELITE_EAGLE_TECH_NUM = 434
FLEMISH_REVOLUTION_TECH_NUM = 755


def deal_tech_requrirement(data: DatFile, params: All_In_1_Params):
    print('Dealing Required tech...')
    for i, tech in enumerate(data.techs):
        if i in FEUDAL_REQUIRE_TECH_LIST:
            tech.required_techs = replace_tuple(tech.required_techs, -1, params.switch_tech_id)
        elif i in CASTLE_AGE_REQUIRE_TECH_LIST:
            tech.required_techs = replace_tuple(tech.required_techs, -1, params.feudal_duplicate_tech_id)
        elif i in IMPERIAL_AGE_REQUIRE_TECH_LIST:
            tech.required_techs = replace_tuple(tech.required_techs, -1, params.castle_duplicate_tech_id)

    elite_eagle_requirement_tech = get_new_tech('Elite Eagle Requirement')
    set_require_techs(elite_eagle_requirement_tech, params.castle_duplicate_tech_id, EAGLE_WARRIOR_TECH_NUM)
    elite_eagle_requirement_tech_num = append_tech(data, elite_eagle_requirement_tech)
    elite_eagle_require_techs = data.techs[ELITE_EAGLE_TECH_NUM].required_techs
    data.techs[ELITE_EAGLE_TECH_NUM].required_techs = replace_tuple(elite_eagle_require_techs, -1, elite_eagle_requirement_tech_num)

    flemish_revolution_tech = data.techs[FLEMISH_REVOLUTION_TECH_NUM]
    flemish_revolution_tech.required_techs = (115, params.switch_tech_id, 758, -1, -1, -1)
    flemish_revolution_tech.required_tech_count = 2
    flemish_revolution_tech.civ = -1

    print('Required tech finished.')
