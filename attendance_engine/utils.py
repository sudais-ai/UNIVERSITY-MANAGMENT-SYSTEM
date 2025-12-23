import cv2
def is_blurry(gray, threshold: float) -> bool:
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold
def ensure_min_face_size(box, min_size: int) -> bool:
    top, right, bottom, left = box
    return (bottom - top) >= min_size and (right - left) >= min_size
def face_distance_to_conf(dist: float) -> float:
    return max(0.0, min(1.0, (0.6 - dist) / 0.6))
