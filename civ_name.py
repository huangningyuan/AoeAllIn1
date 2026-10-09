# -*- coding: utf-8 -*-
"""
统一管理 AoE2DE 文明名称的各种变体。

dat civ.name（单数/原始拼写）、Tech Tree effect 名（标准英文）、
JSON 科技树文件名（全大写，少数特殊）、中文译名，全部映射到一个统一英文名。
"""

CIV_EN_ZH = {
    'Britons': '不列颠', 'Franks': '法兰克', 'Goths': '哥特', 'Teutons': '条顿',
    'Japanese': '日本', 'Chinese': '中国', 'Byzantines': '拜占庭', 'Persians': '波斯',
    'Saracens': '萨拉森', 'Turks': '土耳其', 'Vikings': '维京', 'Mongols': '蒙古',
    'Celts': '凯尔特', 'Spanish': '西班牙', 'Aztecs': '阿兹特克', 'Mayans': '玛雅',
    'Huns': '匈奴', 'Koreans': '高丽', 'Italians': '意大利', 'Hindustanis': '印度斯坦',
    'Incas': '印加', 'Magyars': '马扎尔', 'Slavs': '斯拉夫', 'Portuguese': '葡萄牙',
    'Ethiopians': '埃塞俄比亚', 'Malians': '马里', 'Berbers': '柏柏尔', 'Khmer': '高棉',
    'Malay': '马来', 'Burmese': '缅甸', 'Vietnamese': '越南', 'Bulgarians': '保加利亚',
    'Tatars': '鞑靼', 'Cumans': '库曼', 'Lithuanians': '立陶宛', 'Burgundians': '勃艮第',
    'Sicilians': '西西里', 'Poles': '波兰', 'Bohemians': '波西米亚', 'Dravidians': '达罗毗荼',
    'Bengalis': '孟加拉', 'Gurjaras': '瞿折罗', 'Romans': '罗马', 'Armenians': '亚美尼亚',
    'Georgians': '格鲁吉亚', 'Achaemenids': '阿契美尼德', 'Athenians': '雅典',
    'Spartans': '斯巴达', 'Wei': '魏', 'Shu': '蜀', 'Wu': '吴', 'Jurchens': '女真',
    'Khitans': '契丹', 'Puru': '普鲁', 'Thracians': '色雷斯', 'Macedonians': '马其顿',
    'Muisca': '穆伊斯卡', 'Mapuche': '马普切', 'Tupi': '图皮',
    'Saxons': '撒克逊', 'Danes': '丹麦', 'Varangians': '瓦兰吉',
}

DAT_NAME_TO_STANDARD = {
    'British': 'Britons',
    'French': 'Franks',
    'Byzantine': 'Byzantines',
    'Mayan': 'Mayans',
}

JSON_FILE_TO_STANDARD = {
    'INDIANS': 'Hindustanis',
    'MAGYAR': 'Magyars',
}

CHRONICLE_CIVS = {
    'Achaemenids', 'Athenians', 'Spartans', 'Macedonians', 'Thracians', 'Puru',
}


def from_dat_name(dat_name):
    if dat_name in DAT_NAME_TO_STANDARD:
        return DAT_NAME_TO_STANDARD[dat_name]
    return dat_name


def from_json_file(json_filename):
    name = json_filename.upper()
    if name in JSON_FILE_TO_STANDARD:
        return JSON_FILE_TO_STANDARD[name]
    return name.capitalize()


def to_zh(standard_name):
    return CIV_EN_ZH.get(standard_name, standard_name)


def is_chronicle(standard_name):
    return standard_name in CHRONICLE_CIVS
