# AoE2DE 文明科技树 JSON 文件参考

## 文件位置

``
C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\CivTechTrees\
``

## 文件列表

共 62 个 .json 文件，文件名格式为**全大写文明名** + .json：

- ACHAEMENIDS, ARMENIANS, ATHENIANS, AZTECS
- BENGALIS, BERBERS, BOHEMIANS, BRITONS, BULGARIANS, BURGUNDIANS, BURMESE, BYZANTINES
- CELTS, CHINESE, CUMANS, DANES, DRAVIDIANS, ETHIOPIANS
- FRANKS, GEORGIANS, GOTHS, GURJARAS
- HUNS, INCAS, INDIANS, ITALIANS
- JAPANESE, JURCHENS, KHITANS, KHMER, KOREANS
- LITHUANIANS, MACEDONIANS, MAGYAR, MALAY, MALIANS, MAPUCHE, MAYANS, MONGOLS, MUISCA
- PERSIANS, POLES, PORTUGUESE, PURU
- ROMANS, SARACENS, SAXONS, SHU, SICILIANS, SLAVS, SPANISH, SPARTANS
- TATARS, TEUTONS, THRACIANS, TUPI, TURKS
- VARANGIANS, VIETNAMESE, VIKINGS
- WEI, WU

注意：civ_switch.py 里做文明名匹配用的是 dat 返回名（首字母大写，如 Byzantines），和这里的全大写文件名不同。

## JSON 顶层结构

``json
{
  "civ_id": 1,
  "civ_techs_units": [ ... ],
  "civ_techs_buildings": [ ... ]
}
``

| Key | 类型 | 说明 |
|-----|------|------|
| civ_id | int | 文明索引（1=Britons）。编年史文明共 6 个，按名称枚举：Achaemenids(46), Athenians(47), Spartans(48), Macedonians(54), Thracians(55), Puru(56)——**不是连续区间**，中间夹着 Shu(49), Wu(50), Wei(51), Jurchens(52), Khitans(53) |
| civ_techs_units | list | **核心**：单位、升级、科技、独特单位、独特科技全在这里（按 Node Type 区分） |
| civ_techs_buildings | list | 建筑节点 |

## 节点通用字段

| 字段 | 类型 | 说明 |
|------|------|------|
| Name | str | 游戏内英文显示名（如 "Dromon", "Cannon Galleon"） |
| Node Type | str | 节点类别（见下表） |
| Node Status | str | 可用性（见下表） |
| Node ID | int | **关键！** 单位/科技/建筑在 dat 文件中的 ID，直接等于 dat.civs[0].units[id].ID |
| Trigger Tech ID | int | **关键（UnitUpgrade）**：该升级所依赖的 tech ID。UnitUpgrade 节点不是直接用 Node ID 匹配 dat tech，而是用 Trigger Tech ID 关联。Research/UniqueTech 节点则直接用 Node ID 等于 tech ID |
| Building ID | int | 在哪生产/研发（45=码头, 87=射箭场, 12=兵营, 101=马厩, 82=城堡） |
| Link ID | int | 前置节点的 Node ID（形成升级链） |
| Age ID | int | 时代：2=封建, 3=城堡, 4=帝王 |
| Picture Index | int | 按钮图标索引 |

### Node ID 与 Trigger Tech ID 的匹配规则

| Node Type | 匹配 dat 的方式 | 示例 |
|-----------|----------------|------|
| `Research` / `UniqueTech` / `RegionalTech` | `Node ID == dat tech ID` | Cranequins Node ID=1452, tech ID=1452 |
| `UnitUpgrade` | `Trigger Tech ID == dat tech ID` | Galleon Node ID=442, Trigger Tech ID=21 (War Galley 升级), 实际升级由 tech 911 完成 |
| `Unit` / `RegionalUnit` | `Node ID == dat unit ID` | Dromon Node ID=1795, unit ID=1795 |
| `BuildingNonTech` / `BuildingTech` | `Node ID == dat unit ID`（建筑也是 unit） | Mining Camp Node ID=584, House Node ID=70 |
| `None`（精锐升级节点） | 同时用 `Trigger Tech ID == dat tech ID` + `Node ID == dat unit ID` | Elite Cannon Galleon Node ID=691, Trigger Tech ID=376 |

