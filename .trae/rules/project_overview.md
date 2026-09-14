# AoeAllIn1 项目规则

## 项目简介
帝国时代2决定版（AoE2DE）全文明合一mod。核心思路：让每个文明通过按钮切换拥有原本专属的独特单位/科技。

---

## 项目文件结构

### 核心配置文件（JSON）
| 文件 | 职责 |
|------|------|
| `unit_switch.json` | **文明切换配置**。定义多个category（如cavalry、cavalry archer），每个category包含unit_button_id、tech_button_id，以及switch_contents列表（文明匹配→单位ID/科技ID） |
| `unique_techs_config.json` | **独特科技配置**。按建筑分区（CASTLE_ID/STABLE_ID/BARRACK_ID/ARCHERY_RANGE_ID等），每个科技条目有source_id/button/icon/register_as |
| `linkedTechs.json` | 科技互斥分组数据（项目运行时生成在GAME_DATA_PATH目录） |

### Python模块
| 文件 | 职责 |
|------|------|
| `main.py` | 调试入口（非主流程） |
| `update_all_in_1.py` | **正式入口脚本**。加载原生dat→调用adding_switch()初始化→依次执行ftt/civ_bonuses/unique_techs/civ_switch→保存→mutex互斥处理→打包zip |
| `add_switch.py` | **添加总开关**。adding_switch()函数负责预留tech/effect/unit空间、初始化All_In_1_Params，返回params供后续模块使用 |
| `unit_switch.json` → `civ_switch.py` | 读取unit_switch.json，自动计算all_uids/all_tids并集，匹配文明后通过move_unit_button/move_tech_button调整按钮位置（-1=隐藏，正数=目标位置） |
| `unique_techs_config.json` → `unique_techs_config_loader.py` | 解析config，将register_as映射到params.other_params供civ_switch使用；同时返回source_id→effect_id/tech_id的映射表 |
| `ftt.py` | **FTT补丁**。通过move_tech_button调整原生单位/科技的默认按钮位置 |
| `custom_civ_bonus.py` | **文明加成**。新建单位/科技（get_new_tech/get_new_unit），通过append_tech追加到效果 |
| `civ_bonuses.py` | 文明专属加成逻辑 |
| `unique_techs.py` | 独特科技效果实现（如extend_effect） |
| `mutex.py` | 科技互斥（Linked Techs）处理 |
| `deal_requirement.py` | 科技前置需求调整 |
| `constants.py` | 常量定义（建筑ID、图标ID、游戏数据路径等） |
| `utils.py` | 通用工具（get_new_tech、append_tech、move_unit_button、disable_tech等） |
| `all_in_1_params.py` | All_In_1_Params参数对象，在各模块间传递配置数据 |

### 游戏数据路径
- `C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\`
- `constants.GAME_DATA_PATH` 指向mod数据目录

---

## 关键约定

### 1. register_as 别名机制
- 在`unique_techs_config.json`的科技条目中添加`register_as`字段
- `unique_techs_config_loader.py`解析后自动存入`params.other_params[register_as] = tech_id`
- `unit_switch.json`中tech_ids可直接用字符串别名（如`"el_dorado_id"`），无需硬编码数字ID
- **这是唯一的跨配置引用方式**，禁止用sid2all[原生科技ID][index]这类硬编码模式

### 2. 自动计算并集
- `unit_switch.json`中**不再配置**`all_unit_ids`/`all_tech_ids`
- `civ_switch.py`自动从所有switch_contents的unit_ids/tech_ids计算并集，得到全部候选
- 匹配文明后，将不在enable列表中的按钮移到-1（隐藏），在enable列表中的移到目标位置

### 3. 同源多建筑配置
- 一个科技可在多个建筑section中配置不同button位置
- 例如Fabric Shields在CASTLE_ID/BARRACK_ID用INFANTRY图标，ARCHERY_RANGE_ID用ARCHER图标，STABLE_ID用CAVALRY图标
- icon按所在建筑上下文选择对应类型

### 4. 按钮位置规则
- 单位按钮位置通过`unit_button_id`（category级）统一设定
- 科技按钮位置通过`tech_button_id`（category级）统一设定
- button=-1表示隐藏（civ_switch自动处理）
- **没有switch_content独立按钮位的概念**，同一个category内所有switch_content共享unit_button_id和tech_button_id

### 5. 科技分类
- **独特科技**：只有某个文明/少数文明可研发，需要在unique_techs_config.json注册并在unit_switch中配置
- **共享科技**：多个文明共用同一升级线（如Malon已归类在掷矛投石手共用科技）
- **精锐升级**（Elite Xxx）：不是独特科技，不需要配置

### 6. 新建科技 vs 原生科技
- 1378这类是原生科技，但项目中可能新建了对应的科技实例
- 新增独特科技应仿照攻城船中楼船关联的独特科技实现方式

### 7. 马厩button=7的约定
- 马厩7号位用于骑射手/骆驼弓骑兵/独特科技的切换
- 只对骑士系生效的科技也需注册register_as并在Default/Persians的tech_ids中引用，这样无骑士系的文明切换时会自动隐藏

---

## 新增配置的工作流程

### 添加新的骑兵/骑射手分支
1. 在`unit_switch.json`对应category下添加switch_content条目
2. 配置civ_match（civ_names列表或default:true）
3. 填入unit_ids（精锐也一起配）和tech_ids（数字ID或register_as别名）

### 添加新的独特科技
1. 确认科技的source_id（原生科技ID）
2. 在`unique_techs_config.json`对应建筑section添加条目：source_id/button/icon/tech_name
3. 添加`register_as`别名
4. 在`unit_switch.json`对应switch_content的tech_ids中引用该别名
5. 如果科技对多个兵种线生效，可能需要在多个category中都配置

---

## 注意事项
- 一个科技不能出现在同一建筑的多个button位置（同一文明同一位置不能有两个科技）
- 修改后运行`python update_all_in_1.py`验证
- JSON配置文件改完后可通过`python -c "import json;json.load(open('xxx.json','r',encoding='utf-8'));print('OK')"`快速验证格式