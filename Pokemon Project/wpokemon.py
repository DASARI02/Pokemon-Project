import json
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi-pagination import Page, add_pagination, paginate
from simple_pokemon.schemas import Pokemon
 
app = FastAPI(
    docs_url="/",
    title="Simple Pokemon",
    )
 
add_pagination(app)
 
pokemons = []
 
file_path = "simple_pokemon/pokedex_raw_array.json"
 
def load_data():
    with open(file_path, "r") as file:
        pokemons.extend(json.load(file))    
    return f'total {len(pokemons)} pokemon added.'
 
 
load_data()
 
@app.get("/pokemon", tags=["Pokedex"])
def get_all_pokemon() -> Page[Pokemon]:
    if pokemons:
        return paginate(pokemons)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No pokemon found."
        )
 
 
@app.post("/pokemon/{key}/{value}", tags=["Pokedex"], response_model=List[Pokemon])
def get_pokemon(key: str, value: str):
    search_list = []
 
    if key == "id":
        for pokemon in pokemons:
            if pokemon["id"] == int(value):
                search_list.append(pokemon)
 
    elif key == "name":
        for pokemon in pokemons:
            if pokemon["name"] == value:
                search_list.append(pokemon)
 
    elif key == "height":
        for pokemon in pokemons:
            if pokemon["height"] == int(value):
                search_list.append(pokemon)
 
    elif key == "weight":
        for pokemon in pokemons:
            if pokemon["weight"] == int(value):
                search_list.append(pokemon)
 
    elif key == "xp":
        for pokemon in pokemons:
            if pokemon["xp"] == int(value):
                search_list.append(pokemon)
 
    elif key == "image_url":
        for pokemon in pokemons:
            if pokemon["image_url"] == value:
                search_list.append(pokemon)
 
    elif key == "pokemon_url":
        for pokemon in pokemons:
            if pokemon["pokemon_url"] == value:
                search_list.append(pokemon)
 
    elif key == "abilities":
        for pokemon in pokemons:
            if value in pokemon["abilities"]:
                search_list.append(pokemon)
 
    elif key == "stats":
        for pokemon in pokemons:
            if value in pokemon["stats"]:
                search_list.append(pokemon)
 
    elif key == "types":
        for pokemon in pokemons:
            if value in pokemon["types"]:
                search_list.append(pokemon)
 
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid search key"
        )
 
    if not search_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No pokemon with {key} = {value}"
        )
 
    return search_list
 
 
@app.post("/pokemon", tags=["Pokedex"], status_code=status.HTTP_201_CREATED)
def create_pokemon(new_pokemon: Pokemon):
    if pokemons:
        max_id = max(pokemon["id"] for pokemon in pokemons)
        new_pokemon.id = max_id + 1
    else:
        new_pokemon.id = 1
    pokemons.append(new_pokemon.dict())
    return {"detail": "Added pokemon.", "pokemon": new_pokemon}
 
@app.delete("/pokemon", tags=["Pokedex"], status_code=status.HTTP_200_OK)
def delete_pokemon(id: int):
    pokemon = get_pokemon(key="id",value=str(id))
    if pokemon:
        pokemons.remove(pokemon[0])
        return {
            "detail": "Pokemon deleted sucessfully.",
            "pokemon": pokemon[0]
            }
    raise HTTPException(
        detail=f"Pokemon with id:{id} not found.",
        status_code= status.HTTP_404_NOT_FOUND
    )
 