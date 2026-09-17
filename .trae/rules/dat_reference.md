# AoE2DE Dat 数据结构速查

## DatFile 入口
```python
data.techs          # List[Tech]
data.effects        # List[Effect]
data.civs[0].units  # List[Unit] - 通用单位表
data.civs[civ_id]   # 指定文明的单位覆盖（通常不直接用）
```

---

## Tech (科技)
| 属性 | 类型 | 说明 |
|------|------|------|
| `civ` | int | 所属文明，**-1 = 所有文明可用** |
| `effect_id` | int | 关联的 Effect 索引 |
| `icon_id` | int | 图标 ID |
| `name` | str | SID（原生 tech）或显示名（我们创建的副本）。effect.name 是效果显示名 |
| `required_techs` | Tuple[int, 6] | 前置科技索引列表，**-1 = 空槽** |
| `required_tech_count` | int | 最少需要多少个前置非-1 |
| `research_locations` | List[ResearchLocation] | 研发地点列表（原生 tech 通常只有一个，get_ut 创建的副本可能有多个——每个建筑 section 对应一个） |

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
type = 第一个参数 = 功能类型。其他参数名用 utils 函数签名里的顺序（a, b, c, d 或在某些工具函数里叫 c, a, b, d, e），**以下按 EffectCommand(type, p1, p2, p3, p4) 的顺序描述**：

| type | 功能 | p1 (type之后第一参) | p2 | p3 | p4 | utils 函数 |
|------|------|------|------|------|------|------------|
| **0** | set_unit_attribute | unit_id (或 -1 if p2=-1 by class) | class_id (-1=by unit_id) | attribute | value | `set_unit_attribute` |
| **1** | 资源操作 | resource_id | 0=set, 1=plus | — | value | `set_resource`, `plus_resource` |
| **2** | enable/disable unit | unit_id | 1=enable, 0=disable | — | — | `enable_unit`, `disable_unit` |
| **3** | upgrade unit | from_unit_id | to_unit_id | mode(-1=所有同类) | — | `upgrade_unit` |
| **4** | plus_unit_attribute | unit_id | class_id (-1=by unit) | attribute | value | `plus_unit_attribute`, `plus_unit_attack`, `plus_unit_armor` |
| **5** | multiply_unit_attribute | unit_id | class_id (-1=by unit) | attribute | multiplier | `multiply_unit_attribute`, `multiply_unit_cost`, `multiply_unit_attack` |
| **6** | multiply_resource | resource_id | — | — | multiplier | `multiply_resource` |
| **8** | tech 开关 | tech_id | 12(固定) | — | 1=researchable, 2=force, 3=research | `force_tech`, `research_tech`, `force_research_tech` |
| **101** | tech 成本 | tech_id | resource_id | 0=cost, 2=discount | value | `set_tech_cost`, `set_tech_discount` |
| **102** | disable_tech | — | — | — | tech_id | `disable_tech` |
| **103** | tech 研发时间 | tech_id | — | 0=time, 2=discount | value | `set_tech_time`, `set_tech_time_discount` |
| **203** | set_unit_attribute (selected) | 同 type 0 | 同 type 0 | 同 type 0 | 同 type 0 | `set_unit_attribute(selected=1)` |
| **204** | plus_unit_attribute (selected) | 同 type 4 | 同 type 4 | 同 type 4 | 同 type 4 | `plus_unit_attribute(selected=1)` |
| **205** | multiply_unit_attribute (selected) | 同 type 5 | 同 type 5 | 同 type 5 | 同 type 5 | `multiply_unit_attribute(selected=1)` |

> **注意**：`selected=1` 版本 (type 203/204/205) 只对**玩家自己选中的**单位生效，而 type 0/4/5 对所有单位生效。

### unit attribute 常用值 (type 0/4/5 的第 4 参数 = attribute)
| 值 | 含义 | 备注 |
|----|------|------|
| 0 | HP | |
| 8 | Armor | 用 utils 时自动编码 type（`value + 256 * armor_type`） |
| 9 | Attack | 用 utils 时自动编码 type（`value + 256 * attack_type`） |
| 14 | Range | |
| 36 | Train time | 单位训练时间 |
| 40 | Accuracy | |
| 100 | Cost 乘子 | multiply_unit_cost 用这个 |
| 103 | Cost amount | set_unit_attribute(attr=103) 修改单位成本数值 |
| 105 | Train time | set_unit_attribute(attr=105) 修改训练时间（Corvinian Army 用的） |

### class_id 常用值 (type 0/4/5 的第 3 参数，用 -1 表示 by unit_id)
| 值 | 含义 |
|----|------|
| 0 | Archery (远程单位) |
| 1 | Infantry |
| 2 | Cavalry |
| 3 | Ship |
| 4 | Trade Cart |
| 5 | Building |
| 6 | Mountain Monk (骆驼骑兵) |
| 7 | Siege |
| 8 | Villager |
| 9 | Monk |
| 10 | Fish |
| 11 | Military Building |
| 12 | Horse and Camel |

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
| `CHRONICLE_CIV_IDS` | [46,47,48,54,55,56] | 编年史文明 |
| `GAME_DATA_PATH` | — | 运行时解析的 mod dat 目录 |

---

## 按钮位置约定
| 位置 | 内容 |
|------|------|
| 0~5 | 科技位（UT 常用 0 位，UU 科技用 6） |
| 6 | UU 科技（unique unit upgrade） |
| 7/8 | UT 原生位（用于扫描检测独特科技） |
| -1 | 隐藏 |

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
| `enable_unit(effect, unit_id)` | type 2 p2=1 |
| `disable_unit(effect, unit_id)` | type 2 p2=0 |
| `force_tech(effect, tech_id)` | type 8 p4=2（冗余：get_ut 已设 tech.civ=-1） |
| `research_tech(effect, tech_id)` | type 8 p4=3 |
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
| `set_tech_cost(effect, tech_id, res_id, val)` | type 101 p3=0 |
| `set_tech_discount(effect, tech_id, res_id, val)` | type 101 p3=2 |
| `set_tech_time(effect, tech_id, val)` | type 103 p3=0 |
| `set_tech_time_discount(effect, tech_id, val)` | type 103 p3=2 |

### 资源
| 函数 | 说明 |
|------|------|
| `plus_resource(effect, res_id, val)` | type 1 p2=1 |
| `set_resource(effect, res_id, val)` | type 1 p2=0 |
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