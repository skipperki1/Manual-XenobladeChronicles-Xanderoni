# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item
from Options import OptionError

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

CollectopaediaRequirements = {
    "Colony 9":         { "Vegetable": 1,  "Flower": 1,  "Fruit": 1,  "Animal": 0,  "Bug": 1,  "Nature": 0,  "Part": 1,  "Strange": 1 },
    "Tephra Cave":      { "Vegetable": 0,  "Flower": 2,  "Fruit": 2,  "Animal": 1,  "Bug": 2,  "Nature": 1,  "Part": 0,  "Strange": 2 },
    "Bionis' Leg":      { "Vegetable": 2,  "Flower": 0,  "Fruit": 3,  "Animal": 0,  "Bug": 3,  "Nature": 2,  "Part": 2,  "Strange": 3 },
    "Colony 6":         { "Vegetable": 0,  "Flower": 3,  "Fruit": 0,  "Animal": 2,  "Bug": 0,  "Nature": 0,  "Part": 0,  "Strange": 4 },
    "Ether Mine":       { "Vegetable": 0,  "Flower": 0,  "Fruit": 0,  "Animal": 3,  "Bug": 4,  "Nature": 3,  "Part": 3,  "Strange": 5 },
    "Satorl Marsh":     { "Vegetable": 3,  "Flower": 4,  "Fruit": 0,  "Animal": 4,  "Bug": 0,  "Nature": 4,  "Part": 4,  "Strange": 6 },
    "Bionis' Interior": { "Vegetable": 4,  "Flower": 0,  "Fruit": 0,  "Animal": 5,  "Bug": 0,  "Nature": 0,  "Part": 0,  "Strange": 7 },
    "Makna Forest":     { "Vegetable": 5,  "Flower": 5,  "Fruit": 4,  "Animal": 6,  "Bug": 5,  "Nature": 0,  "Part": 0,  "Strange": 8 },
    "Frontier Village": { "Vegetable": 0,  "Flower": 0,  "Fruit": 5,  "Animal": 0,  "Bug": 6,  "Nature": 0,  "Part": 0,  "Strange": 9 },
    "Eryth Sea":        { "Vegetable": 6,  "Flower": 6,  "Fruit": 0,  "Animal": 7,  "Bug": 0,  "Nature": 5,  "Part": 0,  "Strange": 10 },
    "Alcamoth":         { "Vegetable": 0,  "Flower": 7,  "Fruit": 6,  "Animal": 0,  "Bug": 0,  "Nature": 0,  "Part": 0,  "Strange": 11 },
    "High Entia Tomb":  { "Vegetable": 0,  "Flower": 0,  "Fruit": 0,  "Animal": 0,  "Bug": 7,  "Nature": 0,  "Part": 5,  "Strange": 12 },
    "Valak Mountain":   { "Vegetable": 7,  "Flower": 8,  "Fruit": 7,  "Animal": 8,  "Bug": 0,  "Nature": 6,  "Part": 0,  "Strange": 13 },
    "Sword Valley":     { "Vegetable": 8,  "Flower": 9,  "Fruit": 8,  "Animal": 0,  "Bug": 0,  "Nature": 0,  "Part": 6,  "Strange": 14 },
    "Galahad Fortress": { "Vegetable": 0,  "Flower": 0,  "Fruit": 0,  "Animal": 0,  "Bug": 8,  "Nature": 0,  "Part": 7,  "Strange": 15 },
    "Fallen Arm":       { "Vegetable": 9,  "Flower": 0,  "Fruit": 9,  "Animal": 9,  "Bug": 0,  "Nature": 7,  "Part": 8,  "Strange": 16 },
    "Mechonis Field":   { "Vegetable": 10, "Flower": 10, "Fruit": 0,  "Animal": 0,  "Bug": 9,  "Nature": 8,  "Part": 9,  "Strange": 17 },
    "Central Factory":  { "Vegetable": 11, "Flower": 0,  "Fruit": 0,  "Animal": 10, "Bug": 10, "Nature": 9,  "Part": 10, "Strange": 18 },
    "Agniratha":        { "Vegetable": 0,  "Flower": 11, "Fruit": 10, "Animal": 0,  "Bug": 11, "Nature": 10, "Part": 11, "Strange": 19 },
    "Prison Island":    { "Vegetable": 0,  "Flower": 0,  "Fruit": 11, "Animal": 11, "Bug": 12, "Nature": 11, "Part": 12, "Strange": 20 },
    "Other":            { "Vegetable": 0,  "Flower": 0,  "Fruit": 0,  "Animal": 0,  "Bug": 13, "Nature": 0,  "Part": 13, "Strange": 21 },
}