## Node Type 取值

| Node Type | 含义 | 分组 |
|-----------|------|------|
| Unit | 普通可训练单位（Archer, Militia） | UNIT_LIKE |
| UniqueUnit | 独特单位（Samurai, Longbowman） | SKIP（固定独特单位，不可能被 disable） |
| RegionalUnit | 区域特殊单位（Dromon, Lou Chuan, Catapult Galleon — 替代默认 Cannon Galleon） | UNIT_LIKE |
| UnitUpgrade | 单位升级（Man-at-Arms->Champion, War Galley->Galleon） | TECH |
| BuildingNonTech | 可建造建筑（House, Dock, Gate, Keep, Bombard Tower） | UNIT_LIKE |
| BuildingTech | 建筑科技节点（如 Mining Camp, Lumber Camp — 可被 tech 间接替换） | UNIT_LIKE |
| RegionalBuilding | 区域特殊建筑（未在 check 脚本中处理） | SKIP |
| UniqueBuilding | 独特建筑（Feitoria, Krepost, Donjon, Folwark, Harbor, Fortified Outpost） | SKIP（固定独特建筑） |
| UniqueTech | 独特科技（银冠/金冠） | TECH |
| RegionalTech | 区域科技（Cranequins — 替代默认 Hand Cannon） | TECH |
| Research | 可研发科技（铁匠铺/大学/修道院等） | TECH |
| **None** | **无 Node Type 但有完整 Node ID + Trigger Tech ID 的节点**（全是精锐升级） | **根据 Use Type 判断** |
| None（无 ID） | 真正的根占位节点 | SKIP |

### None 类型节点特殊说明

JSON 中所有 Node Type=`None` 且有有效 `Node ID` 和 `Trigger Tech ID` 的节点（共 51 个，全部 Use Type=`Unit`），**都是精锐升级节点**，它们的 `Trigger Tech ID` 指向 dat 中的精锐科技 ID，`Node ID` 指向升级后的精锐单位 ID。这类节点在 check 脚本中**不跳过**，按 `Use Type` 归入相应分组处理。

精锐升级识别：`Node Type=None` + `Use Type="Unit"` + 有有效 `Trigger Tech ID`。

### 节点类型功能分组（来自 check_civ_tech_trees.py）

check 脚本中定义了三个分组，决定哪些节点会参与 dat↔JSON 匹配：

| 分组 | Node Types | 说明 |
|------|-----------|------|
| **SKIP_NODE_TYPES** | `UniqueUnit`, `RegionalBuilding`, `UniqueBuilding` | 固定独特单位/建筑或区域占位，不可能被 Tech Tree disable |
| **UNIT_LIKE_TYPES** | `Unit`, `RegionalUnit`, `BuildingNonTech`, `BuildingTech` | **可被 type=2 (enable/disable unit) 直接控制**。dat Tech Tree Effect 中出现 type=2 b=0 的 unit_id，JSON 中对应 Node ID 的节点应 NotAvailable |
| **TECH_NODE_TYPES** | `Research`, `UnitUpgrade`, `UniqueTech`, `RegionalTech` | **被 type=102 (disable tech) 间接控制**。disable tech 后需要展开该 tech 的 effect 才能知道哪些 unit 被间接触发（type=2 b=0 disable / type=2 b=1 make_avail / type=3 upgrade） |

**None 类型节点动态归属**：有有效 `Trigger Tech ID` 且 `Use Type="Unit"` 的归入 TECH_NODE_TYPES（它们是精锐升级，本质是 UnitUpgrade）；无有效 ID 的真正占位节点跳过。

关键区别：type=2 只能直接 disable unit，**不能直接 disable tech**（tech 只能被 type=102 disable，且 disable tech 后需要展开其 effect 才能知道哪些 unit 被间接触发）。

## Node Status 取值

