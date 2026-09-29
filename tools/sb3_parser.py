#!/usr/bin/env python3
"""
sb3_parser.py

Parses a Scratch .sb3 project file into readable pseudocode per sprite, plus
a block-ID diff against a previous snapshot. Used by the tutor to see what a
student actually built, without relying on what they say they did.

Usage:
    python sb3_parser.py snapshot.sb3
    python sb3_parser.py snapshot.sb3 --previous previous.sb3
    python sb3_parser.py snapshot.sb3 -o parsed.json
"""

import argparse
import json
import sys
import zipfile

# Opcode -> human-readable label. {PARAM} placeholders are filled from that
# block's inputs/fields when present; unknown opcodes fall back to the raw
# opcode string so nothing is silently dropped.
OPCODE_LABELS = {
    "event_whenflagclicked": "when green flag clicked",
    "event_whenkeypressed": "when key [{KEY_OPTION}] pressed",
    "event_whenthisspriteclicked": "when this sprite clicked",
    "event_whenbroadcastreceived": "when I receive [{BROADCAST_OPTION}]",
    "event_broadcast": "broadcast [{BROADCAST_INPUT}]",
    "motion_movesteps": "move ({STEPS}) steps",
    "motion_turnright": "turn right ({DEGREES}) degrees",
    "motion_turnleft": "turn left ({DEGREES}) degrees",
    "motion_gotoxy": "go to x: ({X}) y: ({Y})",
    "motion_goto": "go to [{TO}]",
    "motion_pointindirection": "point in direction ({DIRECTION})",
    "motion_pointtowards": "point towards [{TOWARDS}]",
    "motion_changexby": "change x by ({DX})",
    "motion_changeyby": "change y by ({DY})",
    "motion_setx": "set x to ({X})",
    "motion_sety": "set y to ({Y})",
    "motion_ifonedgebounce": "if on edge, bounce",
    "looks_say": "say [{MESSAGE}]",
    "looks_sayforsecs": "say [{MESSAGE}] for ({SECS}) seconds",
    "looks_think": "think [{MESSAGE}]",
    "looks_show": "show",
    "looks_hide": "hide",
    "looks_nextcostume": "next costume",
    "looks_switchcostumeto": "switch costume to [{COSTUME}]",
    "looks_changesizeby": "change size by ({CHANGE})",
    "looks_setsizeto": "set size to ({SIZE}) %",
    "sound_play": "play sound [{SOUND_MENU}]",
    "sound_playuntildone": "play sound [{SOUND_MENU}] until done",
    "control_repeat": "repeat ({TIMES})",
    "control_forever": "forever",
    "control_if": "if <{CONDITION}> then",
    "control_if_else": "if <{CONDITION}> then / else",
    "control_wait": "wait ({DURATION}) seconds",
    "control_repeat_until": "repeat until <{CONDITION}>",
    "control_stop": "stop [{STOP_OPTION}]",
    "sensing_touchingobject": "touching [{TOUCHINGOBJECTMENU}] ?",
    "sensing_keypressed": "key [{KEY_OPTION}] pressed?",
    "sensing_askandwait": "ask [{QUESTION}] and wait",
    "operator_add": "({NUM1} + {NUM2})",
    "operator_subtract": "({NUM1} - {NUM2})",
    "operator_multiply": "({NUM1} * {NUM2})",
    "operator_divide": "({NUM1} / {NUM2})",
    "operator_equals": "({OPERAND1} = {OPERAND2})",
    "operator_gt": "({OPERAND1} > {OPERAND2})",
    "operator_lt": "({OPERAND1} < {OPERAND2})",
    "operator_and": "<{OPERAND1}> and <{OPERAND2}>",
    "operator_or": "<{OPERAND1}> or <{OPERAND2}>",
    "operator_not": "not <{OPERAND}>",
    "data_setvariableto": "set [{VARIABLE}] to ({VALUE})",
    "data_changevariableby": "change [{VARIABLE}] by ({VALUE})",
}

