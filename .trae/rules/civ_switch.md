# Civ Switch 机制详解

## 一、Civ Switch 是什么

Civ Switch 是本 mod 的**核心机制**——让玩家在游戏中通过一个"切换到X"按钮，把自己当前文明的独特单位（UU）和独特科技（UT）**替换成目标文明**的 UU/UT。

原理是利用 AoE2 dat 的两个 EffectCommand：
- `type=2` c=1/c=0：enable_unit / disable_unit（启用或禁用单位）
- `type=0` c=43：设置单位训练按钮位（-1 = 隐藏）
- `type=8` b=5：设置科技按钮位（-1 = 隐藏）

每个"切换到X"科技的 effect 就是一套"显示X的东西，隐藏其他所有东西"的指令集合。

---

## 二、整体调用链

```
add_switch.py::adding_switch()      ← 先调用，预留空间 + 初始化 params
    ↓ 返回 params
update_all_in_1.py 依次执行：
    deal_ftt()          FTT 补丁（单位/科技默认按钮位置）
    add_civ_bonuses()   文明专属加成
    build_discount_tech() 折扣合并
    add_unique_techs()  独特科技效果
    add_civ_switch()    ← 这里读 unit_switch.json，真正干活
    auto_extend_building_effects()  自动扩展建筑变体效果
```

---

## 三、add_civ_switch() 六步主流程

### 第 1 步：自动发现 UU / UT / Elite UU

代码位置：`civ_switch.py:158-188`

从原生 dat 中扫描三个字典：

| 字典 | 含义 | 识别条件 |
|------|------|---------|
| `uu_tech_id_list[civ_id]` | **精锐 UU 升级科技** ID | Castle(82) + button_id==6（专指精锐城堡独特兵升级） |
| `uu_id_list[civ_id]` | **基础 UU** ID | effect command.type==2（enable_unit）且该单位 train_location 在 Castle button==1 |
| `elite_uu_id_list[civ_id]` | **精锐 UU** ID | effect command.type==3（upgrade_unit）且 command.a 是已知的基础 UU ID → command.b 就是精锐形态 |

### 第 2 步：硬编码特殊处理

`civ_switch.py:196-204`

- **Huskarl**（哥德 Goths，tech ID 365）：把 UT 的研究位置追加到 Barracks
- **Tarkan**（匈奴 Huns，tech ID 2）：把 UT 的研究位置追加到 Stable

这两个是因为它们原本只能在城堡研究，为了 All-in-1 切换后在原建筑也能出，需要加额外研究位置。

### 第 3 步：为每个文明创建"切换到X"科技

循环 `for civ_id in range(1, current_civ_num)` 共 ~62 次，每次创建一个 tech + effect。

核心逻辑（`civ_switch.py:214-227`）：

```python
for j in range(1, current_civ_num):
    if j == civ_id:
        # 当前目标文明自己的东西：显示出来
        disable_unit(effect, civ_switch_unit_offset_id + j)   # 隐藏"切换到自己"按钮
        move_unit_button(effect, uu_id_list[j], 1)            # UU 放回城堡 button 1
        move_tech_button(effect, uu_tech_id_list[j], 6, 0)   # UT 放回城堡 button 6
    else:
        # 其他文明的东西：全部隐藏
        enable_unit(effect, civ_switch_unit_offset_id + j)    # 显示"切换到其他"按钮
        move_unit_button(effect, uu_id_list[j], -1)           # 隐藏其他 UU
        move_tech_button(effect, uu_tech_id_list[j], -1, 0)   # 隐藏其他 UT
```

然后调用 `_execute_unit_switch()` 处理 unit_switch.json 配置（多文明共享兵种线但外观不同的情况，见第五节）。

最后是几处硬编码特殊文明单位（`civ_switch.py:230-251`）：
- Sicilians → Donjon (unit 1659)
- Bulgarians → Krepost (unit 1227)
- Huns → Cavalry / Heavy Cavalry (886 / 887)
- Goths → Huskarl / Elite Huskarl (759 / 761)

### 第 4 步：创建可点击的切换按钮单位

`civ_switch.py:254-270`

为**每个文明的每个文明**创建一个 dead unit（`get_dead_unit`，从 trebuchet 模板拷贝再清空）：
- 图标 = 目标文明的 Elite UU 图标（玩家通过图标一眼认出"这是切换到XX"）
- 训练建筑 = MULE_CART_ID（市场旁的运货车位置）
- 按钮位置 = 通过 `get_next_position()` 在 MULE_CART / MILL / BLACKSMITH 的空位依次排布
- 单位的 `building.tech_id` 指向对应的"切换到X"科技（点击单位 = 研发科技 = 触发 effect）

