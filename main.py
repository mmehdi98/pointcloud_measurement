from realsense_handler import RealSenseHandler
from ply_handler import pick_points
from utils import *

def main():
    stream_from_bag = True

    load, ref = parse()
    save_directory = f"F:\\Measurements\\SavedData\\{load}"

    if stream_from_bag:
        bag_file = "F:\\Measurements\\Test 1\\300\\20240624_155309.bag"
        handler = RealSenseHandler(save_directory, bag_file=bag_file, ref=ref)
    else:
        handler = RealSenseHandler(save_directory, ref=ref)
    handler.run()

    points = pick_points(handler.ply_filename)

    update_coords(points, save_directory, ref, handler.ply_filename)

if __name__ == "__main__":
    main()
