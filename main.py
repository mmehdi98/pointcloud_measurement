from realsense_handler import RealSenseHandler
from ply_handler import pick_points
from utils import *

def main():
    load, ref = parse()

    bag_file = "F:\\Measurements\\Test 1\\300\\20240624_155309.bag"
    save_directory = f"F:\\Measurements\\SavedData\\{load}"
    handler = RealSenseHandler(save_directory, bag_file)
    handler.run()

    points = pick_points(handler.ply_filename)

    update_coords(points, save_directory, ref, handler.ply_filename)

if __name__ == "__main__":
    main()