# Block categories that wrap a substack of other blocks (C-blocks / E-blocks).
SUBSTACK_INPUTS = ("SUBSTACK", "SUBSTACK2")


def load_project_json(sb3_path):
    with zipfile.ZipFile(sb3_path) as z:
        with z.open("project.json") as f:
            return json.load(f)


def resolve_input_value(blocks, input_value):
    """
    A block's `inputs[NAME]` entry looks like [shadow_status, value_or_id, ...].
    `value_or_id` is either:
      - a literal shadow array, e.g. [4, "10"] (number) or [10, "hello"] (text)
      - a block ID string, meaning a reporter block is plugged in
      - None, meaning the slot is empty
    Returns a short display string; reporter blocks are rendered as their
    own pseudocode fragment (recursively), not just an opaque ID.
    """
    if not input_value:
        return ""
    target = input_value[1] if len(input_value) > 1 else None
    if target is None:
        return "?"
    if isinstance(target, list):
        # literal shadow: [TYPE, value] -- value is what we want
        return str(target[1]) if len(target) > 1 else ""
    if isinstance(target, str):
        # a block ID: could be a real reporter block, or a hidden shadow
        # block (e.g. a number input's own default-value shadow)
        block = blocks.get(target)
        if block is None:
            return "?"
        return render_reporter(blocks, block)
    return "?"


def render_reporter(blocks, block):
    opcode = block.get("opcode", "")
    fields = block.get("fields", {}) or {}
    inputs = block.get("inputs", {}) or {}
    if opcode == "math_number" or opcode == "math_integer" or opcode == "math_positive_number":
        return str(fields.get("NUM", [""])[0])
    if opcode == "text":
        return str(fields.get("TEXT", [""])[0])
    if opcode == "data_variable":
        return str(fields.get("VARIABLE", [""])[0])
    label = OPCODE_LABELS.get(opcode, opcode)
    params = {}
    for name, val in fields.items():
        params[name] = val[0] if val else ""
    for name, val in inputs.items():
        if name in SUBSTACK_INPUTS:
            continue
        params[name] = resolve_input_value(blocks, val)
    try:
        return label.format(**params)
    except (KeyError, IndexError):
        return label


def build_node(blocks, block_id, seen):
    if block_id is None or block_id in seen:
        return None
    seen.add(block_id)
    block = blocks.get(block_id)
    if block is None:
        return None

    opcode = block.get("opcode", "unknown")
    fields = {name: val[0] if val else "" for name, val in (block.get("fields") or {}).items()}
    inputs_raw = block.get("inputs", {}) or {}

    params = dict(fields)
    for name, val in inputs_raw.items():
        if name in SUBSTACK_INPUTS:
            continue
        params[name] = resolve_input_value(blocks, val)

    label_template = OPCODE_LABELS.get(opcode, opcode)
    try:
        label = label_template.format(**params)
    except (KeyError, IndexError):
        label = label_template

    node = {
        "id": block_id,
        "opcode": opcode,
        "label": label,
        "fields": fields,
        "params": params,
    }

    # Only C/E-blocks (repeat, if, if-else, ...) actually declare a
    # SUBSTACK/SUBSTACK2 input -- add the key only when the block has it, so
    # an empty substack (nothing dragged in yet) is still distinguishable
    # from "this block doesn't wrap anything at all".
    if "SUBSTACK" in inputs_raw:
        sub = inputs_raw.get("SUBSTACK")
        node["substack"] = build_stack(blocks, sub[1], seen) if sub and isinstance(sub[1], str) else []
    if "SUBSTACK2" in inputs_raw:
        sub2 = inputs_raw.get("SUBSTACK2")
        node["substack2"] = build_stack(blocks, sub2[1], seen) if sub2 and isinstance(sub2[1], str) else []

    next_id = block.get("next")
    node["next"] = build_node(blocks, next_id, seen) if next_id else None
    return node