COLLECTOPAEDIA_LOCATIONS = [
    { "name": "Colony 9 Collectopaedia Page Completion", "area": "Colony 9", "cat": "ALL" },
    { "name": "Colony 9 Collectopaedia Vegetable Completion", "area": "Colony 9", "cat": "Vegetable" },
    { "name": "Colony 9 Collectopaedia Flower Completion", "area": "Colony 9", "cat": "Flower" },
    { "name": "Colony 9 Collectopaedia Fruit Completion", "area": "Colony 9", "cat": "Fruit" },
    { "name": "Colony 9 Collectopaedia Bug Completion", "area": "Colony 9", "cat": "Bug" },
    { "name": "Colony 9 Collectopaedia Part Completion", "area": "Colony 9", "cat": "Part" },
    { "name": "Colony 9 Collectopaedia Strange Completion", "area": "Colony 9", "cat": "Strange" },
    { "name": "Tephra Cave Collectopaedia Page Complete", "area": "Tephra Cave", "cat": "ALL" },
    { "name": "Tephra Cave Collectopaedia Flower Completion", "area": "Tephra Cave", "cat": "Flower" },
    { "name": "Tephra Cave Collectopaedia Fruit Completion", "area": "Tephra Cave", "cat": "Fruit" },
    { "name": "Tephra Cave Collectopaedia Animal Completion", "area": "Tephra Cave", "cat": "Animal" },
    { "name": "Tephra Cave Collectopaedia Bug Completion", "area": "Tephra Cave", "cat": "Bug" },
    { "name": "Tephra Cave Collectopaedia Nature Completion", "area": "Tephra Cave", "cat": "Nature" },
    { "name": "Tephra Cave Collectopaedia Strange Completion", "area": "Tephra Cave", "cat": "Strange" },
    { "name": "Bionis' Leg Collectopaedia Page Completion", "area": "Bionis' Leg", "cat": "ALL" },
    { "name": "Bionis' Leg Collectopaedia Vegetable Completion", "area": "Bionis' Leg", "cat": "Vegetable" },
    { "name": "Bionis' Leg Collectopaedia Fruit Completion", "area": "Bionis' Leg", "cat": "Fruit" },
    { "name": "Bionis' Leg Collectopaedia Bug Completion", "area": "Bionis' Leg", "cat": "Bug" },
    { "name": "Bionis' Leg Collectopaedia Nature Completion", "area": "Bionis' Leg", "cat": "Nature" },
    { "name": "Bionis' Leg Collectopaedia Part Completion", "area": "Bionis' Leg", "cat": "Part" },
    { "name": "Bionis' Leg Collectopaedia Strange Completion", "area": "Bionis' Leg", "cat": "Strange" },
    { "name": "Colony 6 Collectopaedia Page Completion", "area": "Colony 6", "cat": "ALL" },
    { "name": "Colony 6 Collectopaedia Flower Completion", "area": "Colony 6", "cat": "Flower" },
    { "name": "Colony 6 Collectopaedia Animal Completion", "area": "Colony 6", "cat": "Animal" },
    { "name": "Colony 6 Collectopaedia Strange Completion", "area": "Colony 6", "cat": "Strange" },
    { "name": "Ether Mine Collectopaedia Page Completion", "area": "Ether Mine", "cat": "ALL" },
    { "name": "Ether Mine Collectopaedia Animal Completion", "area": "Ether Mine", "cat": "Animal" },
    { "name": "Ether Mine Collectopaedia Bug Completion", "area": "Ether Mine", "cat": "Bug" },
    { "name": "Ether Mine Collectopaedia Nature Completion", "area": "Ether Mine", "cat": "Nature" },
    { "name": "Ether Mine Collectopaedia Parts Completion", "area": "Ether Mine", "cat": "Part" },
    { "name": "Ether Mine Collectopaedia Strange Completion", "area": "Ether Mine", "cat": "Strange" },
    { "name": "Satorl Marsh Collectopaedia Page Completion", "area": "Satorl Marsh", "cat": "ALL" },
    { "name": "Satorl Marsh Collectopaedia Vegetable Completion", "area": "Satorl Marsh", "cat": "Vegetable" },
    { "name": "Satorl Marsh Collectopaedia Flower Completion", "area": "Satorl Marsh", "cat": "Flower" },
    { "name": "Satorl Marsh Collectopaedia Animal Completion", "area": "Satorl Marsh", "cat": "Animal" },
    { "name": "Satorl Marsh Collectopaedia Nature Completion", "area": "Satorl Marsh", "cat": "Nature" },
    { "name": "Satorl Marsh Collectopaedia Parts Completion", "area": "Satorl Marsh", "cat": "Part" },
    { "name": "Satorl Marsh Collectopaedia Strange Completion", "area": "Satorl Marsh", "cat": "Strange" },
    { "name": "Makna Forest Collectopaedia Page Completion", "area": "Makna Forest", "cat": "ALL" },
    { "name": "Makna Forest Collectopaedia Vegetable Completion", "area": "Makna Forest", "cat": "Vegetable" },
    { "name": "Makna Forest Collectopaedia Flower Completion", "area": "Makna Forest", "cat": "Flower" },
    { "name": "Makna Forest Collectopaedia Fruit Completion", "area": "Makna Forest", "cat": "Fruit" },
    { "name": "Makna Forest Collectopaedia Animal Completion", "area": "Makna Forest", "cat": "Animal" },
    { "name": "Makna Forest Collectopaedia Bug Completion", "area": "Makna Forest", "cat": "Bug" },
    { "name": "Makna Forest Collectopaedia Strange Completion", "area": "Makna Forest", "cat": "Strange" },
    { "name": "Frontier Village Collectopaedia Page Completion", "area": "Frontier Village", "cat": "ALL" },
    { "name": "Frontier Village Collectopaedia Fruit Completion", "area": "Frontier Village", "cat": "Fruit" },
    { "name": "Frontier Village Collectopaedia Bug Completion", "area": "Frontier Village", "cat": "Bug" },
    { "name": "Frontier Village Collectopaedia Strange Completion", "area": "Frontier Village", "cat": "Strange" },
    { "name": "Eryth Sea Collectopaedia Page Completion", "area": "Eryth Sea", "cat": "ALL" },
    { "name": "Eryth Sea Collectopaedia Vegetable Completion", "area": "Eryth Sea", "cat": "Vegetable" },
    { "name": "Eryth Sea Collectopaedia Flower Completion", "area": "Eryth Sea", "cat": "Flower" },
    { "name": "Eryth Sea Collectopaedia Animal Completion", "area": "Eryth Sea", "cat": "Animal" },
    { "name": "Eryth Sea Collectopaedia Nature Completion", "area": "Eryth Sea", "cat": "Nature" },
    { "name": "Eryth Sea Collectopaedia Strange Completion", "area": "Eryth Sea", "cat": "Strange" },
    { "name": "Alcamoth Collectopaedia Page Completion", "area": "Alcamoth", "cat": "ALL" },
    { "name": "Alcamoth Collectopaedia Flower Completion", "area": "Alcamoth", "cat": "Flower" },
    { "name": "Alcamoth Collectopaedia Fruit Completion", "area": "Alcamoth", "cat": "Fruit" },
    { "name": "Alcamoth Collectopaedia Strange Completion", "area": "Alcamoth", "cat": "Strange" },
    { "name": "High Entia Tomb Collectopaedia Page Completion", "area": "High Entia Tomb", "cat": "ALL" },
    { "name": "High Entia Tomb Collectopaedia Part Completion", "area": "High Entia Tomb", "cat": "Part" },
    { "name": "High Entia Tomb Collectopaedia Bug Completion", "area": "High Entia Tomb", "cat": "Bug" },
    { "name": "High Entia Tomb Collectopaedia Strange Completion", "area": "High Entia Tomb", "cat": "Strange" },
    { "name": "Valak Mountain Collectopaedia Page Completion", "area": "Valak Mountain", "cat": "ALL" },
    { "name": "Valak Mountain Collectopaedia Vegetable Completion", "area": "Valak Mountain", "cat": "Vegetable" },
    { "name": "Valak Mountain Collectopaedia Flower Completion", "area": "Valak Mountain", "cat": "Flower" },
    { "name": "Valak Mountain Collectopaedia Fruit Completion", "area": "Valak Mountain", "cat": "Fruit" },
    { "name": "Valak Mountain Collectopaedia Animal Completion", "area": "Valak Mountain", "cat": "Animal" },
    { "name": "Valak Mountain Collectopaedia Nature Completion", "area": "Valak Mountain", "cat": "Nature" },
    { "name": "Valak Mountain Collectopaedia Strange Completion", "area": "Valak Mountain", "cat": "Strange" },
    { "name": "Sword Valley Collectopaedia Page Completion", "area": "Sword Valley", "cat": "ALL" },
    { "name": "Sword Valley Collectopaedia Flower Completion", "area": "Sword Valley", "cat": "Flower" },
    { "name": "Sword Valley Collectopaedia Fruit Completion", "area": "Sword Valley", "cat": "Fruit" },
    { "name": "Sword Valley Collectopaedia Vegetable Completion", "area": "Sword Valley", "cat": "Vegetable" },
    { "name": "Sword Valley Collectopaedia Strange Completion", "area": "Sword Valley", "cat": "Strange" },
    { "name": "Sword Valley Collectopaedia Part Completion", "area": "Sword Valley", "cat": "Part" },
    { "name": "Galahad Fortress Collectopaedia Page Completion", "area": "Galahad Fortress", "cat": "ALL" },
    { "name": "Galahad Fortress Collectopaedia Bug Completion", "area": "Galahad Fortress", "cat": "Bug" },
    { "name": "Galahad Fortress Collectopaedia Part Completion", "area": "Galahad Fortress", "cat": "Part" },
    { "name": "Galahad Fortress Collectopaedia Strange Completion", "area": "Galahad Fortress", "cat": "Strange" },
    { "name": "Fallen Arm Collectopaedia Page Completion", "area": "Fallen Arm", "cat": "ALL" },
    { "name": "Fallen Arm Collectopaedia Vegetable Completion", "area": "Fallen Arm", "cat": "Vegetable" },
    { "name": "Fallen Arm Collectopaedia Fruit Completion", "area": "Fallen Arm", "cat": "Fruit" },
    { "name": "Fallen Arm Collectopaedia Animal Completion", "area": "Fallen Arm", "cat": "Animal" },
    { "name": "Fallen Arm Collectopaedia Nature Completion", "area": "Fallen Arm", "cat": "Nature" },
    { "name": "Fallen Arm Collectopaedia Part Completion", "area": "Fallen Arm", "cat": "Part" },
    { "name": "Fallen Arm Collectopaedia Strange Completion", "area": "Fallen Arm", "cat": "Strange" },
    { "name": "Mechonis Field Collectopaedia Page Completion", "area": "Mechonis Field", "cat": "ALL" },
    { "name": "Mechonis Field Collectopaedia Flower Completion", "area": "Mechonis Field", "cat": "Flower" },
    { "name": "Mechonis Field Collectopaedia Vegetable Completion", "area": "Mechonis Field", "cat": "Vegetable" },
    { "name": "Mechonis Field Collectopaedia Bug Completion", "area": "Mechonis Field", "cat": "Bug" },
    { "name": "Mechonis Field Collectopaedia Nature Completion", "area": "Mechonis Field", "cat": "Nature" },
    { "name": "Mechonis Field Collectopaedia Part Completion", "area": "Mechonis Field", "cat": "Part" },
    { "name": "Mechonis Field Collectopaedia Strange Completion", "area": "Mechonis Field", "cat": "Strange" },
    { "name": "Central Factory Collectopaedia Page Completion", "area": "Central Factory", "cat": "ALL" },
    { "name": "Central Factory Collectopaedia Vegetable Completion", "area": "Central Factory", "cat": "Vegetable" },
    { "name": "Central Factory Collectopaedia Animal Completion", "area": "Central Factory", "cat": "Animal" },
    { "name": "Central Factory Collectopaedia Bug Completion", "area": "Central Factory", "cat": "Bug" },
    { "name": "Central Factory Collectopaedia Nature Completion", "area": "Central Factory", "cat": "Nature" },
    { "name": "Central Factory Collectopaedia Part Completion", "area": "Central Factory", "cat": "Part" },
    { "name": "Central Factory Collectopaedia Strange Completion", "area": "Central Factory", "cat": "Strange" },
    { "name": "Agniratha Collectopaedia Page Completion", "area": "Agniratha", "cat": "ALL" },
    { "name": "Agniratha Collectopaedia Fruit Completion", "area": "Agniratha", "cat": "Fruit" },
    { "name": "Agniratha Collectopaedia Flower Completion", "area": "Agniratha", "cat": "Flower" },
    { "name": "Agniratha Collectopaedia Bug Completion", "area": "Agniratha", "cat": "Bug" },
    { "name": "Agniratha Collectopaedia Nature Completion", "area": "Agniratha", "cat": "Nature" },
    { "name": "Agniratha Collectopaedia Part Completion", "area": "Agniratha", "cat": "Part" },
    { "name": "Agniratha Collectopaedia Strange Completion", "area": "Agniratha", "cat": "Strange" },
    { "name": "Bionis' Interior Collectopaedia Page Completion", "area": "Bionis' Interior", "cat": "ALL" },
    { "name": "Bionis' Interior Collectopaedia Vegetable Completion", "area": "Bionis' Interior", "cat": "Vegetable" },
    { "name": "Bionis' Interior Collectopaedia Animal Completion", "area": "Bionis' Interior", "cat": "Animal" },
    { "name": "Bionis' Interior Collectopaedia Strange Completion", "area": "Bionis' Interior", "cat": "Strange" },
    { "name": "Prison Island Collectopaedia Page Completion", "area": "Prison Island", "cat": "ALL" },
    { "name": "Prison Island Collectopaedia Fruit Completion", "area": "Prison Island", "cat": "Fruit" },
    { "name": "Prison Island Collectopaedia Animal Completion", "area": "Prison Island", "cat": "Animal" },
    { "name": "Prison Island Collectopaedia Bug Completion", "area": "Prison Island", "cat": "Bug" },
    { "name": "Prison Island Collectopaedia Nature Completion", "area": "Prison Island", "cat": "Nature" },
    { "name": "Prison Island Collectopaedia Part Completion", "area": "Prison Island", "cat": "Part" },
    { "name": "Prison Island Collectopaedia Strange Completion", "area": "Prison Island", "cat": "Strange" },
    { "name": "Other Collectopaedia Page Completion", "area": "Other", "cat": "ALL" },
    { "name": "Other Collectopaedia Bug Completion", "area": "Other", "cat": "Bug" },
    { "name": "Other Collectopaedia Part Completion", "area": "Other", "cat": "Part" },
    { "name": "Other Collectopaedia Strange Completion", "area": "Other", "cat": "Strange" }
]

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    def getCollectopaediaValue(world: World, state: CollectionState, player: int, catName: str, cacheKey: str):
        val = state.has_all(world.item_name_groups[catName], player)
        return val

    def getColVal(state: CollectionState, area: str, cat: str, player: int):
        if (cat == "ALL"):
            for item in ["Vegetable", "Flower", "Fruit", "Animal", "Bug", "Nature", "Part", "Strange"]:
                if state.count(f"Progressive {item} Category", player) < CollectopaediaRequirements[area][item]:
                    return False
            return True
        else:
            return state.count(f"Progressive {cat} Category", player) >= CollectopaediaRequirements[area][cat]


    if is_option_enabled(multiworld, player, "Collectopaedia") and is_option_enabled(multiworld, player, "collectopaediasanity"):
        for loc in COLLECTOPAEDIA_LOCATIONS:
            location = multiworld.get_location(loc["name"], player)
            area = loc["area"]
            cat = loc["cat"]
            if cat == "ALL":
                location.access_rule = lambda state, area=area: (getCollectopaediaValue(world, state, player, f"{area} Collectopaedia", "") == True)
            else:
                location.access_rule = lambda state, area=area, cat=cat: (getCollectopaediaValue(world, state, player, f"{area} Collection ({cat})", "") == True)
    elif is_option_enabled(multiworld, player, "Collectopaedia"):
        for loc in COLLECTOPAEDIA_LOCATIONS:
            location = multiworld.get_location(loc["name"], player)
            area = loc["area"]
            cat = loc["cat"]
            location.access_rule = lambda state, area=area, cat=cat: (getColVal(state, area, cat, player) == True)

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    if world.options.Collectopaedia == False and world.options.collectopaediasanity == True:
        raise OptionError(
            "When Collectopaediasanity is set to True, Collectopaedia must also be set to True"
        )

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
