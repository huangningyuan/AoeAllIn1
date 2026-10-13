# 数据真实性约束（防幻觉规则）

## 核心原则

> **dat 文件和 strings 文件是唯一真相，训练记忆一律不可信。**
> AoE2DE 经历 10+ 个 DLC 重平衡，编年史 DLC 对大量科技/文明归属做了重分配，训练时沉淀的"盘蛇阵=玛雅"、"盾墙=希腊"等历史印象**已经失效**。任何涉及具体数据的输出必须有工具调用证据。

> **字段用法永远先看文档再看数据。**
> `dat_reference.md` 是 EffectCommand、Unit、Tech 等所有 dat 结构字段含义的权威手册。解读 `EffectCommand(a, b, c, d)` 的语义（例如 type 101 的 c=0 是设成本、c=2 是折扣）、判断某个 dat 字段的合法取值范围，**必须先查 dat_reference.md**，再用实际数据验证。禁止凭字段名猜含义（例如看到 `c` 以为是 count、看到 `d` 以为是 damage）。

## 强制查询清单（回答以下内容前，必须有对应查询）

| 想输出的内容 | 必须查询的来源 | 不可信来源 |
|---|---|---|
| 科技中文名 | `resources/zh/strings/key-value/key-value-strings-utf8.txt` + `key-value-modded-strings-utf8.txt` | 训练记忆、英文名直觉、en strings |
| 单位中文名 | 同上 | 训练记忆 |
| 文明归属（某 tech/unit 属于哪个 civ） | `data.techs[tid].civ` 字段 + `civ_tech_trees.md` ID 对照表 | 训练记忆、科技主题推断 |
| tech / effect / unit 的字段值 | 本次 `DatFile.parse(...)` 加载结果 | 训练记忆、上次运行缓存 |
| XS 函数体/常量值 | `_parse_xs()` 或直接查 `Effects.xs` / `Constants.xs` | 训练记忆、ugc wiki 过时缓存 |

## 标准查询模板（照抄）

### 查中文名

```python
import os, re
zh_strings = {}
for p in [
    r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\zh\strings\key-value\key-value-strings-utf8.txt',
    r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\zh\strings\key-value\key-value-modded-strings-utf8.txt',
]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.match(r'(\d+)\s+"(.+)"', line.strip())
                if m:
                    zh_strings[int(m.group(1))] = m.group(2)

lid = getattr(data.techs[tid], 'language_dll_name', 0)
print(zh_strings.get(lid, '<NO ZH>'))
```

### 查文明归属

```python
CIV_NAMES_ZH = {
    1: '不列颠', 2: '法兰克', 3: '哥特', 4: '条顿', 5: '日本', 6: '中国',
    7: '拜占庭', 8: '波斯', 9: '撒拉逊', 10: '土耳其', 11: '维京', 12: '蒙古',
    13: '凯尔特', 14: '西班牙', 15: '阿兹特克', 16: '玛雅', 17: '匈奴', 18: '高丽',
    19: '意大利', 20: '印度斯坦', 21: '印加', 22: '马扎尔', 23: '斯拉夫', 24: '葡萄牙',
    25: '埃塞俄比亚', 26: '马里', 27: '柏柏尔', 28: '高棉', 29: '马来', 30: '缅甸',
    31: '越南', 32: '保加利亚', 33: '鞑靼', 34: '库曼', 35: '立陶宛', 36: '勃艮第',
    37: '西西里', 38: '波兰', 39: '波西米亚', 40: '达罗毗荼', 41: '孟加拉', 42: '瞿折罗',
    43: '罗马', 44: '亚美尼亚', 45: '格鲁吉亚',
    46: '阿契美尼德', 47: '雅典', 48: '斯巴达', 49: '蜀', 50: '吴', 51: '魏',
    52: '女真', 53: '契丹', 54: '马其顿', 55: '色雷斯', 56: '普鲁',
    57: '穆伊斯卡', 58: '马普切', 59: '图皮', 60: '撒克逊', 61: '瓦良格', 62: '丹麦',
}
civ_id = data.techs[tid].civ
print(CIV_NAMES_ZH.get(civ_id, '<civ ' + str(civ_id) + '>'))
```

## 自检清单（回答涉及具体数据的内容前）

- [ ] 我输出的每个中文名/文明归属/数值，是否都有**本次对话内**的工具调用结果支撑？
- [ ] 有没有偷偷用了"这个科技应该属于 X 文明"之类的训练记忆但没验证？
- [ ] 对拿不准的数据，是否先说"需要查一下"再回答，还是硬编了一个看起来合理的答案？

## 反模式（禁止）

1. 看到英文名直接联想"应该就是 X 文明的" —— DLC 重分配会打脸
2. 用 en strings 代替 zh strings 输出中文 —— 有 zh 文件就必须用
3. 回答里提到具体 tech/unit 的属性值、归属、中文名，但本次对话没有 `RunCommand` 验证过
4. 说"根据我的记忆"或"通常来说"——一律改成"查一下 dat"