def build_stack(blocks, first_id, seen):
    result = []
    node = build_node(blocks, first_id, seen)
    while node is not None:
        nxt = node.pop("next", None)
        result.append(node)
        node = nxt
    return result


def node_to_pseudocode(node, indent=0):
    pad = "  " * indent
    lines = [pad + node["label"] + (":" if node.get("substack") is not None else "")]
    for sub_node in node.get("substack", []) or []:
        lines.extend(node_to_pseudocode(sub_node, indent + 1).split("\n"))
    if "substack2" in node:
        lines.append(pad + "else:")
        for sub_node in node["substack2"] or []:
            lines.extend(node_to_pseudocode(sub_node, indent + 1).split("\n"))
    return "\n".join(lines)


def collect_opcodes(node, acc):
    acc.add(node["opcode"])
    for sub_node in node.get("substack", []) or []:
        collect_opcodes(sub_node, acc)
    for sub_node in node.get("substack2", []) or []:
        collect_opcodes(sub_node, acc)


def collect_block_ids(node, acc):
    acc.add(node["id"])
    for sub_node in node.get("substack", []) or []:
        collect_block_ids(sub_node, acc)
    for sub_node in node.get("substack2", []) or []:
        collect_block_ids(sub_node, acc)


def parse_target(target):
    blocks = target.get("blocks", {}) or {}
    scripts = []
    all_opcodes = set()
    all_block_ids = set()
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue  # variable/list reporter values are stored inline too
        if not block.get("topLevel") or block.get("shadow"):
            continue
        seen = set()
        stack = build_stack(blocks, block_id, seen)
        for node in stack:
            collect_opcodes(node, all_opcodes)
            collect_block_ids(node, all_block_ids)
        pseudocode = "\n".join(node_to_pseudocode(node) for node in stack)
        scripts.append({"pseudocode": pseudocode, "tree": stack})
    return scripts, all_opcodes, all_block_ids


def parse_project(project_json):
    sprites = {}
    opcodes_present = set()
    block_ids_present = set()
    for target in project_json.get("targets", []):
        name = target.get("name", "Stage" if target.get("isStage") else "Sprite")
        scripts, opcodes, block_ids = parse_target(target)
        sprites[name] = scripts
        opcodes_present |= opcodes
        block_ids_present |= block_ids
    return sprites, opcodes_present, block_ids_present


def diff_snapshots(prev_opcodes, prev_block_ids, cur_opcodes, cur_block_ids):
    return {
        "opcodes_added": sorted(cur_opcodes - prev_opcodes),
        "opcodes_removed": sorted(prev_opcodes - cur_opcodes),
        "block_count_before": len(prev_block_ids),
        "block_count_after": len(cur_block_ids),
        "blocks_added": len(cur_block_ids - prev_block_ids),
        "blocks_removed": len(prev_block_ids - cur_block_ids),
        "changed": cur_block_ids != prev_block_ids,
    }


def main():
    parser = argparse.ArgumentParser(description="Parse a Scratch .sb3 into pseudocode + diff")
    parser.add_argument("sb3_path", help="path to the .sb3 snapshot to parse")
    parser.add_argument("--previous", help="path to the previous .sb3 snapshot, for a diff")
    parser.add_argument("-o", "--output", help="write JSON here instead of stdout")
    args = parser.parse_args()

    project_json = load_project_json(args.sb3_path)
    sprites, opcodes_present, block_ids_present = parse_project(project_json)

    result = {
        "sprites": sprites,
        "opcodes_present": sorted(opcodes_present),
    }

    if args.previous:
        prev_json = load_project_json(args.previous)
        _, prev_opcodes, prev_block_ids = parse_project(prev_json)
        result["diff"] = diff_snapshots(prev_opcodes, prev_block_ids, opcodes_present, block_ids_present)
    else:
        result["diff"] = None

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
