import open3d as o3d
import numpy as np

def pick_points(ply_file):
    pcd = o3d.io.read_point_cloud(ply_file)

    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window("PLY Viewer")
    vis.add_geometry(pcd)
    vis.run()
    vis.destroy_window()

    points_indices = vis.get_picked_points()

    points_coordinates = np.asarray(pcd.points)[points_indices]

    return points_coordinates


if __name__ == "__main__":
    pick_points("F:\\Measurements\\SavedData\\100\\pointcloud_1.ply")