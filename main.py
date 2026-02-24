# -*- coding: utf-8 -*-
import constants
import os
import utils
from genieutils.datfile import DatFile
from genieutils.effect import EffectCommand


if __name__ == '__main__':
    # update_mod()
    mod_path = utils.get_mod_path()
    file_name = os.path.join(mod_path, 'resources', '_common', 'dat', 'empires2_x2_p1.dat')
    print(file_name)
    # file_name = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\empires2_x2_p1.dat'
    data = DatFile.parse(file_name)
    effects = data.effects
    techs = data.techs
    tech_cost = list()
    units = data.civs[55].units
    for effect in effects:
        for command in effect.effect_commands:
            if command.a == 1137:
                print(effect.name, command)

