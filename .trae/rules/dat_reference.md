# AoE2DE Dat 数据结构速查

## DatFile 入口

**核心原理**：dat 的单位表是全文明共享的，每个文明通过 `civs[civ_id].units` 覆盖表 + effect（enable/disable unit、force/disable tech）+ 科技前置关系来构建自己的单位/科技可用性。科技树 JSON（CivTechTrees 目录下）是官方单独给的参考文件，可能和 dat 不匹配。

```python
data.techs          # List[Tech] - 所有科技（tech.civ 控制文明归属）
data.effects        # List[Effect]
data.civs[0].units  # List[Unit] - 通用单位表（默认值）
data.civs[civ_id].units  # 指定文明的单位覆盖（该文明对此单位的修改）
```

### Unit.creatable.train_locations

`unit.creatable.train_locations` 是一个列表，列出**这个单位可以在哪些建筑里被生产**：
- `train_locations[i].unit_id` = 生产它的建筑 ID（如 DOCK_ID=45, BARRACK_ID=12, CASTLE_ID=82）
- `train_locations[i].button_id` = 在该建筑里的按钮位置
- `train_locations[i].train_time` = 生产时间

典型用法（项目中大量出现）：
```python
# 找出所有在马厩生产的骑兵单位
for i, unit in enumerate(data.civs[0].units):
    if unit and unit.creatable and STABLE_ID in list(
            map(lambda x: x.unit_id, unit.creatable.train_locations)):
        ...
```

> **注意**：建筑本身也有 creatable.train_locations，表示**这个建筑在哪里被建造**（Dock、Port、Shipyard 等都指向 VMBLD 118 占位，因为它们是隐藏建筑，需要 tech 控制）。

---

## Tech (科技)
| 属性 | 类型 | 说明 |
|------|------|------|
| `civ` | int | 所属文明，**-1 = 所有文明可用** |
| `effect_id` | int | 关联的 Effect 索引 |
| `icon_id` | int | 图标 ID |
| `name` | str | 原生 tech 是 SID 字符串（如 `7067`），项目创建的副本设为可读英文名（如 `Forging`） |
| `language_dll_name` | int | **官方英文名的 strings SID**（AGE 截图中的 "Language File Name *"） |
| `language_dll_description` | int | **官方描述文本的 strings SID**（AGE 截图中的 "Language File Description"） |
| `language_dll_help` | int | 帮助文本 SID（`language_dll_name + 100000`） |
| `required_techs` | Tuple[int, 6] | 前置科技索引列表，**-1 = 空槽** |
| `required_tech_count` | int | 最少需要多少个前置非-1 |
| `research_locations` | List[ResearchLocation] | 研发地点列表。**原生 tech 通常只有一个**；`get_ut` 创建的副本也只有一个（同一科技在不同建筑中通过创建多个 tech 实例来保证按钮顺序）。**多个 location 的典型案例**是全文明开关科技（同按钮在多个建筑均可研发） |

---

## Unit (单位)
| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | int | dat 内部 ID（等于 unit_switch.json 的 unit_ids） |
| `name` | str | **内部名**（如 `MOSUN`, `HOUS`, `ARCHR_D`），不是游戏内显示名 |
| `language_dll_name` | int | **官方显示名的 strings SID**（AGE 截图中的 "Language File Name *"） |
| `language_dll_creation` | int | "建造/训练"提示文本 SID（`language_dll_name + 1000`） |
| `language_dll_help` | int | 帮助文本 SID（`language_dll_name + 100000`） |
| `icon_id` | int | 按钮图标索引 |
| `class_` | int | 单位类别（见 class_id 速查表） |
| `hit_points` | int | HP |
| `speed` | float | 速度 |
| `train_sound` | int | 训练音效 |
| `copy_id` | int | 复制来源 ID |
| `base_id` | int | 基础单位 ID（用于升级链） |

### 如何用 SID 找游戏内显示名
AGE 截图中看到的 `Language File Name *` 数字 = strings 文件 SID。直接在 `key-value-strings-utf8.txt` 里搜这个数字就能找到官方文本。

