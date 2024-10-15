from realsense_handler import RealSenseHandler
from ply_handler import pick_points

def main():
    bag_file = "F:\\Measurements\\Test 1\\300\\20240624_155309.bag"
    save_directory = "F:\\Measurements\\SavedData\\100"
    handler = RealSenseHandler(save_directory, bag_file)
    handler.run()

    points = pick_points(handler.ply_filename)

    for point in points:
        print(point.coord)

if __name__ == "__main__":
    main()
