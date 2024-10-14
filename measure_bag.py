import pyrealsense2 as rs
import numpy as np
import cv2
import json
import os
import re

test_load = 100

save_directory = f"F:\\Measurements\\SavedData\\{test_load}"

clicked_coordinates = None

def main():
    global clicked_coordinates

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    bag_file = "F:\\Measurements\\Test 1\\300\\20240624_155309.bag"

    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_device_from_file(bag_file)

    pipeline.start(config)

    pc = rs.pointcloud()

    align_to = rs.stream.color
    align = rs.align(align_to)

    paused = False
    depth_image = None
    depth_frame = None
    color_image = None

    while True:
        if not paused:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not depth_frame or not color_frame:
                print("Could not retrieve frames")
                continue

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            cv2.imshow('Color Image', color_image)

        # Window management
        if cv2.getWindowProperty('Color Image', cv2.WND_PROP_VISIBLE) < 1:
            break

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            paused = not paused

        if key == ord('q'):
            break

        # Desired frame manipulation
        if paused:
            cv2.setMouseCallback('Color Image', on_mouse_click, param={
                'depth_image': depth_image, 
                'depth_frame': depth_frame, 
                'color_frame': color_frame
            })

            if key == ord('s') or (key == ord('S') and (cv2.waitKey(1) & 0xFF == 224)):
                save_data(depth_image, color_image, clicked_coordinates)

    pipeline.stop()
    cv2.destroyAllWindows()


def on_mouse_click(event, x, y, flags, param):
    global clicked_coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_pixel = (x, y)
        print(f"Clicked pixel coordinates: {clicked_pixel}")
        
        depth_image = param['depth_image']
        depth_frame = param['depth_frame']
        color_frame = param['color_frame']
        
        depth_value = depth_image[y, x]
        
        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        
        x3d, y3d, z3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, clicked_pixel, depth_value)
        print(f"3D World Coordinates (x, y, z): ({x3d}, {y3d}, {z3d})")

        clicked_coordinates = {"x": x3d, "y": y3d, "z": z3d, "depth": depth_value, "pixel": clicked_pixel}


def save_data(depth_image, color_image, coordinates):
    if coordinates is None:
        print("No coordinates selected to save.")
        return

    coordinates_to_save = {
        "x": float(coordinates["x"]),
        "y": float(coordinates["y"]),
        "z": float(coordinates["z"]),
        "depth": int(coordinates["depth"]),
        "pixel": [int(p) for p in coordinates["pixel"]]
    }

    coord_filename = get_next_filename("coordinates", ".json")
    color_filename = get_next_filename("color_image", ".png")
    depth_filename = get_next_filename("depth_image", ".npy")

    with open(coord_filename, 'w') as coord_file:
        json.dump(coordinates_to_save, coord_file, indent=4)
    print(f"Coordinates saved to: {coord_filename}")

    cv2.imwrite(color_filename, color_image)
    print(f"Color image saved to: {color_filename}")

    np.save(depth_filename, depth_image)
    print(f"Depth image saved to: {depth_filename}")


def get_next_filename(base_name, extension):
    files = os.listdir(save_directory)
    pattern = re.compile(rf'{base_name}_(\d+)\{extension}$')

    numbers = [int(m.group(1)) for f in files if (m := pattern.match(f))]
    next_number = max(numbers, default=0) + 1 

    return os.path.join(save_directory, f"{base_name}_{next_number}{extension}")

if __name__ == "__main__":
    main()