编码规律（原生 dat）：
| 类型 | SID 公式 | 示例 |
|------|---------|------|
| 单位显示名 | `language_dll_name` 直接取 | Unit 70 Mangudai → 6108 |
| 科技显示名 | `language_dll_name` 直接取 | Tech 67 Forging → 7067 |
| 科技描述 | `language_dll_description` 直接取 | Forging → 8067 |
| 单位创建提示 | `language_dll_name + 1000` | Mangudai → 7108 |
| 帮助文本 | `language_dll_name + 100000` | Mangudai → 106108 |

> **重要**：`unit.name` 和 `tech.name` 不是游戏内显示名！显示名必须走 `language_dll_name` → strings SID 这条路。项目创建的副本会把 `tech.name` 设成可读英文（如 `Forging`），方便代码引用，但 strings 里查不到，游戏内显示还是走 `language_dll_name`。

### strings 编码体系总览

**AGE 编辑器和游戏内地图编辑器共享同一套 strings 编码**。dat 文件里的 attr、class、resource、armor type 等数字编码，在 strings 文件（`key-value-strings-utf8.txt`）中都有对应的中文文本——分别落在 Attribute List、Class List、Resource List、Armor/Attack classes 几个段里。

strings 文件路径（Steam 安装目录）：
```
C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\{zh|en}\strings\key-value\key-value-strings-utf8.txt
```

| 编码类型 | strings 段名 | SID 范围 | 与 dat 编码关系 | 公式 |
|---------|-------------|---------|----------------|------|
| **Attack/Armor Type** | Attack and Armor classes | 12400-12599 | `command.d` 里的 type | **SID = type + 12400** ✅ 严格线性 |
| **Class** | Class List | 13300-13366 | `unit.class_`、type 0/4/5 的 `b`（class_id） | **SID = class_id + 13300** ✅ 严格线性 |
| **Resource** | Resource List | 15000-15049 | type 1/6/101 的 `a`（resource_id） | **SID = res_id + 15000** ✅ 严格线性 |
| **Attribute** | Attribute List | 12200-12609 | type 0/4/5 的 `c`（attribute） | **SID = attr + 12200**（有少量跳跃缺口，如 attr 7/31/35-39 无 strings 条目） |
| 单位显示名 | — | 各段分散 | `language_dll_name` | 直接取 |
| 科技显示名 | — | 各段分散 | `language_dll_name` | 直接取 |

### ResearchLocation (研发地点 / 按钮)
| 属性 | 类型 | 说明 |
|------|------|------|
| `location_id` | int | 建筑 ID（如 CASTLE_ID=82） |
| `button_id` | int | 按钮位置 |
| `research_time` | int | 研发时间 |

### 关键操作模式
```python
# 用 get_ut 创建副本（配置文件驱动时 loader 自动调用）
new_tech_id, new_effect_id = get_ut(data, params, source_id, in_castle=True)
# get_ut 内部已做 tech.civ = -1，克隆 research_locations 并设 button_id

# 为已有 tech 绑定新 effect
tech = data.techs[tech_id]
effect = get_new_effect('some name')
bind_effect(data, tech, effect)
```

---

## Effect / EffectCommand

### Effect
| 属性 | 类型 | 说明 |
|------|------|------|
| `effect_commands` | List[EffectCommand] | 效果指令列表 |

### EffectCommand(type, a, b, c, d) 参数含义
所有 EffectCommand 的构造签名都是 `EffectCommand(type, a, b, c, d)`，不同 type 下 a/b/c/d 的含义不同。

