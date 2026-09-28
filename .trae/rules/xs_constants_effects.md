# AoE2DE XS Scripting (Constants.xs & Effects.xs) 参考

## 文件位置

``
C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\xs\
├── Constants.xs      ← 所有常量定义（自动包含）
├── Effects.xs        ← EffectFunction 实现（自动包含）
├── ailib\            ← AI 脚本库
├── x256tech.xs
└── x9tech.xs
``

这两个文件是游戏引擎**自动包含**的，不需要 mod 主动 #include。

---

## 核心机制：dat → XS 的桥梁

### 问题背景

dat 文件里有一种特殊的效果指令：

``
EffectCommand(1, 33, b, -1, X)   # type=1, a=33, d=X
``

这在 utils.py 里对应：

``python
plus_resource(effect, 33, X)  # type=1, a=33, b=1, d=X
# 或
set_resource(effect, 33, X)   # type=1, a=33, b=0, d=X
``

**resource 33 是什么？** 由 Constants.xs 定义：

``c
extern const int cAttributeEffectFunctionNumber = 33;
``

### 机制说明

1. 科技的 Effect 中包含一条 type=1 (ModResource) + a=33 (EffectFunctionNumber) 的指令
2. 引擎读取到 value = X
3. 游戏在运行时自动调用 Effects.xs 里的 **EffectFunctionX(int playerId)** 函数

### 映射关系

| dat 指令 | Constants.xs 常量 | 触发 |
|---------|-------------------|------|
| type=1, a=33, d=X | cModResource, cAttributeEffectFunctionNumber=33 | 引擎调用 Effects.xs 中的 EffectFunctionX(playerId) |
| dat 数值 33 | cAttributeEffectFunctionNumber | 同一个东西，名字在 Constants.xs 里 |

**举例**：某科技效果里有 plus_resource(33, 5)，引擎就会调用：

``c
// Effects.xs line 334
void EffectFunction5(int playerId = -1)
{
    // 5 - Effect of Chieftains for Vikings
    xsTask(...);  // 维京酋长科技效果
}
``

---

## Constants.xs 关键常量

### xsEffectAmount 第一个参数：效果类型（= dat EffectCommand.type）

| Constants.xs | 值 | dat type | 说明 |
|---|---|---|---|
| cSetAttribute | 0 | type=0 | 设置玩家全局属性（如人口上限、起始资源） |
| cModResource | 1 | type=1 | 玩家资源操作（set/plus 资源、设置 EffectFunctionNumber=33） |
| cEnableObject | 2 | type=2 | 启用/禁用单位（enable_unit / disable_unit） |
| cUpgradeUnit | 3 | type=3 | 单位升级（upgrade_unit） |
| cAddAttribute | 4 | type=4 | 玩家全局属性加法 |
| cMulAttribute | 5 | type=5 | 玩家全局属性乘法 |
| cMulResource | 6 | type=6 | 玩家资源乘法 |
| cSpawnUnit | 7 | type=7 | 生成单位（如印加生成羊驼） |
| cModifyTech | 8 | type=8 | 修改科技状态（disable/force/research） |
| cSetPlayerData | 9 | type=9 | 设置玩家数据 |
| cSetUnitAttribute | 10 | type=10 | 设置单位属性（by class） |
| cAddUnitAttribute | 11 | type=11 | 加单位属性（by class） |
| cMulUnitAttribute | 12 | type=12 | 乘单位属性（by class） |
| cSetTechCost | 100 | type=101 | 设置科技成本 |
| cAddTechCost | 101 | type=101 | 加科技成本 |
| cDisableTech | 102 | type=102 | 禁用科技 |
| cModTechTime | 103 | type=103 | 设置科技时间 |

### 注：gaia 版本加 -100：如 cGaiaSetAttribute = -1，cGaiaModResource = -2 等

### xsEffectAmount 第二个参数：单位属性（= dat unit attribute）

| Constants.xs | 值 | 说明 |
|---|---|---|
| cHitpoints | 0 | HP |
| cLineOfSight | 1 | 视野 |
| cGarrisonCapacity | 2 | 驻扎容量 |
| cMovementSpeed | 5 | 移速 |
| cArmor | 8 | 护甲 |
| cAttack | 9 | 攻击力 |
| cAttackReloadTime | 10 | 攻击间隔 |
| cAccuracyPercent | 11 | 精度 |
| cMaxRange | 12 | 射程 |
| cWorkRate | 13 | 工作效率 |
| cCarryCapacity | 14 | 运载量 |
| cProjectileUnit | 16 | 投射物 |
| cMinimumRange | 20 | 最小射程 |
| cTrainLocation | 42 | 训练建筑 |
| cTrainButton | 43 | 训练按钮位 |

### cAttributeEffectFunctionNumber = 33（最关键）

这个值**就是** dat 里 set resource 33 对应的东西。设为 X 就会调用 EffectFunctionX()。

### 玩家资源属性（cSetAttribute / cModResource 用）

| Constants.xs | 值 | 说明 |
|---|---|---|
| cAttributeFood | 0 | 食物存量 |
| cAttributeWood | 1 | 木材存量 |
| cAttributeStone | 2 | 石料存量 |
| cAttributeGold | 3 | 金币存量 |
| cAttributePopulationCap | 4 | 人口上限 |
| cAttributeRelics | 7 | 圣物数 |
| cAttributeEffectFunctionNumber | 33 | **EffectFunction 选择器** |
| cAttributeFarmFood | 36 | 农田食物存量 |

