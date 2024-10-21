from realsense_handler import RealSenseHandler
from ply_handler import pick_points
import json
import os
import argparse
import sys

def main():
    load, ref = parse()

    bag_file = "F:\\Measurements\\Test 1\\300\\20240624_155309.bag"
    save_directory = f"F:\\Measurements\\SavedData\\{load}"
    handler = RealSenseHandler(save_directory, bag_file)
    handler.run()

    points = pick_points(handler.ply_filename)

    update_coords(points, save_directory, load, ref)

def parse():
    parser = argparse.ArgumentParser(prog="Measurement Tool")
    parser.add_argument("load", type=int, help="The load for which the measurement is being made")
    parser.add_argument('-r', "--ref", default=False, action="store_true", help="Specifies if the current measurement is the reference")

    args = parser.parse_args()
    
    return args.load, args.ref

def update_coords(points, save_directory, load, ref):
    point_coords = []
    for point in points:
        point_coords.append(list(point.coord))

    json_filename = os.path.join(save_directory, f"Coordinates_{load}.json")
    
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as file:
            data = json.load(file)
    else:
        data = {}

    if not ref:
        data[f"test_{len(data)+1}"] = point_coords
    else:
        data[f"ref"] = point_coords

    with open(json_filename, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    main()
