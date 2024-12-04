from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, HttpUrl, Field  
import json 
import requests 

from math import ceil

app = FastAPI()


pokemon_list = []
DATA_URL = "https://raw.githubusercontent.com/DetainedDeveloper/Pokedex/master/pokedex_raw/pokedex_raw_array.json"

class Ability(BaseModel):
    name : str 
    is_hidden : bool 

class Stats(BaseModel):
    name : str 
    base_stat : int = Field(gt = 0)

class Type(BaseModel):
    name : str 

class Update(BaseModel):
    name : str 
    height : int 
    weight : int 
    xp : int 
    image_url : HttpUrl
    pokemon_url : HttpUrl
    ability : list[Ability]
    stats : list[Stats]
    type : list[Type]

class Pokemon(BaseModel):
    id : int = Field(gt=0)
    name : str 
    height : int = Field(ge = 0)
    weight : int = Field(ge= 0)
    xp : int 
    image_url : HttpUrl
    pokemon_url : HttpUrl
    ability : list[Ability]
    stats : list[Stats]
    type : list[Type]


def load_pokemon_data():

    response = requests.get(DATA_URL)
    if response.status_code != 200:
        raise Exception("Failed Pokémon")
    
    data = response.json()  
    pokemon_list.extend(data)
    # for pokemon in data:
    #     pokemon_list[pokemon["id"]] = pokemon
load_pokemon_data()

@app.patch("/pokemon/{pokemon_id}")
def patch_pokemon(pokemon_id: int, updates: dict):

    pokemon = next((p for p in pokemon_list if p["id"] == pokemon_id), None)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    for key, value in updates.items():
        if key in pokemon:
            pokemon[key] = value
        else:
            raise HTTPException(status_code=400, detail=f"Invalid field: {key}")

    return {"message": "Pokémon updated successfully", "pokemon": pokemon}

@app.get("/pokemon/all")
def get_pokemon(
    page: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, le=30)  
):

    total_items = len(pokemon_list)
    total_pages = ceil(total_items / size) 
    
   
    if page > total_pages:
        raise HTTPException(status_code=404, detail=f"There are only {total_pages} pages available.")

    start = (page - 1) * size
    end = start + size
    paginated_pokemon = pokemon_list[start:end]

    return {
        "page": page,
        "size": size,
        "total": total_items,
        "total_pages": total_pages, 
        "data": paginated_pokemon
    }


@app.get("/pokemon/search")
def partial_search(key: str, value: str):

    try:

        filtered_pokemon = [
            pokemon for pokemon in pokemon_list
            if str(pokemon.get(key)) == value
        ]

        if not filtered_pokemon:
            raise HTTPException(status_code=404, detail="No Pokémon match the criteria.")
        
        return filtered_pokemon

    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid key: {key}")



@app.get("/pokemon/{pokemon_id}")
def get_pokemon_by_id(pokemon_id: int):
    for pokemon in pokemon_list:
        if pokemon["id"] == pokemon_id:
            return pokemon
    raise HTTPException(status_code=404, detail="Pokémon not found")


@app.get("/pokemon")
def get_all_pokemon():
    return pokemon_list


def is_url_accessible(url: str) -> bool:
    try:
        response = requests.head(url, timeout=5)  
        return response.status_code == 200
    except requests.RequestException:
        return False



@app.post("/pokemon")
def create_pokemon(pokemon: Pokemon):
    if pokemon.id in pokemon_list:
        raise HTTPException(status_code=400, detail="Pokémon with this ID already exists.")
    
    if not is_url_accessible(pokemon.image_url):
        raise HTTPException(status_code=400, detail="Invalid or inaccessible image URL.")
    if not is_url_accessible(pokemon.pokemon_url):
        raise HTTPException(status_code=400, detail="Invalid or inaccessible Pokémon URL.")

    pokemon_list[pokemon.id] = pokemon.dict()  # Convert to dictionary and add to the list
    return {"message": "Pokemon added", "pokemon": pokemon}


#UPDATE
@app.put("/pokemon/{pokemon_id}")
def update_pokemon(pokemon_id: int, pokemon: Pokemon):
    if pokemon_id not in pokemon_list:
        raise HTTPException(status_code=404, detail="Pokémon not found.")
    
    if not is_url_accessible(pokemon.image_url):
        raise HTTPException(status_code=400, detail="Invalid or inaccessible image URL.")
    if not is_url_accessible(pokemon.pokemon_url):
        raise HTTPException(status_code=400, detail="Invalid or inaccessible Pokémon URL.")

    pokemon_list[pokemon_id] = pokemon.dict()  
    return {"message": "Pokemon updated", "pokemon": pokemon}

#delete
@app.delete("/pokemon/{pokemon_id}")
def delete_by_id(pokemon_id : int , pokemon : Pokemon):
    if pokemon_id not in pokemon_list:
        raise HTTPException(status_code=404, detail = "NOT FOUND.")
    del pokemon_list[pokemon.id]
    return {"messsage":"Pokemon deleted"}