| type | 功能 | a | b | c | d | utils 函数 |
|------|------|------|------|------|------|------------|
| **0** | set_unit_attribute | unit_id (或 -1 if b=-1 by class) | class_id (-1=by unit_id) | attribute | value | `set_unit_attribute` |
| **1** | 资源操作 | resource_id | 0=set, 1=plus | — | value | `set_resource`, `plus_resource` |
| **2** | enable/disable unit | unit_id | 1=enable, 0=disable | — | — | `enable_unit`, `disable_unit` |
| **3** | upgrade unit | from_unit_id | to_unit_id | mode(-1=所有同类) | — | `upgrade_unit` |
| **4** | plus_unit_attribute | unit_id | class_id (-1=by unit) | attribute | value | `plus_unit_attribute`, `plus_unit_attack`, `plus_unit_armor` |
| **5** | multiply_unit_attribute | unit_id | class_id (-1=by unit) | attribute | multiplier | `multiply_unit_attribute`, `multiply_unit_cost`, `multiply_unit_attack` |
| **6** | multiply_resource | resource_id | — | — | multiplier | `multiply_resource` |
| **8** | tech 开关 | tech_id | 12(固定) | **-1**=所有建筑生效，**≥0**=建筑下标（配合 research_locations 内各条目） | 1=enable, 2=force, 3=research。**注意**：enable(d=1) 仅对 `civ=-1` 的通用科技有效，文明专属科技只能用 force(d=2)；少数原生科技 enable 莫名无效，也需 force | `force_tech`, `research_tech`, `force_research_tech` |
| **101** | tech 成本 | tech_id | resource_id | 0=cost, 2=discount | value | `set_tech_cost`, `set_tech_discount` |
| **102** | disable_tech | — | — | — | tech_id | `disable_tech` |
| **103** | tech 研发时间 | tech_id | — | 0=time, 2=discount | value | `set_tech_time`, `set_tech_time_discount` |
| **203** | set_unit_attribute (selected) | 同 type 0 | 同 type 0 | 同 type 0 | 同 type 0 | `set_unit_attribute(selected=1)` |
| **204** | plus_unit_attribute (selected) | 同 type 4 | 同 type 4 | 同 type 4 | 同 type 4 | `plus_unit_attribute(selected=1)` |
| **205** | multiply_unit_attribute (selected) | 同 type 5 | 同 type 5 | 同 type 5 | 同 type 5 | `multiply_unit_attribute(selected=1)` |

> **注意**：`selected=1` 版本 (type 203/204/205) 只对**玩家自己选中的**单位生效，而 type 0/4/5 对所有单位生效。

### unit attribute 常用值 (type 0/4/5 的第 4 参数 = attribute)

**基本线性：SID = attr + 12200**（中间有少量跳跃缺口，如 attr 7/31/35-39 无 strings 条目）。完整列表见 strings Attribute List（SID 12200-12609）。

| attr | strings SID | strings 中文 | 含义 | 备注 |
|------|------------|-------------|------|------|
| 0 | 12200 | 生命值 | HP | |
| 1 | 12201 | 视野 | Line of Sight | |
| 5 | 12205 | 移动速度 | Speed | |
| 8 | 12208 | 护甲 | Armor | 用 utils 时自动编码 type（`value + 256 * armor_type`） |
| 9 | 12209 | 攻击力 | Attack | 用 utils 时自动编码 type（`value + 256 * attack_type`） |
| 11 | 12211 | 准确度百分比 | Accuracy | |
| 12 | 12212 | 最大射程 | Max Range | |
| 36 | 12301 | 训练时间 | Train time | strings 叫"训练时间" |
| 100 | — | — | Cost 乘子 | multiply_unit_cost 用这个（无 strings 条目） |
| 103 | — | — | Cost amount | set_unit_attribute(attr=103) 修改单位成本数值（无 strings 条目） |
| 105 | — | — | Train time | set_unit_attribute(attr=105) 修改训练时间（Corvinian Army 用的） |

#### 建筑附属存储量 (Storage Amount)
编年史建筑有附属存储槽，用于建造奖励资源。每个建筑原生定义了多个 storage slot，每个 slot 固定一种资源类型（食物/石头等）。通过 type 0/4/5 修改存储量数值：