### 第 5 步：初始化科技

`civ_switch.py:272-288`

| 科技 | 依赖 | 效果 |
|------|------|------|
| "disable civ switch" | switch_tech_id（总开关） | 默认 disable 所有 switch unit → 玩家激活前看不到切换按钮 |
| "initialize civ switch X" | switch_tech_id + feudal_duplicate_tech_id | force + research 对应的 switch tech → 自动激活当前文明自己的切换 |

每个文明都有一个 initialize 科技，`tech.civ = civ_id` 表示只对该文明生效。

### 第 6 步：精锐 UU 自动激活

`civ_switch.py:290-296`

科技 "enable elite uu tech"：
- 依赖：switch_tech_id + imp_duplicate_tech_id + 266（Imperial Age 原生科技）
- 效果：对所有 `uu_tech_id_list[civ_id]` 执行 `force_tech` → 进入帝王时代自动获得全部精锐 UU 升级

---

## 四、玩家视角的工作流程

```
1. 打开 All-in-1 开关（Activate switch 科技）
   → switch_tech 被激活 → 解锁时代线和 initialize 科技

2. 进入封建时代
   → initialize civ switch [当前文明] 自动触发
   → 当前文明自己的 UU/UT 已在原位，其他文明的 UU/UT 被隐藏
   → 市场旁运货车位置出现一排切换按钮（每个文明一个）

3. 点击"切换到 Persians"（假设当前是 Britons）
   → 研发 Persians 对应的 switch tech
   → effect 执行：
     • 隐藏 Britons 的 UU(Elite Longbowman) 和 UT(Longbow 升级科技)
     • 显示 Persians 的 UU(Elite War Elephant) 和 UT(Walhalla)
     • 同时触发 unit_switch.json 里 Persian 匹配的 category（骑兵线 → 显示 Asadi 骑兵）

4. 进入帝王时代
   → "enable elite uu tech" 自动触发
   → 当前激活的所有精锐 UU 升级科技被 force（虽然上面第 3 步已经在 Castle button 6 了）
```

---

## 五、unit_switch.json 与 _execute_unit_switch()

### 为什么需要它

上述第 3 步的硬编码循环只处理"城堡独特单位/科技"。但很多兵种线是**跨文明共享但外观不同**的，例如：
- 攻城船：Dromon（拜占庭/匈奴）、楼船（中国三朝）、Catapult Galleon（玛雅等）、Cannon Galleon（西欧默认）
- 骑射手：蒙古突骑（东亚）、Mounted Crossbowman（西欧）、Elephant Archer（印度）
- 骑兵：东亚重骑（Hei Guang）、西方默认重骑、Xolotl（美洲）

这些需要按文明"显示A的单位线，隐藏B的单位线"——这就是 unit_switch.json 的用途。

### JSON 结构

```json
[
  {
    "category_name": "cavalry",      // 描述性名称，仅日志使用
    "unit_button_id": 2,             // 启用的单位放 Stable button 2
    "tech_button_id": 7,             // 启用的科技放 Stable button 7
    "switch_contents": [
      {
        "unit_name": "Hei Guang",
        "civ_match": {
          "civ_names": ["Wei", "Shu", "Wu"]
        },
        "unit_ids": [1944, 1946],
        "tech_ids": [1033]
      },
      {
        "unit_name": "Default",
        "civ_match": { "default": true },
        "unit_ids": [38, 283, 569],
        "tech_ids": [209, 265]
      }
    ]
  }
]
```

civ_match 的匹配优先级：
1. **精确匹配**：`civ_names` 包含当前文明名，或 `civ_ids` 包含当前文明 ID
2. **default 回退**：`"default": true` 的条目兜底（注意 default 的 `_civ_matches` 永远返回 False，所以总是作为 fallback）

### _execute_unit_switch() 执行逻辑

`civ_switch.py:64-100`

```
对每个 category：
  1. 找匹配的 switch_content target_sc（先精确匹配，找不到用 default）
  2. 计算 all_uids / all_tids：把该 category 下所有 switch_contents 的 unit_ids / tech_ids 取并集
  3. target_sc 的 unit_ids / tech_ids 就是 enable 列表
  4. 不在 enable 列表的 → move_button(-1) 隐藏
  5. 在 enable 列表的 → move_button(category 的 unit_button_id / tech_button_id)
```

