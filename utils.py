import copy
import os
import zipfile
from dataclasses import fields
from typing import Any, Type, Tuple

from genieutils.civ import Civ
from genieutils.datfile import DatFile
from genieutils.effect import Effect
from genieutils.effect import EffectCommand
from genieutils.tech import ResearchResourceCost, ResearchLocation
from genieutils.tech import Tech
from genieutils.unit import ResourceCost
from genieutils.unit import ResourceStorage
from genieutils.unit import Unit


def get_civ_name(civs: list[Civ], idx):
    match idx:
        case 1:
            return 'Britons'
        case 2:
            return 'Franks'
        case 7:
            return 'Byzantines'
        case 16:
            return 'Mayans'
        case 25:
            return 'Ethiopians'
        case _:
            return civs[idx].name


def get_default_value(field_type: Any) -> Any:
    if field_type is int:
        return 0
    elif field_type is float:
        return 0.0
    elif field_type is str:
        return ''
    else:
        return None


def create_new(cls: Type, **kwargs: Any) -> Any:
    instance = cls(**{field.name: kwargs.get(field.name, get_default_value(field.type)) for field in fields(cls)})
    return instance


def get_new_tech(name='', need_location=False):
    return Tech(required_techs=(-1, -1, -1, -1, -1, -1),
                resource_costs=(
                    ResearchResourceCost(-1, 0, 0), ResearchResourceCost(-1, 0, 0), ResearchResourceCost(-1, 0, 0),),
                required_tech_count=0,
                civ=-1,
                full_tech_mode=0,
                research_locations= list() if need_location else [ResearchLocation(-1, 0, 0, -1)],
                language_dll_name=7000,
                language_dll_description=8000,
                effect_id=-1,
                type=0,
                icon_id=-1,
                language_dll_help=107000,
                language_dll_tech_tree=150000,
                name=name,
                repeatable=0)


def get_new_effect(name=''):
    effect = Effect(effect_commands=list(), name=name)
    return effect


def get_new_unit(units: list[Unit]):
    return copy.deepcopy(units[946])


def get_dead_unit(units: list[Unit]):
    treb = copy.deepcopy(units[331])
    treb.hit_points = -1
    treb.language_dll_name = 0
    treb.language_dll_creation = 6000
    treb.hot_key = 16000
    treb.language_dll_help = 105000
    treb.language_dll_hotkey_text = 155000
    treb.line_of_sight = 0
    treb.standing_graphic = (-1, -1)
    treb.dying_graphic = -1
    treb.interface_kind = 0
    treb.resource_storages = (ResourceStorage(-1, 0.0, 0), ResourceStorage(-1, 0.0, 0), ResourceStorage(-1, 0.0, 0))
    treb.creatable.resource_costs = (ResourceCost(-1, 0, 0), ResourceCost(-1, 0, 0), ResourceCost(-1, 0, 0))
    treb.building.transform_unit = -1
    treb.icon_id = -1
    treb.building.construction_graphic_id = -1
    treb.building.destruction_graphic_id = -1
    treb.speed = 0
    treb.resource_capacity = 0
    treb.resource_decay = 0
    treb.bird.work_rate = 0
    treb.enabled = 1
    treb.interation_mode = 0
    treb.minimap_mode = 0
    treb.dead_unit_id = -1
    treb.creatable.train_locations.pop()
    return treb


def append_tech_effect(data: DatFile, tech: Tech, effect: Effect):
    tech_id = len(data.techs)
    effect_id = len(data.effects)
    tech.effect_id = effect_id
    data.techs.append(tech)
    data.effects.append(effect)
    return tech_id, effect_id


def append_tech(data: DatFile, tech: Tech, effect: Effect = None):
    if effect is None:
        tech_id = len(data.techs)
        data.techs.append(tech)
        return tech_id
    else:
        return append_tech_effect(data, tech, effect)

def append_unit(data: DatFile, unit: Unit):
    unit_id = len(data.civs[0].units)
    for civ in data.civs:
        civ.units.append(unit)
    return unit_id


def replace_tuple(t: tuple, origin, replace):
    for i in range(len(t)):
        if t[i] == origin:
            return t[:i] + (replace,) + t[i + 1:]
    return t


def enable_tech(effect: Effect, tech_id):
    effect.effect_commands.append(EffectCommand(8, tech_id, 12, -1, 1))


def force_tech(effect: Effect, tech_id):
    effect.effect_commands.append(EffectCommand(8, tech_id, 12, -1, 2))


def disable_tech(effect: Effect, tech_id):
    effect.effect_commands.append(EffectCommand(102, -1, -1, -1, tech_id))


def research_tech(effect: Effect, tech_id):
    effect.effect_commands.append(EffectCommand(8, tech_id, 12, -1, 3))

def force_research_tech(effect: Effect, tech_id):
    effect.effect_commands.append(EffectCommand(8, tech_id, 12, -1, 2))
    effect.effect_commands.append(EffectCommand(8, tech_id, 12, -1, 3))


def enable_unit(effect: Effect, unit_id):
    effect.effect_commands.append(EffectCommand(2, unit_id, 1, -1, 0))


def disable_unit(effect: Effect, unit_id):
    effect.effect_commands.append(EffectCommand(2, unit_id, 0, -1, 0))


