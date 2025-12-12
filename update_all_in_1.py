import os
import zipfile

import constants
from add_switch import adding_switch
from civ_bonuses import add_civ_bonuses
from civ_switch import add_civ_switch
from constants import gunpowder_units, siege_units, siege_workshop_units, elephant_units
from ftt import deal_ftt
from genieutils.datfile import DatFile
from unique_techs import add_unique_techs


def update_all_in_1(debug = True):
    origin_file_name = r'C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\dat\empires2_x2_p1.dat'
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
        mod_path = os.path.join(game_path, steam_account, 'mods', 'local', 'All Civ Bonus Test')
        if os.path.isdir(mod_path):
            break
    print(mod_path)
    target_file_name = os.path.join(mod_path, 'resources', '_common', 'dat', 'empires2_x2_p1.dat')
    print('Loading data...')
    data = DatFile.parse(origin_file_name)
    print('Data loaded.')
    params = adding_switch(data)
    constants.TECH_NUM = len(data.techs)
    effects = data.effects
    for command in effects[410].effect_commands:
        gunpowder_units.append(command.a)
    units = data.civs[0].units
    for i, unit in enumerate(units):
        if unit and unit.creatable and len(unit.creatable.train_locations) > 0:
            if constants.SIEGE_NUM in list(map(lambda x: x.unit_id ,unit.creatable.train_locations)):
                siege_workshop_units.append(i)
            if 20 in list(map(lambda armor: armor.class_, unit.type_50.armours)):
                siege_units.append(i)
            if 5 in list(map(lambda armor: armor.class_, unit.type_50.armours)):
                elephant_units.append(i)
    for i, tech in enumerate(data.techs):
        if len(tech.research_locations) > 0:
            if tech.research_locations[0].location_id == 209:
                constants.university_techs[tech.name] = i
    print(f'Gunpowder units: {gunpowder_units}')
    print(f'Siege units: {siege_units}')
    print(f'Siege workshop units: {siege_workshop_units}')
    print(f'Elephant units: {elephant_units}')
    print(f'University techs: {constants.university_techs}')
    deal_ftt(data, params)
    add_civ_bonuses(data, params)
    add_unique_techs(data, params)
    add_civ_switch(data, params)
    print('Saving Data...')
    data.save(target_file_name)
    print('Data saved.')
    ofilename = r'allin1.zip'
    with zipfile.ZipFile(os.path.join(mod_path, ofilename), 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(mod_path, 'thumbnail.jpg'), os.path.basename('thumbnail.jpg'))
        resource_path = 'resources'
        for root, dirs, files in os.walk(os.path.join(mod_path, resource_path)):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), mod_path))
    print('Zip file created.')
    os.startfile(mod_path)
    print('All in 1 finished.')

if __name__ == '__main__':
    update_all_in_1(False)