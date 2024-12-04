from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, ValidationError
import requests

app = FastAPI()

pokemon_list = {}
DATA_URL = "https://raw.githubusercontent.com/DetainedDeveloper/Pokedex/master/pokedex_raw/pokedex_raw_array.json"

class Ability(BaseModel):
    name: str
    is_hidden: bool

class Stats(BaseModel):
    name: str
    base_stat: int

class Type(BaseModel):
    name: str

class Pokemon(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    xp: int
    image_url: HttpUrl
    pokemon_url: HttpUrl
    ability: list[Ability]
    stats: list[Stats]
    type: list[Type]

@app.on_event("startup")
def load_pokemon_data():
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        raise Exception("Failed to load Pokémon data.")
    data = response.json()
    for pokemon in data:
        pokemon_list[pokemon["id"]] = pokemon

@app.get("/pokemon/{pokemon_id}")
def get_pokemon_by_id(pokemon_id: int):
    if pokemon_id in pokemon_list:
        return pokemon_list[pokemon_id]
    raise HTTPException(status_code=404, detail="Pokémon not found.")

@app.get("/pokemon")
def get_all_pokemon():
    return {"pokemon_count": len(pokemon_list), "pokemon": list(pokemon_list.values())}

# Helper function to validate URLs
def validate_url(url: str):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Create Pokémon
@app.post("/pokemon")
def create_pokemon(pokemon: Pokemon):
    if pokemon.id in pokemon_list:
        raise HTTPException(status_code=400, detail="Pokémon with this ID already exists.")
    if not validate_url(pokemon.image_url) or not validate_url(pokemon.pokemon_url):
        raise HTTPException(status_code=400, detail="Invalid image_url or pokemon_url.")
    pokemon_list[pokemon.id] = pokemon.dict()  # Convert to dictionary and store
    return {"message": "Pokémon added successfully", "pokemon": pokemon}

# Update Pokémon
@app.put("/pokemon/{pokemon_id}")
def update_pokemon(pokemon_id: int, pokemon: Pokemon):
    if pokemon_id not in pokemon_list:
        raise HTTPException(status_code=404, detail="Pokémon not found.")
    if pokemon_id != pokemon.id:
        raise HTTPException(status_code=400, detail="Cannot change Pokémon ID.")
    if not validate_url(pokemon.image_url) or not validate_url(pokemon.pokemon_url):
        raise HTTPException(status_code=400, detail="Invalid image_url or pokemon_url.")
    pokemon_list[pokemon_id] = pokemon.dict()
    return {"message": "Pokémon updated successfully", "pokemon": pokemon}

# Delete Pokémon
@app.delete("/pokemon/{pokemon_id}")
def delete_pokemon(pokemon_id: int):
    if pokemon_id not in pokemon_list:
        raise HTTPException(status_code=404, detail="Pokémon not found.")
    del pokemon_list[pokemon_id]
    return {"message": "Pokémon deleted successfully"}