| 值 | Constants.xs | 含义 | 典型案例 |
|----|-------------|------|----------|
| 21 | `cAmountFirstStorage` | 第 1 个附属存储量 | |
| 26 | `cAmountSecondStorage` | 第 2 个附属存储量 | Dropsite +10 石头 |
| 27 | `cAmountThirdStorage` | 第 3 个附属存储量 | Wu Dock +65 食物, Dropsite +35 食物 |

**注意**：这个属性依赖建筑原生定义好的 slot 资源类型，不是随便指定资源。例如 Effect #1084 (`C-Bonus, Military Buildings +65f`) 对 Dock 设 `type=4, a=DOCK_ID, c=27, d=55`，就是给 Dock 第三个 slot（食物）+55。但 Harbour（1189）原生 slot[2] 是 `type=-1`（无效），不是食物。

**船坞/巨港差异与修复（Thalassocracy 触发后）**：

| 项目 | Dock (45/51/47/133) | Harbor (1189) 原生 | Harbor 修复后 |
|------|---------------------|-------------------|--------------|
| slot[2] type | 0 (Food) | -1 (无效) | 0 (Food) ✅ 已修复 |
| slot[2] flag | 8 | 0 | 8 ✅ 已修复 |
| Wu Effect #1084 c=27 | 4 条 Dock 指令 | 无 Harbor 指令 | 追加 Harbor ✅ 已修复 |
| 核心科技 attack 指令 | 原生含 Harbor | — | 原生已覆盖，无需修复 |

**修复代码位置**：`unique_techs.py` Thalassocracy 段之后（双修复：unit storage + effect 指令追加）

### class_id 常用值 (type 0/4/5 的第 3 参数，用 -1 表示 by unit_id)

**严格线性：SID = class_id + 13300** ✅。dat `unit.class_` 直接等于 strings Class List 的 index。

> ⚠️ **重要区分**：这里的 `class_id` 是 **Class List（单位类别）**，和下面 Attack/Armor Type（护甲类型）是两套完全不同的编码。骆驼的**护甲类型**是 Attack/Armor Type 30，但其**单位类别**是 Class 12（骑兵）。马穆鲁克的**护甲类型**是 Attack/Armor Type 35，但其**单位类别**是 Class 12（骑兵）。判断"这是骆驼兵"要查 `unit.type_50.armours` 里有没有 armor type 30（见 `unique_techs.py:420`），不是查 `unit.class_`。

| class_id | strings SID | strings 中文 | 含义 | 代码验证 |
|----------|------------|-------------|------|---------|
| 0 | 13300 | 步弓手 | Archery / 远程单位（弓箭手、弩手、投矛手等） | custom_civ_bonus.py:687 `class_==0` 城堡 UU 步弓手 |
| 4 | 13304 | 平民 | Villager | |
| 6 | 13306 | 步兵 | Infantry（近战单位，不限生产建筑。兵营产：剑士、长枪兵、鹰勇士；城堡产：条顿骑士、日本武士） | unique_techs.py:580 `class_==6` Huskarl |
| 12 | 13312 | 骑兵 | Cavalry / 骑在马上的单位（不限生产建筑和攻击方式）。马厩产：游侠、骆驼兵、重装骆驼兵；城堡产：马穆鲁克 | custom_civ_bonus.py:352 `class_==12` |
| 13 | 13313 | 攻城武器 | Siege（牵引抛石机 class_=13） | |
| 18 | 13318 | 僧侣 | Monk | |
| 19 | 13319 | 贸易车 | Trade Cart | |
| 22 | 13322 | 战船 | Ship | |
| 36 | 13336 | 骑射手 | Cavalry Archers（骑射类，城堡产 UU：蒙古突骑、骆驼射手） | Mangudai(突骑) class_=36 ≠ 骑兵类 |
| 44 | 13344 | 火枪手 | Gunpowder | custom_civ_bonus.py:1045 `class_==44` |
| 51 | 13351 | 组装的单位 | Assembled Unit | 巨型投石机（组装状态）class_=51 |
| 54 | 13354 | 拆装的攻城单位 | Disassembled siege | 巨型投石机 class_=54 |
| 55 | 13355 | 弩炮 | Ballista / Scorpion | 弩炮 class_=55 |

