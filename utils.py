import argparse
import os
import re
import json

def parse():
    parser = argparse.ArgumentParser(prog="Measurement Tool")
    parser.add_argument("load", type=int, help="The load for which the measurement is being made")
    parser.add_argument('-r', "--ref", default=False, action="store_true", help="Specifies if the current measurement is the reference")

    args = parser.parse_args()
    
    return args.load, args.ref

def update_coords(point_coords, save_directory, ref, ply_filename):
    if match := re.search(r".*\\(\d+)$", save_directory):
        load = match.group(1)
    else:
        raise ValueError("Save directory not valid")

    if not ref:
        if match := re.search(r".*_(\d+)\.ply$", ply_filename):
            test_num = match.group(1)
        else:
            raise ValueError("ply filename not valid")

    point_coords = point_coords.tolist()

    json_filename = os.path.join(save_directory, f"Coordinates_{load}.json")
    
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as file:
            data = json.load(file)
    else:
        data = {}
    
    if not ref:
        data[f"test_{test_num}"] = point_coords
        data[f"test_{test_num}_ply_filename"] = ply_filename
    else:
        data[f"ref"] = point_coords
        data[f"ref_ply_filename"] = ply_filename

    with open(json_filename, 'w') as file:
        json.dump(data, file, indent=4)