| Node Status | 含义 | 处理 |
|-------------|------|------|
| ResearchedCompleted | 初始可用 | 视为可用 |
| ResearchRequired | 可用但需前置 | **视为可用**，参与匹配 |
| NotAvailable | 无法获得（如拜占庭的 Cannon Galleon 被 Dromon 替代） | 排除 |

判断标准：通过 **Node ID** 或 **Trigger Tech ID** 定位到节点 **且** Node Status != NotAvailable。**不使用 Name 匹配**——单位/科技名称在编年史文明、区域替换、本地化字符串中都可能不唯一或不一致。

## 关键关系：Node ID = dat 文件 ID

科技树 JSON 的 Node ID 直接就是 dat 文件里的 ID，无需额外查找：

``python
node["Node ID"] == dat.civs[0].units[node["Node ID"]].ID
node["Node ID"] == dat.techs[node["Node ID"]].ID
``

可直接把 Node ID 填入 unit_switch.json 的 unit_ids 字段。

## Link ID 升级链示例

``
拜占庭码头：
  War Galley     Node ID=21    Link ID=539
  Galleon        Node ID=442   Link ID=21
  Dromon         Node ID=1795  Link ID=532   (RegionalUnit)

兵营：
  Man-at-Arms       Node ID=75    Link ID=74
  Long Swordsman    Node ID=77    Link ID=75
  Two-Handed Swordsman Node ID=473  Link ID=77
  Champion          Node ID=567   Link ID=473
``

## 常用 Building ID

| ID | 建筑 | 常量名 |
|----|------|--------|
| 12 | 兵营 | BARRACK_ID |
| 45 | 码头 | DOCK_ID |
| 49 | 攻城器工厂 | SIEGE_ID |
| 82 | 城堡 | CASTLE_ID |
| 87 | 射箭场 | ARCHERY_RANGE_ID |
| 101 | 马厩 | STABLE_ID |
| 103 | 铁匠铺 | BLACKSMITH_ID |
| 104 | 修道院 | MONESTARY_ID |
| 209 | 大学 | UNIV_ID |

## Python 解析工具函数

``python
import json, os

CIV_TECH_TREES = r"C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\CivTechTrees"

def load_civ_tree(civ_filename):
    path = os.path.join(CIV_TECH_TREES, civ_filename.upper() + ".json")
    if not os.path.exists(path):
        return None
    return json.load(open(path, "r", encoding="utf-8"))

def get_all_nodes(data):
    nodes = []
    for arr in ['civ_techs_units', 'civ_techs_buildings']:
        for node in data.get(arr, []):
            if isinstance(node, dict):
                nodes.append(node)
    return nodes

def find_by_node_id(data, node_id):
    """按 Node ID 查找节点（Unit/Building/Research 直接 Node ID=dat ID）"""
    for node in get_all_nodes(data):
        if node.get('Node ID') == node_id:
            return node
    return None

def find_by_trigger_tech_id(data, tech_id):
    """按 Trigger Tech ID 查找节点（UnitUpgrade / None 精锐升级）"""
    for node in get_all_nodes(data):
        if node.get('Trigger Tech ID') == tech_id:
            return node
    return None

def node_is_available(node):
    """判断节点在 JSON 中是否可用"""
    return node is not None and node.get('Node Status') != 'NotAvailable'

def civ_has_unit(data, unit_id):
    """通过 Unit ID 判断文明是否拥有该单位"""
    node = find_by_node_id(data, unit_id)
    return node_is_available(node)

def civ_has_upgrade(data, trigger_tech_id):
    """通过 Trigger Tech ID 判断文明是否拥有该升级"""
    node = find_by_trigger_tech_id(data, trigger_tech_id)
    return node_is_available(node)

def get_all_civ_files():
    files = [f.replace(".json", "")
             for f in os.listdir(CIV_TECH_TREES)
             if f.endswith(".json")]
    return sorted(files)
``

## 实际工作流

### 确认哪些文明拥有 Dromon（Unit ID=1795）

Dromon 在 JSON 中 Node ID=1795（RegionalUnit），替代默认的 Cannon Galleon。通过 Unit ID 查询：

