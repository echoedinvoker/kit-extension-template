import numpy as np

def setup(db: og.Database):
    state = db.internal_state
    state.angular = 0

def cleanup(db: og.Database):
    pass

def quaternion_to_rotation_matrix(q):
    # Normalize the quaternion
    q = q / np.linalg.norm(q)
    x, y, z, w = q

    # Compute rotation matrix elements
    r00 = 1 - 2*y**2 - 2*z**2
    r01 = 2*x*y - 2*z*w
    r02 = 2*x*z + 2*y*w
    r10 = 2*x*y + 2*z*w
    r11 = 1 - 2*x**2 - 2*z**2
    r12 = 2*y*z - 2*x*w
    r20 = 2*x*z - 2*y*w
    r21 = 2*y*z + 2*x*w
    r22 = 1 - 2*x**2 - 2*y**2

    return np.array([[r00, r01, r02],
                     [r10, r11, r12],
                     [r20, r21, r22]])

def rotation_matrix_to_unit_vector(rotation_matrix):
    unit_vector = rotation_matrix[:, 1]
    unit_vector = unit_vector / np.linalg.norm(unit_vector)
    return -unit_vector # because that car move to negative y direction, so it might be the front of the car

def unit_vector_to_angular_degree(unit_vector):
    reference_vector = np.array([0, -1, 0])
    dot_product = np.dot(unit_vector, reference_vector)
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def compute(db: og.Database):
    state = db.internal_state
    orient = db.inputs.orient
    rotation_matrix = quaternion_to_rotation_matrix(orient)
    unit_vector = rotation_matrix_to_unit_vector(rotation_matrix)
    angle_deg = unit_vector_to_angular_degree(unit_vector)
    state.angular = angle_deg

    return True
