#!/usr/bin/env python3

import configparser
import glob
import re
from collections import defaultdict


def fix_line(line, replacements=None):
    if replacements:
        for key, value in replacements.items():
            line = line.replace(key, value)

    line = line.replace("!0", "1")
    line = line.replace("!1", "0")
    line = re.sub(r"variable,name=([^,]+),value=", r"var \1=", line)
    line = line.replace("call_action_list,name=", "call_action_list.")
    line = line.replace(",if=", " if ")
    line = line.replace("debuff.", "")
    line = line.replace("buff.", "")
    line = line.replace("dot.", "")
    line = line.replace("variable.", "")
    line = line.replace("spell_targets", "targets")

    # Rogue
    line = line.replace("effective_combo_points", "cp")
    line = line.replace("combo_points", "cp")

    line = (
        line.replace("&", " & ")
        .replace("|", " | ")
        .replace("<", " < ")
        .replace(">", " > ")
        .replace("=", " = ")
        .replace("?", " ? ")
        .replace(">  =", ">=")
        .replace("<  =", "<=")
        .replace(">  ?", ">?")
        .replace("<  ?", "<?")
        .replace("+", " + ")
        .replace("-", " - ")
        .replace("*", " * ")
        .replace("/", " / ")
    )

    return line


def should_skip_line(line):
    starts_with_blacklist = [
        "ancestral_call",
        "apply_poison",
        "arcane_pulse",
        "arcane_torrent",
        "augmentation",
        "bag_of_tricks",
        "berserking",
        "blood_fury",
        "fireblood",
        "flask",
        "food",
        "kick",
        "lights_judgment",
        "pool_resource",
        "snapshot_stats",
        "stealth",
        "use_item,name=algethar_puzzle_box",
        "use_item,name=ashes_of_the_embersoul",
        "use_item,name=dragonfire_bomb_dispenser",
        "use_item,name=elementium_pocket_anvil",
        "use_item,name=enduring_dreadplate",
        "use_item,name=imperfect_ascendancy_serum",
        "use_item,name=manic_grieftorch",
        "use_item,name=stormeaters_boon",
        "use_item,name=windscar_whetstone",

        "goremaws_bite",
    ]

    if any(line.startswith(s) for s in starts_with_blacklist):
        return True
    
    return False

def parse_config_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    
    # Extract sections and their key-value pairs
    config_data = {}
    for section in config.sections():
        config_data[section] = dict(config.items(section))
    
    return config_data


def prettify(raw_apl, replacements=None):
    actions = defaultdict(list)

    for line in raw_apl.split("\n"):
        if line.startswith("#"):
            continue

        match = re.match(r"(actions(?:\.\w+)?)(\+?=\/?)(.+)", line)

        if match:
            key = match.group(1)
            value = match.group(3)

            subkey = ""
            if "." in key:
                subkey = key.split(".")[1]

            if should_skip_line(value):
                continue

            actions[subkey].append(fix_line(value, replacements=replacements))

    text_output = ""
    for key, value in actions.items():
        text_output += f'# {key or "actions"}\n'
        text_output += "\n".join(value)
        text_output += "\n\n"
        
    return text_output


def main():
    config_files = glob.glob('./config/*.conf')
    all_configs = {}
    for config_file in config_files:
        config_name = config_file.split('/')[-1]
        all_configs[config_name] = parse_config_file(config_file)

    for config_name, config_data in all_configs.items():
        with open(config_data['general']['input'], 'r') as f:
            raw_apl = f.read()
        pretty_apl = prettify(raw_apl, replacements=config_data['replacements'])
        
        with open(config_data['general']['output'], 'w') as f:
            f.write(pretty_apl)
        
        print(f'Prettified {config_name} to ./output/{config_name}')


if __name__ == "__main__":
    main()