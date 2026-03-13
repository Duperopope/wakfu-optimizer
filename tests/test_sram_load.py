import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.classes.sram import Sram

print(f"Classe: {Sram.name}")
print(f"Elements: {Sram.elements}")
print(f"Sorts feu: {len(Sram.spells['fire'])}")
print(f"Sorts eau: {len(Sram.spells['water'])}")
print(f"Sorts air: {len(Sram.spells['air'])}")
print(f"Sorts neutres: {len(Sram.neutral_spells)}")
print(f"Passifs sram: {len(Sram.passives)}")
print(f"Sorts 3eme barre: {len(Sram.built_in_spells)}")

for element, spells in Sram.spells.items():
    for spell in spells:
        if "damage_table" in spell:
            table = spell["damage_table"]
            print(f"  {spell['display_name']}: {len(table)} paliers ({min(table.keys())}-{max(table.keys())})")

print()
print("OK - Fichier Sram valide")
