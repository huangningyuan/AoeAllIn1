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

## 命名来源约定

项目中出现的名称来自多个源头，允许差异。以下是完整的来源层级和典型差异，**用于 AI 理解时快速定位"这个名称从哪来"**，避免混淆。

### 来源层级（按使用位置）

| # | 名称类型 | 格式 | 来源 | 用途 | 典型示例 |
|---|---------|------|------|------|---------|
| 1 | **dat 返回名** | 英文首字母大写，文明名带复数 s | `DatFile.parse()` → `get_civ_name()` | unit_switch.json 的 `civ_names` 字段、代码逻辑匹配 | Britons, Koreans, Achaemenids, Vikings |
| 2 | **科技树 JSON 文件名** | 全大写，无复数 s | `CivTechTrees\*.json` | civ_tech_trees.md 的文件名匹配 | BRITONS, KOREANS, ACHAEMENIDS |
| 3 | **civ_switch 中文映射** | 中文简称（项目约定） | `civ_switch.py` `civ_en_zh_dict` | mod strings 文件生成 | Britons→不列颠 |
| 4 | **strings 官方中文** | 游戏内完整译名 | `key-value-strings-utf8.txt` SID 10271-10332 | 描述/文档时用、游戏内显示 | Varangians→瓦兰吉人 |
| 5 | **AGE3NamesV0007.ini** | 编辑器英文术语 | `Tools_Builds\AGE3NamesV0007.ini` | 发 AGE 截图时对上文本 | Base Pierce, Eagle Warriors |
| 6 | **代码变量/常量** | Snake Case 全大写 | Python 代码内部 | 常量定义 | `DOCK_ID`, `KHITANS_CA_DISCOUNT` |

### 关键注意点

- **dat 返回名 vs 科技树 JSON 文件名**：没有复数 s，全大写。例：dat 返回 `Koreans`，文件名 `KOREANS.json`
- **civ_switch 中文 vs 官方中文允许差异**：以下几处已确认不同，**保留项目约定**：
  - 编年史文明后缀：`Macedonians`→马其顿 vs 马其顿人、`Thracians`→色雷斯 vs 色雷斯人、`Puru`→普鲁 vs 普鲁人、`Saxons`→撒克逊 vs 撒克逊人、`Varangians`→瓦兰吉 vs 瓦兰吉人、`Danes`→丹麦 vs 丹麦人
- **编年史文明分两部**（`CHRONICLE_CIV_IDS = [46,47,48,54,55,56]`），科技树差异大：
  - **编年史 1**：`Achaemenids`(46)、`Athenians`(47)、`Spartans`(48) — 希腊化/波斯
  - **编年史 2**：`Macedonians`(54)、`Thracians`(55)、`Puru`(56) — 后续章节
  - ⚠️ 49-53 (`Shu/Wu/Wei/Jurchens/Khitans`) 和 57-61 (`Muisca/Mapuche/Tupi/Saxons/Varangians`) **不属于编年史 DLC**，是独立 DLC

### Unit / Tech 名称字段区分（避免混淆）

dat 中 Unit 和 Tech 都有 `name` 和 `language_dll_name` 两个字段，**含义完全不同**：

| dat 字段 | 类型 | 含义 | 示例 |
|---------|------|------|------|
| `unit.name` | str | **内部代号**（不是显示名） | `MOSUN`, `HOUS`, `ARCHR_D` |
| `unit.language_dll_name` | int | **游戏内显示名的 strings SID** | Mangudai = 6108 |
| `tech.name` | str | 原生 tech = SID 字符串；项目副本 = 可读英文名 | 原生 `7067` / 副本 `Forging` |
| `tech.language_dll_name` | int | **游戏内显示名的 strings SID** | Forging = 7067 |
| `tech.language_dll_description` | int | 科技描述的 strings SID | Forging = 8067 |

**查官方文本的方法**：AGE 截图看到的 `Language File Name *` 数字 → 直接在 `key-value-strings-utf8.txt` 搜这个 SID。编码规律详见 `dat_reference.md` 的 Unit 部分。

**`unique_techs_config.json` 的 `tech_name`** → 用**官方英文名**（即 strings 里的英文文本，不是 SID 也不是内部代号）。

### 已整理到专门文档的名称

| 主题 | 位置 | 覆盖范围 |
|------|------|---------|
| Attack Type / Armor Type | `dat_reference.md` | type 0-61，AGE3Names vs strings 双栏对比（攻防护甲共用同一套编码，没有独立的 AttackNames section） |
| Unit / Tech 字段映射 | `dat_reference.md` | `name` vs `language_dll_name` 区别、strings SID 编码规则 |
| 科技树 Node 名称 | `civ_tech_trees.md` | `Name` 字段 = 游戏内显示名，配合 Node Type / Node Status 判断可用性 |

---

## 注意事项
- 一个科技不能出现在同一建筑的多个button位置（同一文明同一位置不能有两个科技）
- 修改后运行`python update_all_in_1.py`验证
- JSON配置文件改完后可通过`python -c "import json;json.load(open('xxx.json','r',encoding='utf-8'));print('OK')"`快速验证格式