def set_unit_attribute(effect: Effect, unit_id, class_id, attribute, value, selected=0):
    if selected == 0:
        effect.effect_commands.append(EffectCommand(0, unit_id, class_id, attribute, value))
    else:
        effect.effect_commands.append(EffectCommand(203, unit_id, class_id, attribute, value))


def plus_unit_attribute(effect: Effect, unit_id, class_id, attribute, value, selected=0):
    if selected == 0:
        effect.effect_commands.append(EffectCommand(4, unit_id, class_id, attribute, value))
    else:
        effect.effect_commands.append(EffectCommand(204, unit_id, class_id, attribute, value))


def multiply_unit_attribute(effect: Effect, unit_id, class_id, attribute, value, selected=0):
    if selected == 0:
        effect.effect_commands.append(EffectCommand(5, unit_id, class_id, attribute, value))
    else:
        effect.effect_commands.append(EffectCommand(205, unit_id, class_id, attribute, value))


def multiply_unit_cost(effect: Effect, unit_id, class_id, value):
    effect.effect_commands.append(EffectCommand(5, unit_id, class_id, 100, value))


def multiply_unit_hp(effect: Effect, unit_id, class_id, value):
    effect.effect_commands.append(EffectCommand(5, unit_id, class_id, 0, value))


def multiply_unit_attack(effect: Effect, unit_id, class_id, percentage, type):
    effect.effect_commands.append(EffectCommand(5, unit_id, class_id, 9, percentage + 256 * type))

def plus_unit_attack(effect: Effect, unit_id, class_id, value, type):
    effect.effect_commands.append(EffectCommand(4, unit_id, class_id, 9, value + 256 * type))


def plus_unit_armor(effect: Effect, unit_id, class_id, amount, type):
    effect.effect_commands.append(EffectCommand(4, unit_id, class_id, 8, amount + 256 * type))


def plus_resource(effect: Effect, resource_id, value):
    effect.effect_commands.append(EffectCommand(1, resource_id, 1, -1, value))


def set_resource(effect: Effect, resource_id, value):
    effect.effect_commands.append(EffectCommand(1, resource_id, 0, -1, value))


def multiply_resource(effect: Effect, resource_id, value):
    effect.effect_commands.append(EffectCommand(6, resource_id, -1, -1, value))


def set_tech_cost(effect: Effect, tech_id, resource_id, value):
    effect.effect_commands.append(EffectCommand(101, tech_id, resource_id, 0, value))


def set_tech_time(effect: Effect, tech_id, value):
    effect.effect_commands.append(EffectCommand(103, tech_id, -1, 0, value))

def set_tech_time_discount(effect: Effect, tech_id, value):
    effect.effect_commands.append(EffectCommand(103, tech_id, -1, 2, value))

def set_tech_discount(effect: Effect, tech_id, resource_id, value):
    effect.effect_commands.append(EffectCommand(101, tech_id, resource_id, 2, value))

def upgrade_unit(effect: Effect, unit_id, new_unit_id, mode=-1):
    effect.effect_commands.append(EffectCommand(3, unit_id, new_unit_id, mode, 0))

def spawn_a_llama(effect: Effect):
    set_resource(effect, 234, 1)
    effect.effect_commands.append(EffectCommand(7, 305, 619, 1, 0))

def get_tech_id_by_name(data: DatFile, name: str):
    for i, tech in enumerate(data.techs):
        if tech.name == name:
            return i
    return -1

def extend_effect(effect: Effect, unit_ids = [], class_ids=[]):
    command_set = set(map(lambda command: (command.type, command.c, command.d), effect.effect_commands))
    for command in command_set:
        for unit_id in unit_ids:
            effect.effect_commands.append(EffectCommand(command[0], unit_id, -1, command[1], command[2]))
        for class_id in class_ids:
            effect.effect_commands.append(EffectCommand(command[0], -1, class_id, command[1], command[2]))


def set_require_techs(tech: Tech, *args):
    tech.required_techs = args + (-1,) * (6 - len(args))
    tech.required_tech_count = len(args)


def get_mod_path(mod_name: str = 'All Civ Bonus Test') -> str:
    """查找游戏的mod路径"""
    user_path = r'C:\Users'
    for user in os.listdir(user_path):
        if user in ('.', 'Public'):
            continue
        game_path = os.path.join(user_path, user, 'Games', 'Age of Empires 2 DE')
        if os.path.isdir(game_path):
            break
    for steam_account in os.listdir(game_path):
        if steam_account == '0' or not steam_account.isnumeric():
            continue
        mod_path = os.path.join(game_path, steam_account, 'mods', 'local', mod_name)
        if os.path.isdir(mod_path):
            break
    return mod_path


def create_mod_zip(mod_path: str, zip_filename: str = 'allin1.zip') -> str:
    """创建mod的zip文件"""
    ofilename = os.path.join(mod_path, zip_filename)
    with zipfile.ZipFile(ofilename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(mod_path, 'thumbnail.jpg'), os.path.basename('thumbnail.jpg'))
        resource_path = 'resources'
        for root, dirs, files in os.walk(os.path.join(mod_path, resource_path)):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), mod_path))
    return ofilename


if __name__ == '__main__':
    tech = create_new(Tech)
    set_require_techs(tech, 1, 2, 4)
    print(tech)