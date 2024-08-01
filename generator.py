#!/usr/bin/env python3

import argparse
import json
import math
import requests
import urllib.parse

from collections import defaultdict


def read_json_from_local_path(file_path: str) -> dict:
    with open(file_path) as f:
        file_contents = f.read()
        return json.loads(file_contents)


def read_json_from_qmk_path(qmk_path: str) -> dict:
    url = f"https://raw.githubusercontent.com/qmk/qmk_firmware/master/keyboards/{urllib.parse.quote(qmk_path)}/keyboard.json"
    response = requests.get(url)
    return json.loads(response.content)


def parse_json():
    parser = argparse.ArgumentParser(
        description="Generate a wiring diagram from qmk keyboard.json."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", type=str, help="Path to local keyboard.json file.", dest="file_path"
    )
    group.add_argument(
        "-p",
        type=str,
        help="Path to keyboard in upstream qmk repo. (e.g.: handwired/dactyl_manuform/4x5)",
        dest="qmk_path",
    )

    args = parser.parse_args()
    if not any([args.qmk_path, args.file_path]):
        parser.error("-f or -p argument is required.")

    if args.qmk_path:
        data = read_json_from_qmk_path(args.qmk_path)
    else:
        data = read_json_from_local_path(args.file_path)

    return data


def extract_default_layout(data: dict) -> dict:
    keys = defaultdict(dict)
    layout = data["layouts"][next(iter(data["layouts"]))]["layout"]

    for key in layout:
        y = math.floor(key["y"])
        x = math.floor(key["x"])
        keys[y][x] = key["matrix"]

    return keys


def extract_pins(data: dict) -> dict:
    return data["matrix_pins"]


def extract_pin(row_dict: dict, matrix_pins: dict, col: int, kind: str) -> str:
    if kind == "row":
        i = 0
    elif kind == "col":
        i = 1
    else:
        raise ValueError("Kind should be 'row' or 'col'.")

    kind += "s"

    nth = row_dict[tuple(row_dict.keys())[col]][i]
    nth = nth % len(matrix_pins[kind])

    return matrix_pins[kind][nth]


def extract_row_pin(row_dict: dict, matrix_pins: dict, side: str) -> str:
    if side == "left":
        col = 0
    elif side == "right":
        col = -1
    else:
        raise ValueError("Side should be 'left' or 'right'.")

    return extract_pin(row_dict, matrix_pins, col, "row")


def extract_col_pin(row_dict: dict, matrix_pins: dict, col: int) -> str:
    return extract_pin(row_dict, matrix_pins, col, "col")


def translate_pin(pin: str) -> str:
    # From: https://golem.hu/article/pro-micro-pinout/
    pin_translation = {
        "D3": "TX0",
        "D2": "RX1",
        "D1": "2",
        "D0": "3",
        "D4": "4",
        "C6": "5",
        "D7": "6",
        "E6": "7",
        "B4": "8",
        "B5": "9",
        "B6": "10",
        "B3": "14",
        "B1": "15",
        "B2": "16",
        "F7": "A0",
        "F6": "A1",
        "F5": "A2",
        "F4": "A3",
        "B0": "LED pin (left of crystal)",
        "D5": "LED pin (right of crystal)",
    }

    return pin_translation[pin]


def translated_col_pins(row_dict: dict, matrix_pins: dict) -> tuple:
    col_numbers = map(lambda x: x[1], tuple(row_dict.values()))
    col_pins = map(lambda x: extract_col_pin(row_dict, matrix_pins, x), col_numbers)
    translated_col_pins = map(translate_pin, col_pins)
    return tuple(translated_col_pins)


def print_row(row: dict, matrix_pins: dict, key_width: int) -> None:
    cols = tuple(keys[row].keys())

    left_pin = translate_pin(extract_row_pin(keys[row], matrix_pins, "left"))
    right_pin = translate_pin(extract_row_pin(keys[row], matrix_pins, "right"))

    for i in range(len(cols)):
        if i == 0:
            print(" " * (key_width + 1) * cols[i], end="")
            print(f"{left_pin} " + "-" * (key_width // 2), end=" ")
        else:
            offset = cols[i] - cols[i - 1]
            print(" " * (key_width + 1) * (offset - 1), end="")
        to_print = str(keys[row][cols[i]])
        print(f"{to_print:>{key_width}}", end=" ")

    print("-" * (key_width // 2) + f" {right_pin}")


def print_header(keys: dict, matrix_pins: dict, key_width: int) -> None:
    cols = tuple(keys[0].keys())

    def print_line(to_print: tuple) -> None:
        for i in range(len(cols)):
            if i == 0:
                print(" " * 4, end="")
                offset = 1
            else:
                offset = cols[i] - cols[i - 1]

            print(" " * (key_width + 1) * (offset - 1), end="")
            print(f"{to_print[i]:>{key_width}}", end=" ")

        print()

    print_line(translated_col_pins(keys[0], matrix_pins))
    print_line(("|",) * len(cols))


def print_layout(keys: dict, matrix_pins: dict, key_width: int = 6) -> None:
    print_header(keys, matrix_pins, key_width)
    for row in keys:
        print_row(row, matrix_pins, key_width)


def max_key_width(keys):
    max_width = 0

    for row_dict in keys.values():
        for key_coords in tuple(row_dict.values()):
            max_width = max(len(str(key_coords)), max_width)

    return max_width


data = parse_json()

matrix_pins = extract_pins(data)
keys = extract_default_layout(data)

print_layout(keys, matrix_pins, max_key_width(keys))
