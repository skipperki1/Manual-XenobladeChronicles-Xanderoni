from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value, is_option_enabled
from BaseClasses import MultiWorld, CollectionState

import re

def questPaolaAndNarineReq():
    return "|Shulk Progressive Affinity Rank:4| AND |Reyn Progressive Affinity Rank:4|" \
                " AND ((|Sharla Progressive Affinity Rank:4| AND |Melia Progressive Affinity Rank:4|) " \
                " OR (|Sharla Progressive Affinity Rank:4| AND |Fiora Progressive Affinity Rank:4|)" \
                " OR (|Melia Progressive Affinity Rank:4| AND |Fiora Progressive Affinity Rank:4|))"