---

## Object Class 常量（= civ_switch 的 unit class_id）

| Constants.xs | 值 | dat class_id | 说明 |
|---|---|---|---|
| cInfantryClass | 906 | 1 | 步兵 |
| cCavalryClass | 912 | 2 | 骑兵 |
| cSiegeWeaponClass | 913 | 7 | 攻城器 |
| cMonkClass | 918 | 9 | 僧侣 |
| cArcherClass | 900 | 0 | 远程/弓箭手 |
| cBuildingClass | 903 | 5 | 建筑 |
| cWarshipClass | 922 | — | 战舰 |
| cCavalryArcherClass | 936 | — | 骑射手 |
| cHandCannoneerClass | 944 | — | 火枪手 |
| cElephantArcherClass | 926 | — | 战象射手 |
| cConquistadorClass | 923 | — | 征服者 |
| cScoutCavalryClass | 947 | — | 侦察骑兵 |
| cTwoHandedSwordsmanClass | 945 | — | 双手剑士 |
| cPikemanClass | 946 | — | 长枪兵 |
| cSpearmanClass | 950 | — | 矛兵 |
| cPetardClass | 935 | — | 炸药桶 |
| cRaiderClass | 956 | — | 劫掠者 |
| cFarmClass | 949 | — | 农田 |
| cTreeClass | 915 | — | 树木 |
| cWallClass | 927 | — | 城墙 |
| cGateClass | 939 | — | 城门 |
| cTowerClass | 952 | — | 塔楼 |

---

## xsEffectAmount 调用签名

``c
xsEffectAmount(effectType, objectOrClass, attribute, amount, playerId);
``

示例（来自 Effects.xs）：

``c
// 生成单位：EffectFunction1 印加羊驼
xsEffectAmount(cSpawnUnit, targetLlama, 619, 1, playerId);

// 单位属性乘法：HandicapSetup 困难加成
xsEffectAmount(cMulAttribute, cBuildingClass, cHitpoints, handicapMultiplier, playerId);

// 玩家资源乘法：HandicapSetup
xsEffectAmount(cMulResource, cAttributeGoldBonus, -1, handicapMultiplier, playerId);
``

---

## 与项目 dat 操作的对应

| 项目操作 | dat 效果 | Constants.xs 等价 | Effects.xs 用法 |
|---------|----------|-------------------|-----------------|
| plus_resource(effect, 33, X) | type=1, a=33, d=X | xsEffectAmount(cModResource, cAttributeEffectFunctionNumber, -1, X, playerId) | 触发 EffectFunctionX() |
| plus_resource(effect, 0, 500) | type=1, a=0, d=500 | xsEffectAmount(cModResource, cAttributeFood, -1, 500, playerId) | 直接给食物 |
| set_unit_attribute(effect, unit_id, -1, 8, 5) | type=0, c=8, d=5 | xsEffectAmount(cSetUnitAttribute, unit_id, cArmor, 5, playerId) | — |
| plus_unit_armor(effect, unit_id, -1, 1, ...) | type=4, c=8 | xsEffectAmount(cAddUnitAttribute, unit_id, cArmor, value, playerId) | — |
| multiply_unit_attribute(effect, unit_id, -1, 0, 1.2) | type=5, c=0, d=1.2 | xsEffectAmount(cMulUnitAttribute, unit_id, cHitpoints, 1.2, playerId) | — |

---

## 文明 ID 常量

``c
extern const int cBritons = 1;
extern const int cFranks = 2;
extern const int cTeutons = 3;
// ... (编年史: 46-56)
extern const int cNumCivs = 62;
``

这些 ID 与 dat 文件的 civ 数组索引**一致**（dat 里 civs[1] = Britons, civs[46] = Achaemenids）。

---

## xsTask 系列（EffectFunction 内部实现大量使用）

``c
// 让某类单位执行某任务（如采集、生成资源）
xsTask(unitClassOrID, taskType, targetObjectClass, playerId);

// 设置任务参数（如资源产出类型和数量）
xsTaskAmount(taskAttr, attribute);
``

常用 taskAttr：
| 常量 | 值 | 说明 |
|---|---|---|
| cTaskAttrProductivityResource | 9 | 产出的资源类型（= cAttributeGold 等） |
| cTaskAttrResourceOut | 10 | 资源产出数量 |
| cTaskAttrWorkRate | 13 | 工作效率 |

---

## 实际工作流示例

### 想用 Effects.xs 机制实现自定义效果

1. 在 Effects.xs 里写 oid EffectFunction99(int playerId = -1) { ... }
2. 在 tech 的 effect 里加：
   ``python
   plus_resource(effect, 33, 99)   # 或 set_resource
   `
3. 科技研发后引擎自动调用 EffectFunction99(playerId)

### 想知道 dat 里某个科技用了哪个 EffectFunction

1. 打开 dat 文件 → techs[X].effect_id → effects[Y].effect_commands
2. 找有没有 type=1 且 a=33 的指令
3. d 的值就是 EffectFunction 编号
4. 打开 Effects.xs 搜索 EffectFunction<编号> 查看实现