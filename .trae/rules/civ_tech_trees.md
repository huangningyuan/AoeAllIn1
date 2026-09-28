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
| civ_id | int | 文明索引（1=Britons, 编年史在 46-56 区间） |
| civ_techs_units | list | **核心**：单位、升级、科技、独特单位、独特科技全在这里（按 Node Type 区分） |
| civ_techs_buildings | list | 建筑节点 |

## 节点通用字段

| 字段 | 类型 | 说明 |
|------|------|------|
| Name | str | 游戏内英文显示名（如 "Dromon", "Cannon Galleon"） |
| Node Type | str | 节点类别（见下表） |
| Node Status | str | 可用性（见下表） |
| Node ID | int | **关键！** 单位/科技/建筑在 dat 文件中的 ID，直接等于 dat.civs[0].units[id].ID |
| Building ID | int | 在哪生产/研发（45=码头, 87=射箭场, 12=兵营, 101=马厩, 82=城堡） |
| Link ID | int | 前置节点的 Node ID（形成升级链） |
| Age ID | int | 时代：2=封建, 3=城堡, 4=帝王 |
| Picture Index | int | 按钮图标索引 |

## Node Type 取值

| Node Type | 含义 |
|-----------|------|
| Unit | 普通可训练单位（Archer, Militia） |
| UniqueUnit | 独特单位（Samurai, Longbowman） |
| RegionalUnit | 区域特殊单位（Dromon, Lou Chuan, Catapult Galleon — 替代默认 Cannon Galleon） |
| UnitUpgrade | 单位升级（Man-at-Arms->Champion, War Galley->Galleon） |
| BuildingNonTech | 可建造建筑（Dock, Castle） |
| BuildingTech | 建筑节点 |
| UniqueTech | 独特科技 |
| Research | 可研发科技 |
| None | 无类型（根节点或占位） |

精锐升级识别：Name 以 "Elite " 开头 + Node Type = UnitUpgrade。

## Node Status 取值

| Node Status | 含义 | 处理 |
|-------------|------|------|
| ResearchedCompleted | 初始可用 | 视为可用 |
| ResearchRequired | 可用但需前置 | **视为可用**，参与匹配 |
| NotAvailable | 无法获得（如拜占庭的 Cannon Galleon 被 Dromon 替代） | 排除 |

判断标准：能按 Name 匹配到节点 **且** Node Status != NotAvailable。

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

def find_node(nodes, name_filter=None, node_type=None):
    results = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if name_filter and name_filter not in node.get("Name", ""):
            continue
        if node_type and node.get("Node Type") != node_type:
            continue
        results.append(node)
    return results

def civ_has_unit(data, unit_name):
    for node in data.get("civ_techs_units", []):
        if not isinstance(node, dict):
            continue
        if node.get("Name") != unit_name:
            continue
        if node.get("Node Status") == "NotAvailable":
            return False
        return True
    return False

def get_all_civ_files():
    files = [f.replace(".json", "")
             for f in os.listdir(CIV_TECH_TREES)
             if f.endswith(".json")]
    return sorted(files)
``

## 实际工作流

### 确认哪些文明拥有 Dromon

``python
all_civs = get_all_civ_files()
dromon_civs = []
for civ_file in all_civs:
    data = load_civ_tree(civ_file)
    if data and civ_has_unit(data, "Dromon"):
        dromon_civs.append(civ_file)
# ['ARMENIANS', 'BYZANTINES', 'GOTHS', 'HUNS', 'ROMANS'] -> 首字母大写填 civ_names
``

### 攻城船区分

``python
for ship_name in ["Dromon", "Lou Chuan", "Catapult Galleon"]:
    if civ_has_unit(data, ship_name):
        break
else:
    pass  # 默认 Cannon Galleon
``

注意：Cannon Galleon 在有 Dromon/Lou Chuan/Catapult Galleon 的文明中 Node Status = NotAvailable，不是节点不存在。

## 与 unit_switch.json 对应

| 科技树字段 | unit_switch.json 字段 |
|------------|----------------------|
| Node ID | unit_ids（直接填数字） |
| Node Status | 判断文明是否应归入该 switch_content |
| Name | unit_name（逻辑名） |
| Building ID | 反查建筑类型 |

编年史文明（ACHAEMENIDS, ATHENIANS, MACEDONIANS, PURU, SPARTANS, THRACIANS）科技树中可能缺少某些节点，通常落到 default:true 分支处理。