> ⚠️ **步兵类 ≠ 兵营单位**：class 6 strings 叫"步兵"，但条顿骑士、日本武士这两个城堡产的 UU 也是 class 6。
> ⚠️ **骑兵类 ≠ 马厩单位**：class 12 strings 叫"骑兵"（骑在马上的单位），但马穆鲁克是城堡产的，游侠和骆驼兵是马厩产的。
> ⚠️ **骑兵类 ≠ 骑射类**：class 12 是骑兵（近战/投掷），class 36 是骑射手（远程）。蒙古突骑 class_=36，不是 12。
> ⚠️ **弩炮 class_=55**：Scorpion 在游戏里指弩炮，strings Class List 里 class 55 就是"弩炮"。不要和攻城武器 class 13 混淆。

**完整 Class List（strings 13300-13366）：**

| class_id | 中文 | class_id | 中文 | class_id | 中文 |
|----------|------|----------|------|----------|------|
| 0 | 步弓手 | 22 | 战船 | 44 | 火枪手 |
| 1 | 古物 | 23 | 西班牙征服者 | 45 | 双手剑士 |
| 2 | 贸易艇 | 24 | 战象 | 46 | 长枪兵 |
| 3 | 建筑 | 25 | 英雄 | 47 | 侦察 |
| 4 | 平民 | 26 | 骑象射手 | 48 | 矿场 |
| 5 | 海洋鱼群 | 27 | 城墙 | 49 | 农田 |
| 6 | 步兵 | 28 | 方阵步兵 | 50 | 长矛兵 |
| 7 | 浆果灌木丛 | 29 | 家畜 | 51 | 组装的单位 |
| 8 | 石矿 | 30 | 旗帜 | 52 | 箭塔 |
| 9 | 被捕食动物 | 31 | 深海鱼类 | 53 | 登船 |
| 10 | 捕食性动物 | 32 | 金矿 | 54 | 拆装的攻城单位 |
| 11 | 其他 | 33 | 海滨鱼群 | 55 | 弩炮 |
| 12 | 骑兵 | 34 | 悬崖 | 56 | 突袭者 |
| 13 | 攻城武器 | 35 | 爆破兵 | 57 | 骑兵突袭者 |
| 14 | 地形 | 36 | 骑射手 | 58 | 牲畜 |
| 15 | 树木 | 37 | 幽灵 | 59 | 国王 |
| 16 | 树桩 | 38 | 鸟 | 60 | 其他建筑 |
| 17 | 治疗者 | 39 | 城门 | 61 | 可控制的动物 |
| 18 | 僧侣 | 40 | 打捞堆 | | |
| 19 | 贸易车 | 41 | 资源堆 | | |
| 20 | 运输船 | 42 | 圣物 | | |
| 21 | 捕鱼艇 | 43 | 带着圣物的僧侣 | | |

### Attack Type / Armor Type 完整对照 (攻击和护甲共用同一套 ID)

> ⚠️ **与 Class 的关键区别**：这一套编码是 **护甲/攻击类型**，出现在 `unit.type_50.attacks[i].class_` 和 `unit.type_50.armours[i].class_` 里。和上面的 Class List（`unit.class_`）是两套独立编码。例如骆驼骑兵的 `unit.class_` = 12（骑兵，Class List），但其 `armour.class_` 包含 30（骆驼单位，Armor Type）。

**两个来源，互为补充：**

| 来源 | 路径 | 面向用户 | 覆盖范围 |
|------|------|---------|---------|
| **AGE3NamesV0007.ini** | `Tools_Builds\AGE3NamesV0007.ini [AoE2DEArmorNames]` | 编辑器(Age3Editor)/mod 开发者 | type 0-36（`NumAoE2DEArmors=37`） |
| **strings 中文文本** | `resources\zh\strings\key-value\key-value-strings-utf8.txt` SID 12400-12599 | 游戏内玩家显示 | type 0-49, 60, 61 |

**SID = type + 12400** ✅ 严格线性（这是所有编码类型中最规整的）。

