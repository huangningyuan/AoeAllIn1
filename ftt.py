from genieutils.datfile import DatFile
from genieutils.effect import Effect
from genieutils.effect import EffectCommand

from all_in_1_params import All_In_1_Params
from constants import ELITE_PHALANGITE_TECH_ID
from utils import enable_tech, append_tech
from utils import get_new_effect
from utils import get_new_tech


def move_unit_button(effect: Effect, unit_id: int, button_id: int, index: int = 0):
    if index > 0:
        effect.effect_commands.append(EffectCommand(0, unit_id, -1, 158, index))
    effect.effect_commands.append(EffectCommand(0, unit_id, -1, 43, button_id))
    if index > 0:
        effect.effect_commands.append(EffectCommand(0, unit_id, -1, 158, 0))


def move_unit_train_location(effect: Effect, unit_id: int, location_id: int, index: int = 0):
    if index > 0:
        effect.effect_commands.append(EffectCommand(0, unit_id, -1, 158, index))
    effect.effect_commands.append(EffectCommand(0, unit_id, -1, 42, location_id))
    if index > 0:
        effect.effect_commands.append(EffectCommand(0, unit_id, -1, 158, 0))


def move_tech_button(effect: Effect, tech_id: int, button_id: int, location_index: int = -1):
    effect.effect_commands.append(EffectCommand(8, tech_id, 5, location_index, button_id))


def move_tech_building(effect: Effect, tech_id: int, building_id: int, location_index: int = -1):
    effect.effect_commands.append(EffectCommand(8, tech_id, 4, location_index, building_id))


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
    # varangian guard
    move_unit_button(effect, 2703, 13)
    move_unit_button(effect, 2704, 13)
    move_tech_button(effect, 1454, 14)
    # Champi
    move_unit_button(effect, 2550, 33)
    move_unit_button(effect, 2588, 33)
    move_unit_button(effect, 2552, 33)
    move_unit_button(effect, 2554, 33)
    move_tech_button(effect, 1402, 34)
    move_tech_button(effect, 1351, 34)
    move_tech_button(effect, 1352, 34)
    # fire lancer
    move_unit_button(effect, 1901, 22)
    move_unit_button(effect, 1903, 22)
    move_tech_button(effect, 982, 27)
    # rocket cart
    move_unit_button(effect, 1904, 22)
    move_unit_button(effect, 1907, 22)
    move_tech_button(effect, 980, 27)
    # War Chariot
    move_unit_button(effect, 2150, 31)
    move_unit_button(effect, 2151, 31)
    move_tech_button(effect, 1171, 32)
    # slinger
    move_unit_button(effect, 185, 21)
    # shrivamsha
    move_unit_button(effect, 1751, 22)
    move_unit_button(effect, 1753, 22)
    move_tech_button(effect, 843, 27)
    # Thirisadai
    move_unit_button(effect, 1750, 24)
    # Longship
    move_unit_button(effect, 250, 21)
    move_tech_button(effect, 372, 26)
    # Turtle ship
    move_unit_button(effect, 831, 22)
    move_unit_button(effect, 832, 22)
    move_tech_button(effect, 448, 27)
    # Caravel
    move_unit_button(effect, 1004, 23)
    move_unit_button(effect, 1006, 23)
    move_tech_button(effect, 597, 28)
    # Phalangite
    move_unit_button(effect, 2384, 31)
    move_tech_button(effect, ELITE_PHALANGITE_TECH_ID, 32)
    # Sannahya
    move_unit_button(effect, 2390, 23)
    move_unit_button(effect, 2391, 23)
    move_tech_button(effect, 1328, 28)

    append_tech(data, tech, effect)

    for i in range(5):
        append_tech(data, get_new_tech(), get_new_effect())
