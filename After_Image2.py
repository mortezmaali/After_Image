import os
import time
import cv2
import numpy as np
from screeninfo import get_monitors

# ----------------------------
# Settings
# ----------------------------
IMAGE_PATH = "Downloads/3.jpg"     # <-- change to your image path
INSTR_SECONDS = 5            # instructions screen duration
NEG_SECONDS = 30             # show negative for 30 sec
GRAY_SECONDS = 30            # show grayscale for 30 sec
FPS = 60                     # target display rate (timing is time-based)

WINDOW_NAME = "Afterimage Demo (ESC to quit)"

# Fixation cross settings
CROSS_SIZE = 18              # half-length of cross arms in pixels
CROSS_THICKNESS = 2
CROSS_GAP = 0
CROSS_COLOR = (255, 255, 255)  # white
CROSS_OUTLINE = True
OUTLINE_THICKNESS = 6

TEXT_OUTLINE_THICKNESS = 8
TEXT_THICKNESS = 3

# ----------------------------
# Helpers
# ----------------------------
def get_primary_monitor_resolution():
    mons = get_monitors()
    primary = None
    for m in mons:
        if hasattr(m, "is_primary") and m.is_primary:
            primary = m
            break
    if primary is None:
        primary = mons[0]
    return int(primary.width), int(primary.height)

def fit_letterbox(img_bgr, W, H):
    """Preserve aspect ratio; letterbox with black bars."""
    h, w = img_bgr.shape[:2]
    s = min(W / w, H / h)
    nw, nh = int(w * s), int(h * s)
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_AREA)
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    x0 = (W - nw) // 2
    y0 = (H - nh) // 2
    frame[y0:y0 + nh, x0:x0 + nw] = resized
    return frame

def to_negative(img_bgr):
    return 255 - img_bgr

def to_grayscale_bgr(img_bgr):
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)

def draw_cross(frame, cx, cy):
    """Draw a small plus in the center."""
    if CROSS_OUTLINE:
        _draw_cross_lines(frame, cx, cy, color=(0, 0, 0), thickness=OUTLINE_THICKNESS)
    _draw_cross_lines(frame, cx, cy, color=CROSS_COLOR, thickness=CROSS_THICKNESS)

def _draw_cross_lines(frame, cx, cy, color, thickness):
    s = CROSS_SIZE
    g = CROSS_GAP
    cv2.line(frame, (cx - s, cy), (cx - g, cy), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (cx + g, cy), (cx + s, cy), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (cx, cy - s), (cx, cy - g), color, thickness, cv2.LINE_AA)
    cv2.line(frame, (cx, cy + g), (cx, cy + s), color, thickness, cv2.LINE_AA)

def put_centered_multiline_text(frame, lines, font_scale=1.6):
    """Big centered instructions with outline."""
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX

    sizes = [cv2.getTextSize(line, font, font_scale, TEXT_THICKNESS)[0] for line in lines]
    heights = [s[1] for s in sizes] if sizes else [0]
    total_h = int(sum(heights) * 1.25)

    y = (h - total_h) // 2 + heights[0]
    for i, line in enumerate(lines):
        tw, th = sizes[i]
        x = (w - tw) // 2
        cv2.putText(frame, line, (x, y), font, font_scale, (0, 0, 0),
                    TEXT_OUTLINE_THICKNESS, cv2.LINE_AA)
        cv2.putText(frame, line, (x, y), font, font_scale, (255, 255, 255),
                    TEXT_THICKNESS, cv2.LINE_AA)
        y += int(th * 1.55)

def show_phase(window_name, base_frame, seconds, show_cross=True, extra_text_lines=None):
    """
    Show a (mostly) static frame for `seconds` using time-based control.
    ESC to quit anytime.
    """
    start = time.perf_counter()
    H, W = base_frame.shape[:2]
    cx, cy = W // 2, H // 2

    frame_static = base_frame.copy()
    if show_cross:
        draw_cross(frame_static, cx, cy)

    if extra_text_lines:
        y0 = 70
        for line in extra_text_lines:
            cv2.putText(frame_static, line, (60, y0), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (0, 0, 0), 6, cv2.LINE_AA)
            cv2.putText(frame_static, line, (60, y0), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (255, 255, 255), 2, cv2.LINE_AA)
            y0 += 48

    while True:
        if (time.perf_counter() - start) >= seconds:
            return True

        cv2.imshow(window_name, frame_static)
        key = cv2.waitKey(int(1000 / FPS)) & 0xFF
        if key == 27:
            return False

def main():
    if not os.path.exists(IMAGE_PATH):
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

    W, H = get_primary_monitor_resolution()
    print(f"Fullscreen resolution: {W} x {H}")

    img = cv2.imread(IMAGE_PATH, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("OpenCV couldn't read the image. Try PNG/JPG and a simple path.")

    neg_full = fit_letterbox(to_negative(img), W, H)
    gray_full = fit_letterbox(to_grayscale_bgr(img), W, H)

    instr = np.zeros((H, W, 3), dtype=np.uint8)
    put_centered_multiline_text(
        instr,
        [
            "INSTRUCTIONS",
            "",
            "When the image appears, fixate on the + in the center.",
            f"Stare at the NEGATIVE image for {NEG_SECONDS} seconds.",
            "Try not to move your eyes.",
            "",
            "Then a BLACK & WHITE image will appear."
        ],
        font_scale=1.6
    )

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Phase 1: instructions (NO plus sign)
    ok = show_phase(WINDOW_NAME, instr, INSTR_SECONDS, show_cross=False)
    if not ok:
        cv2.destroyAllWindows()
        return

    # Phase 2: negative (plus sign ON)
    ok = show_phase(
        WINDOW_NAME,
        neg_full,
        NEG_SECONDS,
        show_cross=True,
        extra_text_lines=[f"NEGATIVE (fixate on +)  |  {NEG_SECONDS} sec"]
    )
    if not ok:
        cv2.destroyAllWindows()
        return

    # Phase 3: grayscale (plus sign ON)
    ok = show_phase(
        WINDOW_NAME,
        gray_full,
        GRAY_SECONDS,
        show_cross=True,
        extra_text_lines=["BLACK & WHITE (do you see colors?)"]
    )

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()