from skills.pokemon_lookup import PokemonLookupSkill
from skills.type_analysis import TypeAnalysisSkill
from skills.team_synergy import TeamSynergySkill

SKILLS = {
    "pokemon_lookup": PokemonLookupSkill(),
    "type_analysis": TypeAnalysisSkill(),
    "team_synergy": TeamSynergySkill(),
}

def get_skill(name: str):
    return SKILLS.get(name)