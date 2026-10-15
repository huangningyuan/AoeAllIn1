from all_in_1_params import All_In_1_Params
from genieutils.datfile import DatFile
from utils import append_tech
from utils import get_new_tech
from utils import replace_require_tech
from utils import set_require_techs

FEUDAL_REQUIRE_TECH_LIST = []
CASTLE_AGE_REQUIRE_TECH_LIST = []
IMPERIAL_AGE_REQUIRE_TECH_LIST = []


def deal_tech_requrirement(data: DatFile, params: All_In_1_Params):
    print('Dealing Required tech...')
    for i, tech in enumerate(data.techs):
        if i in FEUDAL_REQUIRE_TECH_LIST:
            replace_require_tech(tech, 101, params.early_feudal_tech_id)
        elif i in CASTLE_AGE_REQUIRE_TECH_LIST:
            replace_require_tech(tech, 102, params.early_castle_tech_id)
        elif i in IMPERIAL_AGE_REQUIRE_TECH_LIST:
            replace_require_tech(tech, 103, params.early_imp_duplicate_tech_id)
            replace_require_tech(tech, 115, params.early_imp_duplicate_tech_id)

    print('Required tech finished.')