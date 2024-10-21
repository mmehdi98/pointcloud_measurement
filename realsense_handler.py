import pyrealsense2 as rs
import numpy as np
import cv2
import json
import os
import re

class RealSenseHandler:
    def __init__(self, save_directory, bag_file= None):
        self.bag_file = bag_file
        self.save_directory = save_directory
        self.clicked_coordinates = None
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.pc = rs.pointcloud()
        self.points = rs.points()
        self.align = rs.align(rs.stream.color)
        self.paused = False

        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def initialize_pipeline(self):
        if self.bag_file:
            rs.config.enable_device_from_file(self.config, self.bag_file)
        else:
            self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)

    def process_frames(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            print("Could not retrieve frames")
            return None, None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return depth_frame, color_frame, depth_image, color_image

    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            clicked_pixel = (x, y)
            print(f"Clicked pixel coordinates: {clicked_pixel}")
            
            depth_image = param['depth_image']
            depth_frame = param['depth_frame']
            
            depth_value = depth_image[y, x]
            
            depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
            
            x3d, y3d, z3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, clicked_pixel, depth_value)
            print(f"3D World Coordinates (x, y, z): ({x3d}, {y3d}, {z3d})")

            self.clicked_coordinates = {"x": x3d, "y": y3d, "z": z3d, "depth": depth_value, "pixel": clicked_pixel}

    def save_data(self, frames, depth_frame, color_frame, depth_image, color_image):
        if self.clicked_coordinates is None:
            print("No coordinates selected to save.")
        else:
            coordinates_to_save = {
                "x": float(self.clicked_coordinates["x"]),
                "y": float(self.clicked_coordinates["y"]),
                "z": float(self.clicked_coordinates["z"]),
                "depth": int(self.clicked_coordinates["depth"]),
                "pixel": [int(p) for p in self.clicked_coordinates["pixel"]]
            }

            coord_filename = self.get_next_filename("coordinates_color_image", ".json")
            with open(coord_filename, 'w') as coord_file:
                json.dump(coordinates_to_save, coord_file, indent=4)
            print(f"Coordinates saved to: {coord_filename}")

        self.pc.map_to(color_frame)
        points = self.pc.calculate(depth_frame)
        
        next_number, self.ply_filename = self.get_next_filename("pointcloud", ".ply")
        color_filename = self.get_next_filename("color_image", ".png", next_number)
        depth_filename = self.get_next_filename("depth_image", ".npy", next_number)

        ply = rs.save_to_ply(self.ply_filename)
        ply.set_option(rs.save_to_ply.option_ply_binary, False)
        ply.set_option(rs.save_to_ply.option_ply_normals, True)
        print("Saving to output.ply...")
        ply.process(frames)
        print("Done")

        cv2.imwrite(color_filename, color_image)
        print(f"Color image saved to: {color_filename}")

        np.save(depth_filename, depth_image)
        print(f"Depth image saved to: {depth_filename}")

    def get_next_filename(self, base_name, extension, next_number= None):
        if next_number == None:
            files = os.listdir(self.save_directory)
            pattern = re.compile(rf'{base_name}_(\d+)\{extension}$')

            numbers = [int(m.group(1)) for f in files if (m := pattern.match(f))]
            next_number = max(numbers, default=0) + 1 

            return next_number, os.path.join(self.save_directory, f"{base_name}_{next_number}{extension}")
        else:
            return os.path.join(self.save_directory, f"{base_name}_{next_number}{extension}")

    def run(self):
        self.initialize_pipeline()

        try:
            while True:
                if not self.paused:
                    depth_frame, color_frame, depth_image, color_image = self.process_frames()
                    if depth_image is None or color_image is None:
                        continue

                    cv2.imshow('Color Stream', color_image)

                if cv2.getWindowProperty('Color Stream', cv2.WND_PROP_VISIBLE) < 1:
                    break

                key = cv2.waitKey(1) & 0xFF

                if key == ord(' '):
                    self.paused = not self.paused

                if key == ord('q'):
                    break

                if self.paused:
                    cv2.setMouseCallback('Color Stream', self.on_mouse_click, param={
                        'depth_image': depth_image, 
                        'depth_frame': depth_frame, 
                    })

                    if key == ord('s') or (key == ord('S') and (cv2.waitKey(1) & 0xFF == 224)):
                        self.save_data(self.pipeline.wait_for_frames(), depth_frame, color_frame, depth_image, color_image)
                        break

        finally:
            self.pipeline.stop()
            cv2.destroyAllWindows()

# Usage
if __name__ == "__main__":
    bag_file = "F:\\Measurements\\Test 1\\300\\20240624_155309.bag"
    save_directory = "F:\\Measurements\\SavedData\\100"
    handler = RealSenseHandler(save_directory, bag_file)
    handler.run()