``python
DROMON_ID = 1795

all_civs = get_all_civ_files()
dromon_civs = []
for civ_file in all_civs:
    data = load_civ_tree(civ_file)
    if data and civ_has_unit(data, DROMON_ID):
        dromon_civs.append(civ_file)
# ['ARMENIANS', 'BYZANTINES', 'GOTHS', 'HUNS', 'ROMANS'] -> 首字母大写填 civ_names
``

### 攻城船区分（RegionalUnit Node ID 判断）

攻城船 RegionalUnit 的 Node ID 各不相同，可直接用 ID 判断：

| 船名 | Node ID | 所属文明 |
|------|---------|---------|
| Dromon | 1795 | Byzantines, Armenians, Goths, Huns, Romans |
| Lou Chuan | 1600 | Khmer |
| Catapult Galleon | 1800 | (需查具体 ID) |

``python
SHIP_ID_MAP = {DROMON_ID: 'Dromon', LOU_CHUAN_ID: 'Lou Chuan', ...}
for ship_id, ship_name in SHIP_ID_MAP.items():
    if civ_has_unit(data, ship_id):
        break
else:
    pass  # 默认 Cannon Galleon

# 注意：Cannon Galleon (Node ID=420) 在有 RegionalUnit 的文明中 Node Status = NotAvailable，
# 不是节点不存在。RegionalUnit 替代而非覆盖。
``

## 核心机制：dat Tech Tree Effect vs JSON Node Status

### 每个文明有一个 Tech Tree Effect

dat 的 `data.effects` 数组中，每个文明都有一个 Effect，**`effect.name` 以 "Tech Tree" 结尾**（例如 `"Britons Tech Tree"`, `"Byzantines Tech Tree"`）。这个 Effect 包含了该文明对所有 tech 和 unit 的 enable/disable 操作，是判断可用性的**唯一权威来源**。

``python
tech_tree_effects = {}
for eff in data.effects:
    if eff.name.endswith('Tech Tree'):
        civ_name = eff.name[:-10]  # 去掉 " Tech Tree" 后缀
        tech_tree_effects[civ_name] = eff
``

### Tech Tree Effect 中的三种关键指令

| EffectCommand type | 说明 | 处理方式 |
|-------------------|------|---------|
| **102** | disable_tech，`cmd.d = tech_id` | 该 tech 及其 effect 里的 make_avail/disable/upgrade 全部生效为"这个文明没有" |
| **8** + `cmd.b=12` + `cmd.d=1.0` | enable_tech，`cmd.a = tech_id` | 该 tech 及其 effect 里的 disable_units 会额外生效，make_avail_units 会解除禁用 |
| **2** + `cmd.b=0` | disable_unit，`cmd.a = unit_id` | 直接将单位标记为不可用 |

### 有效的单位可用性计算

disable tech 后，不能只看 tech ID，需要**展开 tech 的 effect**：

``python
def build_tech_effect_cache(data, cache, tech_id):
    tech = data.techs[tech_id]
    teff = data.effects[tech.effect_id]
    for tcmd in teff.effect_commands:
        if tcmd.type == 2 and tcmd.b == 1:
            make_avail_units.append(tcmd.a)      # 该 tech 研发后会解锁哪些 unit
        elif tcmd.type == 2 and tcmd.b == 0:
            disable_units.append(tcmd.a)          # 该 tech 研发后会禁用哪些 unit
        elif tcmd.type == 3:
            upgrade_pairs.append((tcmd.a, tcmd.b))  # type=3 upgrade 升级链
``

然后合并所有 disabled tech 的 make_avail_units（加上 direct_disabled_units）得到最终 `eff_disabled_units`。

**特殊情况（土耳其城堡）**：Tech 137 `Castle -- Age Three`（civ=-1 全文明通用）的 effect 只有一条 `type=2 a=82 b=1`，即 enable Castle(82)。**土耳其的 Tech Tree Effect 里 disable 了 137**，但同时启用了专属的 **Tech 354 `Turk Castle`（civ=10，effect 同样是 `type=2 a=82 b=1`）** 作为替代。