utils 中编码公式：`value + 256 * type`（type 即下表的值）。

#### 基础类型（type 0-36，两个来源均覆盖）

| type | AGE3Names 英文 | strings 官方中文 | 差异 / 说明 |
|------|---------------|-----------------|------------|
| 0 | Unused | 未使用的护甲 0 | 保留位 |
| 1 | Infantry | 步兵 | |
| 2 | Turtle Ships | 主力舰 | 龟船等主力舰共用此护甲类型 |
| 3 | Base Pierce | 远程伤害 | 远程武器（最常用！） |
| 4 | Base Melee | 近战 | 近战武器（最常用！） |
| 5 | War Elephants | 大象单位 | |
| 6 | Unused | 未使用的护甲 6 | 保留位 |
| 7 | Unused | 未使用的护甲 7 | 保留位 |
| 8 | Cavalry | 骑兵 | |
| 9 | Unused | 未使用的护甲 9 | 保留位 |
| 10 | Unused | 未使用的护甲 10 | 保留位 |
| 11 | All Buildings (**except Port**) | **所有建筑** | ⚠️ AGE3 标注"except Port"，但游戏内 Harbor（1189）实际也吃 type 11 伤害 |
| 12 | Unused | 未使用的护甲 12 | 保留位 |
| 13 | Stone Walls & Gates & Towers | **石料防御** | strings 更简洁，实际覆盖石墙、城门、塔楼 |
| 14 | Predator Animals | 捕食性动物 | 狼、豹等掠食动物 |
| 15 | Archers | 步弓手 | 远程步兵单位 |
| 16 | Ships & Saboteur | 船舰 | 战舰、爆破者 |
| 17 | Rams & Trebuchet & Siege Towers | **冲车** | ⚠️ strings 只写"冲车"但实际覆盖所有攻城器 |
| 18 | Trees | 树木 | |
| 19 | Unique Units (except Turtle Ship) | 独特单位 | |
| 20 | Siege Weapons | 攻城武器 | |
| 21 | Standard Buildings | 标准建筑 | |
| 22 | Walls & Gates | 城墙与城门 | |
| 23 | Gunpowder Units | 火药单位 | |
| 24 | **Hunted Predator Animals** | **野猪** | AGE3 强调"被捕猎的掠食动物"，strings 具体到"野猪" |
| 25 | Monks | 僧侣 | |
| 26 | Castle | 城堡 | |
| 27 | Spearmen | 长矛兵 | |
| 28 | Cavalry Archers | 骑射手 | |
| 29 | **Eagle Warriors** | **冲击步兵** | DE 版本已从"鹰战士"改名为"冲击步兵"，AGE3 是旧名 |
| 30 | Camels | 骆驼单位 | 骆驼骑兵专属护甲类型。骆驼的 unit class=12（骑兵），armor type=30。`unique_techs.py:420` 用 `armor.class_==30` 识别骆驼 |
| 31 | **Leitis Attack** | **未使用的护甲 31** | ⚠️ DE 更新后此类型已废弃，strings 官方标为未使用；但阿契美尼德 Sagaris 仍使用此 type 值 |
| 32 | Condottiero | 意大利佣兵 | |
| 33 | Unused | 未使用的护甲 33 | 保留位 |
| 34 | Fishing Ship | 捕鱼船 | |
| 35 | Mamelukes | 马穆鲁克 | 马穆鲁克专属护甲类型。马穆鲁克的 unit class=12（骑兵），armor type=35 |
| 36 | Heroes | 英雄和国王 | |

#### 高号段类型（AGE3NamesV0007 无英文命名，strings 有中文）

| type | strings 官方中文 | strings 官方英文 | 说明 |
|------|-----------------|-----------------|------|
| 37 | 重型攻城武器 | Heavy Siege | |
| 38 | 掷矛手 | Skirmishers | |
| 39 | 龙脉 | Royal Heirs | 埃塞俄比亚银冠科技 |
| 40 | 未使用的护甲 40 | Unused Armor 40 | 保留位 |
| 41 | 喷火船 | Fire Ships | |
| 42-49 | 未使用的护甲 42-49 | Unused Armor 42-49 | 保留位 |
| 60 | 远程战船 | Long-Range Warships | |
| 61 | 保留 | <!--RESERVED--> | 官方标记 `<!--RESERVED-->` |