### 别名机制

tech_ids / unit_ids 可以是 int（直接 ID）或 str（别名）。别名必须在 `unique_techs_config.json` 的 `register_as` 字段注册，由 `unique_techs_config_loader.py` 解析后放入 `params.other_params`。

解析代码在 `civ_switch.py:33-45` 的 `_resolve_id()`。

### 注意事项

- **一个 category 内所有 switch_contents 共享同一套 unit_button_id 和 tech_button_id**，没有独立按钮位概念
- **default 条目不是必须的**。有些 category（如 `unique building 1`、`unique infantry`）故意没有 default:true 条目，只对精确 civ_match 到的文明生效。不匹配任何条目的文明，整个 category 跳过（target_sc = None），不做任何 move_button 操作
- **编年史文明**（Achaemenids/Athenians/Spartans/Macedonians/Thracians/Puru）科技树特殊，在多个 category 里碰不到匹配条目，这是预期行为
- **unit_ids 和 tech_ids 中只写"最终形态"**，不需要同时写精锐前/精锐后两个阶段（例如只写 1946，不用同时写 1944+1946 的所有中间态——不过实际代码里有的地方两种都写了，属项目风格）

---

## 六、关键数据结构：All_In_1_Params

| 字段 | 类型 | 谁设值 | 谁消费 |
|------|------|--------|--------|
| `switch_tech_id` | int | add_switch | 所有后续模块做前置依赖 |
| `feudal_duplicate_tech_id` | int | add_switch | civ_switch initialize 科技依赖 |
| `imp_duplicate_tech_id` | int | add_switch | civ_switch enable elite uu 科技依赖 |
| `civ_index_to_additional_uts` | dict[int, list[int]] | unique_techs | civ_switch 第 3 步处理额外 UT 按钮 |
| `other_params` | dict[str, int] | unique_techs_config_loader | civ_switch _resolve_id() 解析别名 |
| `bug_compat` | bool | 默认 True | regional_units / civ_bonuses 控制 bug workaround |

---

## 七、EffectCommand 操作速查

| 项目函数 | EffectCommand | 含义 |
|---------|--------------|------|
| `enable_unit(effect, unit_id)` | type=2, a=unit_id, c=1 | 启用单位 |
| `disable_unit(effect, unit_id)` | type=2, a=unit_id, c=0 | 禁用单位 |
| `move_unit_button(effect, uid, bid)` | type=0, a=uid, c=43, d=bid | 设置按钮位（-1=隐藏） |
| `move_tech_button(effect, tid, bid, idx)` | type=8, a=tid, b=5, c=idx, d=bid | 设置科技按钮位（-1=隐藏） |
| `force_tech(effect, tid)` | type=8, a=tid, c=12, d=2 | 强制科技可用 |
| `research_tech(effect, tid)` | type=8, a=tid, c=12, d=3 | 立即研发 |
| `force_research_tech(effect, tid)` | force_tech + research_tech | 强制可用 + 立即研发 |

---

## 八、新增配置的工作流程

### 场景 A：添加新的兵种分支到现有 category

例如想把 "Xolotl Jaguar Rider" 加进 cavalry category（目前它只在 cavalry archer 里）：

1. 确认该兵种的 unit_ids（普通 + 精锐）和 tech_ids（升级科技）
2. 在 `unit_switch.json` 的 `"category_name": "cavalry"` 下新增一个 switch_content
3. 配置 `civ_match`（哪些文明匹配）
4. 如果 tech_ids 里的科技是 `unique_techs_config.json` 里注册过的，直接用别名；否则写数字 ID

### 场景 B：添加全新的 category

1. 先在 dat 中确认该兵种在哪个建筑生产（决定了 unit_button_id 放在哪个建筑的 button 位置）
2. 在 `unit_switch.json` 顶层数组中添加新 category 对象
3. 按文明分组写 switch_contents，按需配置 default:true 兜底条目（不是必须，没有 default 时未精确匹配的文明整个 category 跳过）
4. 运行 `python update_all_in_1.py` 验证

### 场景 C：添加新的独特科技别名

1. 在 `unique_techs_config.json` 对应建筑 section 里添加条目，含 `register_as`
2. `unique_techs_config_loader.py` 会自动把它放进 `params.other_params`
3. 然后就可以在 `unit_switch.json` 里用字符串别名引用