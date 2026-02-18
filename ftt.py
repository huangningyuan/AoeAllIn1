import constants
from all_in_1_params import All_In_1_Params
from genieutils.datfile import DatFile
from genieutils.effect import Effect
from genieutils.effect import EffectCommand

from constants import PORT_IDS
from utils import append_tech, enable_tech, append_tech
from utils import get_new_effect
from utils import get_new_tech


def move_unit_button(effect: Effect, unit_id: int, button_id: int):
    effect.effect_commands.append(EffectCommand(0, unit_id, -1, 43, button_id))

def move_tech_button(effect: Effect, tech_id: int, button_id: int, location_index: int = -1):
    effect.effect_commands.append(EffectCommand(8, tech_id, 5, location_index, button_id))


def move_tech_building(effect: Effect, tech_id: int, building_id: int):
    effect.effect_commands.append(EffectCommand(8, tech_id, 4, -1, building_id))


def deal_ftt(data: DatFile, params: All_In_1_Params):
    effects = data.effects
    for i, tech in enumerate(data.techs):
        if tech.name.startswith('[FTT]'):
            tech.required_tech_count = 7
            tech.effect_id = -1

    name = 'All in 1 FTT'
    tech = get_new_tech()
    tech.name = name
    tech.required_techs = (params.switch_tech_id, -1, -1, -1, -1, -1)
    tech.required_tech_count = 1
    tech.civ = -1
    effect = get_new_effect()
    effect.name = name

    # armored elephant
    move_unit_button(effect, 1744, 21)
    move_unit_button(effect, 1746, 21)
    move_tech_button(effect, 838, 26)

    # winged hussar
    move_tech_button(effect, 786, 6)

    # elephant archer
    move_unit_button(effect, 873, 23)
    move_unit_button(effect, 875, 23)
    move_tech_button(effect, 481, 28)
    # genitour
    move_unit_button(effect, 1010, 24)
    move_unit_button(effect, 1012, 24)
    move_tech_button(effect, 599, 29)
    # lancers
    move_unit_button(effect, 1370, 24)
    move_unit_button(effect, 1372, 24)
    move_tech_button(effect, 715, 29)
    # hoplite
    move_unit_button(effect, 2110, 3)
    move_unit_button(effect, 2111, 3)
    move_unit_button(effect, 2187, 3)
    move_unit_button(effect, 2188, 3)
    move_tech_button(effect, 1137, 8)
    # war chariot
    move_unit_button(effect, 2150, 31)
    move_unit_button(effect, 2151, 31)
    move_tech_button(effect, 1171, 32)
    # Condottiero
    move_unit_button(effect, 882, 23)
    # Achaemenids TC techs
    move_tech_button(effect, 1195, 7)
    move_tech_button(effect, 1196, 8)
    move_tech_button(effect, 1197, 9)
    # Spartans TC techs
    move_tech_button(effect, 1223, 13)
    move_tech_button(effect, 1224, 14)
    # polemarch
    move_unit_button(effect, 2162, 6)
    move_unit_button(effect, 2164, 6)
    move_unit_button(effect, 2165, 6)
    move_unit_button(effect, 2166, 6)
    move_unit_button(effect, 2167, 6)
    move_unit_button(effect, 2270, 6)
    move_unit_button(effect, 2271, 6)
    move_unit_button(effect, 2272, 6)
    # loom
    move_tech_button(effect, 22, 10)
    # spies
    enable_tech(effect, 408)
    move_tech_button(effect, 408, 14)
    # 3k heroes
    move_unit_button(effect, 1966, 26)
    move_unit_button(effect, 1954, 28)
    move_unit_button(effect, 1978, 27)

    append_tech(data, tech, effect)
    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())


