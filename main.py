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
    units = data.civs[0].units
    
    # 统计拥有最多 armours 的单位，排除 class_ 为 3,4,31 的情况
    unit_armor_count = {}
    excluded_classes = {3, 4, 31}
    
    for i, unit in enumerate(units):
        if (unit and unit.type_50 and unit.type_50.armours and 
            hasattr(unit, 'creatable') and unit.creatable and 
            hasattr(unit.creatable, 'train_locations') and unit.creatable.train_locations and 
            len(unit.creatable.train_locations) > 0 and 
            unit.creatable.train_locations[0].unit_id > 0):
            # 检查是否有 armor 的 class_ 为 36，如果有则排除该单位
            if any(armor.class_ == 36 for armor in unit.type_50.armours):
                continue
            valid_armors = [armor for armor in unit.type_50.armours if armor.class_ not in excluded_classes]
            if valid_armors:
                unit_armor_count[i] = len(valid_armors)
    
    # 找出拥有最多 armours 的单位
    if unit_armor_count:
        max_armor_count = max(unit_armor_count.values())
        max_armor_units = [(unit_id, units[unit_id]) for unit_id, count in unit_armor_count.items() if count == max_armor_count]
        
        print(f"拥有最多 armours 的单位（数量={max_armor_count}）:")
        for unit_id, unit in max_armor_units:
            unit_name = getattr(unit, 'name', f'Unit {unit_id}')
            print(f"- ID={unit_id}, 名称={unit_name}")
    else:
        print("没有找到符合条件的单位")