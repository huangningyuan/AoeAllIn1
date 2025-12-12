from genieutils.datfile import DatFile
from genieutils.tech import ResearchResourceCost
from utils import disable_tech, set_resource

MUTEX_START = 384


class Mutex():
    __mutex_id = MUTEX_START
    _mutex_start = MUTEX_START

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
    mutex_id = Mutex().get_mutex_id()
    for i in tech_ids:
        tech = data.techs[i]
        resource_costs = tech.resource_costs
        tech.resource_costs = (resource_costs[0], resource_costs[1], ResearchResourceCost(mutex_id, 3, 1))
        for effect_id in effect_ids:
            disable_tech(data.effects[effect_id], i)
