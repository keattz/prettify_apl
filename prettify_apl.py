#!/usr/bin/env python3


import re
from collections import defaultdict


def fix_line(line):
    line = re.sub(r"variable,name=([^,]+),value=", r"var \1=", line)
    line = line.replace(",if=", " if ")
    line = line.replace("debuff.", "")
    line = line.replace("buff.", "")
    line = line.replace("dot.", "")
    line = line.replace("variable.", "")
    line = line.replace("spell_targets", "targets")

    # Rogue
    line = line.replace("effective_combo_points", "cp")

    line = (
        line.replace("&", " & ")
        .replace("|", " | ")
        .replace("<", " < ")
        .replace(">", " > ")
        .replace("=", " = ")
        .replace(">  =", ">=")
        .replace("<  =", "<=")
        .replace("+", " + ")
        .replace("-", " - ")
        .replace("*", " * ")
        .replace("/", " / ")
    )

    return line


def prettify(raw_apl):
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

            actions[subkey].append(fix_line(value))

    text_output = ""
    for key, value in actions.items():
        text_output += f'# {key or "actions"}\n'
        text_output += "\n".join(value)
        text_output += "\n\n"
        
    return text_output


def main():
    import os

    args = [
        ["./simc/ActionPriorityLists/rogue_assassination.simc", "out/sin.txt"],
        ["./simc/ActionPriorityLists/rogue_outlaw.simc", "out/outlaw.txt"],
        ["./simc/ActionPriorityLists/rogue_subtlety.simc", "out/sub.txt"],
    ]

    for arg in args:
        input_path, output_path = arg

        with open(input_path) as f:
            raw_apl = f.read()

        output_apl = prettify(raw_apl)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(output_apl)


if __name__ == "__main__":
    main()