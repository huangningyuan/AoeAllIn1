import os
import json
from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost
from utils import disable_tech, set_resource
import constants

# Load linkedTechs.json at module level
linked_techs_path = os.path.join(constants.GAME_DATA_PATH, 'linkedTechs.json')
with open(linked_techs_path, 'r', encoding='utf-8') as f:
    LINKED_TECHS = json.load(f)

# Get the maximum NameId from existing linked techs
max_name_id = 0
if LINKED_TECHS.get('LinkedTechs'):
    for tech in LINKED_TECHS['LinkedTechs']:
        if tech.get('NameId', 0) > max_name_id:
            max_name_id = tech['NameId']

# Current NameId counter
current_name_id = max_name_id


class Mutex():

    @classmethod
    def get_mutex_id(cls):
        match Mutex.__mutex_id:
            case 399:
                Mutex.__mutex_id = 409
            case 424:
                Mutex.__mutex_id = 434
            case _:
                Mutex.__mutex_id += 1
        return Mutex.__mutex_id


def add_mutex(data: DatFile, tech_ids: list[int], effect_ids: list[int]):
    global current_name_id
    
    # Generate new NameId
    current_name_id += 1
    
    # Create Comment from tech names
    tech_names = set()
    for i in tech_ids:
        tech = data.techs[i]
        tech_names.add(tech.name)
    comment = '/'.join(tech_names)
    
    # Create new LinkedTech entry
    new_linked_tech = {
        "NameId": current_name_id,
        "Comment": comment,
        "Type": "MutuallyExclusive",
        "Techs": tech_ids
    }
    
    # Add to LINKED_TECHS
    if 'LinkedTechs' not in LINKED_TECHS:
        LINKED_TECHS['LinkedTechs'] = []
    LINKED_TECHS['LinkedTechs'].append(new_linked_tech)
    
    # Update techs with mutex resource
    for i in tech_ids:
        for effect_id in effect_ids:
            disable_tech(data.effects[effect_id], i)