### Resource ID 常用值 (type 1/6/101 的 resource_id)

**严格线性：SID = res_id + 15000**，strings 见 Resource List（SID 15000-15049）。

| res_id | strings SID | strings 中文 | 含义 |
|--------|------------|-------------|------|
| 0 | 15000 | 食物储备 | Food |
| 1 | 15001 | 木材储备 | Wood |
| 2 | 15002 | 石料储备 | Stone |
| 3 | 15003 | 黄金储备 | Gold |

> Resource 编码在 effect command 中出现在 type 1（资源 set/plus）、type 6（multiply_resource）、type 101（tech 成本/折扣）的 `resource_id` 参数位置。

---

## 常量速查 (`constants.py`)
| 常量 | 值 | 说明 |
|------|----|------|
| `CASTLE_ID` | 82 | 城堡 |
| `BARRACK_ID` | 12 | 兵营 |
| `STABLE_ID` | 101 | 马厩 |
| `ARCHERY_RANGE_ID` | 87 | 射箭场 |
| `SIEGE_ID` | 49 | 攻城器工厂 |
| `MONESTARY_ID` | 104 | 修道院 |
| `UNIV_ID` | 209 | 大学 |
| `DOCK_ID` | 45 | 码头 |
| `BLACKSMITH_ID` | 103 | 铁匠铺 |
| `HARBOR_ID` | 1189 | 巨港 |
| `PORT_ID` | 2172 | 编年史专属港口 |
| `SHIPYARD_ID` | 2119 | 编年史专属造船厂 |
| `CHRONICLE_CIV_IDS` | [46,47,48,54,55,56] | 编年史文明 |
| `GAME_DATA_PATH` | — | 运行时解析的 mod dat 目录 |

> **编年史文明判断方法**：
> 1. 用 `civ_id in CHRONICLE_CIV_IDS` 直接查常量
> 2. 检测文明 effect 里有没有 `type=101 (tech cost), tech_id=1138, resource_id=0, amount=0`（Tech 1138 = Paphos Shadow Tech，编年史文明原生 effect 把它成本设为 0 来激活，作为编年史标记）
>
> ⚠️ **重要**：Tech 1138 只是个标记，不是开关。普通文明就算自己加 effect 把 1138 cost 设为 0，也不会自动获得编年史专属的 Port(2172)、Shipyard(2119)、区域船等单位和科技。编年史的专属内容由多个原生机制共同控制：
> - **civ 覆盖表**：编年史的 `civs[civ_id].units` 直接把 FSHSP(13)/COGXX(17) 等船的 train_locations 改到 Port(2172) 而不是 Dock(45)
> - **enable tech 链**：Tech 1138 + Tech 1209 → Tech 1140 (Enable Shipyard, civ=-1, loc=-1 隐藏按钮) → Effect 1144 用 type=2 b=-1 启用 Shipyard(2119) 和 Shipyard2(2120)
> - **互斥 UT 布局**：编年史科技树原生在 Castle 有两对互斥独特科技（7/8 位互斥银冠，12/13 位互斥金冠）
>
> 项目 mod 中 `civ_bonuses.py` 专门处理了让所有文明都能同时在 Dock 和 Port 生产船的逻辑。

---

## 独特科技俗称

| 俗称 | 正式名称 | 时代 | 说明 |
|------|---------|------|------|
| 银冠 | 城堡时代独特科技（Castle Age Unique Tech） | 城堡 | 城堡时代解锁，因图标是银色皇冠而俗称"银冠" |
| 金冠 | 帝王时代独特科技（Imperial Age Unique Tech） | 帝王 | 帝王时代解锁，因图标是金色皇冠而俗称"金冠" |

---

## 按钮位置约定

