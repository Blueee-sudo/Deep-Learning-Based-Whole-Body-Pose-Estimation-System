import cv2
import numpy as np

COLOR_BODY = (255, 144, 24)
COLOR_FOOT = (209, 46, 114)
COLOR_FACE = (26, 196, 82)
COLOR_L_HAND = (22, 140, 250)
COLOR_R_HAND = (45, 34, 245)

BODY_LINKS = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
]
FOOT_LINKS = [(15, 19), (19, 17), (17, 18), (16, 22), (22, 20), (20, 21)]


def _face_links_abs() -> list:
    base = 23
    links = []
    links += [(base + i, base + i + 1) for i in range(16)]
    links += [(base + i, base + i + 1) for i in range(17, 21)]
    links += [(base + i, base + i + 1) for i in range(22, 26)]
    links += [(base + i, base + i + 1) for i in range(27, 30)]
    links += [(base + i, base + i + 1) for i in range(31, 35)] + [(base + 35, base + 31)]
    links += [(base + i, base + i + 1) for i in range(36, 41)] + [(base + 41, base + 36)]
    links += [(base + i, base + i + 1) for i in range(42, 47)] + [(base + 47, base + 42)]
    links += [(base + i, base + i + 1) for i in range(48, 59)] + [(base + 59, base + 48)]
    links += [(base + i, base + i + 1) for i in range(60, 67)] + [(base + 67, base + 60)]
    return links


def _hand_links(start: int) -> list:
    links = []
    finger_bases = [start + 1 + i * 4 for i in range(5)]
    for mcp in finger_bases:
        links.append((start, mcp))
        links += [(mcp + j, mcp + j + 1) for j in range(3)]
    return links


FACE_LINKS = _face_links_abs()
L_HAND_LINKS = _hand_links(91)
R_HAND_LINKS = _hand_links(112)


def draw_pose(image: np.ndarray, persons: list, alpha: float = 0.85) -> np.ndarray:
    canvas = image.copy()
    overlay = image.copy()
    for person in persons:
        kps = np.array(person["keypoints"])

        def _draw_links(links, color):
            for a, b in links:
                if a >= len(kps) or b >= len(kps):
                    continue
                xa, ya, sa = kps[a]
                xb, yb, sb = kps[b]
                if sa < 1e-3 or sb < 1e-3:
                    continue
                cv2.line(overlay, (int(xa), int(ya)), (int(xb), int(yb)), color, 2, cv2.LINE_AA)

        def _draw_points(indices, color):
            for idx in indices:
                if idx >= len(kps):
                    continue
                x, y, s = kps[idx]
                if s < 1e-3:
                    continue
                cv2.circle(overlay, (int(x), int(y)), 3, color, -1, cv2.LINE_AA)

        _draw_links(BODY_LINKS, COLOR_BODY)
        _draw_points(range(17), COLOR_BODY)
        _draw_links(FOOT_LINKS, COLOR_FOOT)
        _draw_points(range(17, 23), COLOR_FOOT)
        _draw_links(FACE_LINKS, COLOR_FACE)
        _draw_points(range(23, 91), COLOR_FACE)
        _draw_links(L_HAND_LINKS, COLOR_L_HAND)
        _draw_points(range(91, 112), COLOR_L_HAND)
        _draw_links(R_HAND_LINKS, COLOR_R_HAND)
        _draw_points(range(112, 133), COLOR_R_HAND)

    cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)
    return canvas
