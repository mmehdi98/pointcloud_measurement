import open3d as o3d
import numpy as np

def pick_points(ply_file):
    pcd = o3d.io.read_point_cloud(ply_file)

    vis = o3d.visualization.VisualizerWithVertexSelection()
    vis.create_window("PLY Viewer")
    vis.add_geometry(pcd)
    vis.run()  # Run the visualizer
    vis.destroy_window()

    points = vis.get_picked_points()

    return points


if __name__ == "__main__":
    pick_points("F:\\Measurements\\SavedData\\100\\pointcloud_8.ply")