### 普通文明
| 位置 | 内容 |
|------|------|
| 0~5 | 科技位（UT 常用 0 位） |
| 6 | UU 科技（unique unit upgrade） |
| 7/8 | UT 原生位（银冠 / 金冠，用于扫描检测独特科技） |
| -1 | 隐藏 |

### 编年史文明（ACHAEMENIDS, ATHENIANS, MACEDONIANS, PURU, SPARTANS, THRACIANS）
编年史有两对互斥的独特科技，玩家每对选其一：
| 位置 | 内容 |
|------|------|
| 7 / 8 | 互斥银冠（二选一） |
| 12 / 13 | 互斥金冠（二选一） |

---

## utils.py 核心工具函数

### Tech / Effect 创建
| 函数 | 说明 |
|------|------|
| `append_tech(data, tech, effect=None)` | 新建 tech，可选同时绑 effect |
| `bind_effect(data, tech, effect)` | 为已有 tech 绑定新 effect（做 effect_id=len+append） |
| `get_ut(data, params, source_id, in_castle=False)` | 克隆原生 tech 副本，自动 civ=-1，设 button_id。返回 `(tech_id, effect_id)` |
| `get_new_tech(name)` | 创建新 tech 对象（未 append） |
| `get_new_effect(name)` | 创建新 effect 对象（未 append） |
| `disable_tech(effect, tech_id)` | 追加 disable_tech 指令 (type 102) |
| `set_require_techs(tech, *ids)` | 设置前置科技，自动补 -1 到 6 个槽 |

### 单位/文明开关
| 函数 | 说明 |
|------|------|
| `enable_unit(effect, unit_id)` | type 2, b=1 |
| `disable_unit(effect, unit_id)` | type 2, b=0 |
| `force_tech(effect, tech_id)` | type 8, d=2（冗余：get_ut 已设 tech.civ=-1） |
| `research_tech(effect, tech_id)` | type 8, d=3 |
| `force_research_tech(effect, tech_id)` | force + research |

### 属性修改
| 函数 | 说明 |
|------|------|
| `set_unit_attribute(effect, unit_id, class_id, attr, val, selected=0)` | 覆盖，type 0 或 203 |
| `plus_unit_attribute(effect, unit_id, class_id, attr, val, selected=0)` | 加法，type 4 或 204 |
| `multiply_unit_attribute(effect, unit_id, class_id, attr, mul, selected=0)` | 乘法，type 5 或 205 |
| `plus_unit_attack(effect, unit_id, class_id, val, type)` | attr=9，自动编码 type |
| `plus_unit_armor(effect, unit_id, class_id, val, type)` | attr=8，自动编码 type |
| `multiply_unit_cost(effect, unit_id, class_id, mul)` | attr=100 |
| `multiply_unit_attack(effect, unit_id, class_id, pct, type)` | attr=9 |

### 科技修改
| 函数 | 说明 |
|------|------|
| `set_tech_cost(effect, tech_id, res_id, val)` | type 101, c=0 |
| `set_tech_discount(effect, tech_id, res_id, val)` | type 101, c=2 |
| `set_tech_time(effect, tech_id, val)` | type 103, c=0 |
| `set_tech_time_discount(effect, tech_id, val)` | type 103, c=2 |

### 资源
| 函数 | 说明 |
|------|------|
| `plus_resource(effect, res_id, val)` | type 1, b=1 |
| `set_resource(effect, res_id, val)` | type 1, b=0 |
| `multiply_resource(effect, res_id, mul)` | type 6 |

### 按钮操作
| 函数 | 说明 |
|------|------|
| `move_unit_button(effect, unit_id, button)` | type 107 或类似，调整单位按钮位置 |
| `move_tech_button(effect, tech_id, button)` | 调整科技按钮位置 |

### 其他
| 函数 | 说明 |
|------|------|
| `extend_effect(effect, unit_ids=[], class_ids=[])` | 复制 effect_commands 对指定 unit/class 生效 |
| `upgrade_unit(effect, from_id, to_id, mode=-1)` | type 3 |