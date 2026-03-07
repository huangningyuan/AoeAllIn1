from genieutils import unit

import constants
import utils
import os


def deal_xs(units: list[unit.Unit]):
    xs_path = constants.GAME_XS_PATH
    mod_xs_path = os.path.join(utils.get_mod_path(), 'resources', '_common', 'xs')
    if not os.path.exists(mod_xs_path):
        os.makedirs(mod_xs_path, exist_ok=True)
    
    # 读取Constants.xs文件，提取Object Classes信息
    constants_xs_path = os.path.join(xs_path, 'Constants.xs')
    if not os.path.exists(constants_xs_path):
        raise FileNotFoundError(f"Constants.xs file not found at {constants_xs_path}")
    
    with open(constants_xs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到Object Classes部分
    import re
    # 首先定位// Object Classes标题行
    object_classes_start = content.find('// Object Classes')
    if object_classes_start == -1:
        raise ValueError("Object Classes section not found in Constants.xs")
    
    # 从标题行开始提取内容，直到下一个//==============或文件结束
    section_content = content[object_classes_start:]
    section_end = section_content.find('//==============', section_content.find('//==============') + 1)
    if section_end != -1:
        section_content = section_content[:section_end]
    
    # 从section_content中提取所有extern const int定义，直接匹配完整的变量名
    class_matches = re.findall(r'extern const int (c\w+) = (\d+);', section_content)
    
    if not class_matches:
        raise ValueError("No class definitions found in Object Classes section")
    
    # 过滤掉cSentinelEndClass
    class_matches = [(name, value) for name, value in class_matches if name != 'cSentinelEnd']
    
    if not class_matches:
        raise ValueError("No class definitions found after filtering")

    # 创建类名列表，直接使用完整的变量名
    class_list = []
    for class_name, value in class_matches:
        class_list.append(class_name)

    creatable_class_set = set()
    for unit in units:
        if not unit:
            continue
        creatable = unit.creatable
        if creatable and len(creatable.train_locations) > 0 \
                and creatable.train_locations[0].button_id > 0 \
                and creatable.train_locations[0].unit_id > 0:
            creatable_class_set.add(unit.class_)
    print(class_list)
    exclude_class_set = {'cBuildingClass', 'cGateClass', 'cFarmClass', 'cTowerClass', 'cWallClass'}
    valid_class_set = set()
    for class_id in creatable_class_set:
        if class_id < len(class_list) and class_list[class_id] not in exclude_class_set:
            valid_class_set.add(class_list[class_id])

    # 处理Effects.xs文件
    effects_xs_path = os.path.join(xs_path, 'Effects.xs')
    mod_effects_xs_path = os.path.join(mod_xs_path, 'Effects.xs')
    
    if os.path.exists(effects_xs_path):
        # 读取Effects.xs文件
        with open(effects_xs_path, 'r', encoding='utf-8') as f:
            effects_content = f.read()
        
        # 按照要求修改文件内容
        import re
        # 找到OrdoCavalry函数
        ordo_cavalry_pattern = r'(void OrdoCavalry\(int ClassTarget = -1, int playerId = -1\)\s*\{[\s\S]*?\n)\s*xsTask\(ClassTarget, cTaskTypeStinger, -1, playerId\);[\s\S]*?(xsTaskAmount\(cTaskAttrWorkValue1, -1\.5\);[\s\S]*?\})'
        
        def replace_ordo_cavalry(match):
            # 获取函数开头部分
            function_start = match.group(1)
            # 生成遍历valid_class_set的xsTask调用，保持与原代码一致的缩进
            xs_task_calls = ''
            # 确保valid_class_set是有序的，使用sorted()排序
            for class_name in sorted(valid_class_set):
                xs_task_calls += f'  xsTask(ClassTarget, cTaskTypeStinger, {class_name}, playerId);\n'
            # 组合新的函数内容
            return function_start + xs_task_calls + '}'
        
        # 替换函数内容
        modified_effects_content = re.sub(ordo_cavalry_pattern, replace_ordo_cavalry, effects_content)
        
        # 写入到mod目录
        with open(mod_effects_xs_path, 'w', encoding='utf-8') as f:
            f.write(modified_effects_content)
        
        print(f"Effects.xs modified and copied to mod directory: {mod_effects_xs_path}")
    else:
        print(f"Effects.xs not found at {effects_xs_path}")
    
    print("Valid classes:", valid_class_set)
    return valid_class_set