在 check 脚本中 137 被列入 `SKIP_MAKEAVAIL_DISABLE_TECHS`，意思是"即使 dat 里这个文明 disable 了 137，也不要把 137 effect 里的 make_avail_units（即 Castle 82）算入 effective_disabled_units"——因为土耳其有 354 兜底，其他文明不会被 disable 137。这纯粹是为了 check 工具不误报，不代表 137 不是真实的开关科技。

### Tech 35 映射（攻城船升级特殊处理）

**Tech 35 `Galleon`（civ=-1）** 是玩家在码头**实际点击的那个升级科技按钮**（`effect_id=-1`，它自己没有 effect，但有 `research_locations` 和 `required_techs=(103, 34, ...)`）。

真正做 `type=3` 升级的是三个独立的辅助科技，它们都把 Tech 35 作为前置（`required_techs=(35, ...)`）：

| Real Tech | 玩家看到的科技名 | 升级链 | 备注 |
|-----------|----------------|--------|------|
| **911** | Galleon | War Galley(21) → Galleon(442)；Turtle Ship(539) → Galleon(442) | 地中海系 |
| **246** | Fast Fire Ship | Fire Galley(52) → Fast Fire Ship(532)；Caravel(1103) → Fast Fire Ship(532) | 火系 |
| **904** | Carrack | Caravel X(2626) → Carrack(2628)；Caravel Y(2627) → Carrack(2628) | 炮船系 |

科技树 JSON 中这些升级的 UnitUpgrade 节点，`Trigger Tech ID` 统一写的是 **35**（玩家操作层的科技），而不是各自的 real tech ID。所以：

> 如果某个文明被 disable 了 real tech 911，那么对应 JSON 中 `Trigger Tech ID=35` 且 `Node ID=442`（Galleon）的 UnitUpgrade 节点也应该是 NotAvailable。

反向也是一样：如果 JSON 中 `Trigger Tech ID=35` 的 UnitUpgrade 被标记 NotAvailable，dat 中至少应有一个对应的 real upgrade tech 被 disable。

同样的映射关系还适用于：
- **Dromon/Lou Chuan 等 RegionalUnit**：它们的升级链也有类似的"点击科技 vs 辅助升级科技"分离，JSON Trigger Tech ID 指向点击科技，dat 实际升级由辅助科技完成

## 已知异常情况（check_civ_tech_trees.py 中的 EXCEPTIONS）

有些 JSON 节点被标记为 NotAvailable，但 dat 中没有对应的直接 disable，原因是间接替换机制：

| 文明 | Node Type | Node ID | 说明 |
|------|-----------|---------|------|
| ARMENIANS | Research | 375 (Dry Dock) | 确认是 JSON bug，dat 中可用但 JSON 标 NotAvailable |
| ARMENIANS | BuildingTech | 584 (Mining Camp) | 被 tech 940 (Armenian Mt. Camels) 间接替换 |
| ARMENIANS | BuildingTech | 562 (Lumber Camp) | 被 tech 940 间接替换 |
| GEORGIANS | BuildingTech | 584 (Mining Camp) | 被 tech 932 (Georgian Mt. Camels) 间接替换 |
| GEORGIANS | BuildingTech | 562 (Lumber Camp) | 被 tech 932 间接替换 |

这些在 check 脚本中定义为 EXCEPTIONS，不应报错。

## 与 unit_switch.json 对应

| 科技树字段 | unit_switch.json 字段 | 说明 |
|------------|----------------------|------|
| Node ID | unit_ids（直接填数字） | **唯一的匹配依据**，不使用 Name |
| Node Status | 判断文明是否应归入该 switch_content | 只看 ID 对应的 JSON 节点 |
| Name | unit_name（逻辑名） | **仅标签/注释用途**，不参与任何匹配逻辑 |
| Building ID | 反查建筑类型 | 可选，通过 Building ID 反查建筑 button_id |

编年史文明（ACHAEMENIDS, ATHENIANS, MACEDONIANS, PURU, SPARTANS, THRACIANS）科技树中可能缺少某些节点，通常落到 default:true 分支处理。