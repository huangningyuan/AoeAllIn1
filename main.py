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
    class_set = set()
    
    # 收集研发时间大于1的科技
    techs_with_time = []
    for tech in techs:
        tech_name = tech.name
        research_time = tech.research_locations[0].research_time
        if research_time > 1:
            techs_with_time.append((tech_name, research_time))
    
    # 按研发时间从短到长排序
    techs_with_time.sort(key=lambda x: x[1])
    
    # 输出科技名和时间
    print("\n研发时间大于1的科技（按时间从短到长排序）：")
    print("-" * 60)
    for i, (tech_name, research_time) in enumerate(techs_with_time, 1):
        print(f"排名: {i}, 科技名: {tech_name}, 研发时间: {research_time}")
    print("-" * 60)
    print(f"总计: {len(techs_with_time)} 个科技")