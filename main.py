# -*- coding: utf-8 -*-
import constants
from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand


if __name__ == '__main__':
    # update_mod()
    file_name = r'C:\Users\huang\Games\Age of Empires 2 DE\76561198141916001\mods\local\All Civ Bonus Test\resources\_common\dat\empires2_x2_p1.dat'
    # file_name = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\empires2_x2_p1.dat'
    data = DatFile.parse(file_name)
    effects = data.effects
    techs = data.techs
    tech_cost = list()
    units = data.civs[55].units
    for effect in effects:
        for command in effect.effect_commands:
            if command.a == 429:
                print(effect.name, command)

