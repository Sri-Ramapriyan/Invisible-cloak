# invisible_cloak.py
"""
Invisible Cloak (Red) using OpenCV.
- Requires background.jpg produced by background.py in the same folder.
- Press 'q' or ESC to quit. Press 's' to save a snapshot.
- Optional: --save output.mp4 to record the effect.

Tip: Use a bright, saturated red cloth; avoid wearing other red items.
"""

import cv2
import numpy as np
import argparse
import os
import time

def open_camera(index: int):
    cap = None
    try:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(index)
    except Exception:
        cap = cv2.VideoCapture(index)
    return cap

def build_red_mask(hsv):
    """
    Build mask for red to orange cloak.
    Covers:
      - pure red (0°–10° and 170°–180° in HSV hue circle)
      - extended reddish-orange (10°–25°)
    """
    # Pure red ranges
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Reddish-orange range
    lower_orange = np.array([10, 100, 70])
    upper_orange = np.array([25, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask3 = cv2.inRange(hsv, lower_orange, upper_orange)

    # Combine masks
    mask = mask1 | mask2 | mask3

    # Clean mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)

    return mask


def main():
    parser = argparse.ArgumentParser(description="Invisible cloak effect (red).")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--background", type=str, default="background.jpg", help="Path to background image")
    parser.add_argument("--save", type=str, default="", help="Optional: output video path (e.g., output.mp4)")
    args = parser.parse_args()

    if not os.path.exists(args.background):
        raise FileNotFoundError(f"Background not found: {args.background}. Run background.py first.")

    bg = cv2.imread(args.background)
    if bg is None:
        raise RuntimeError("Failed to load background image.")

    cap = open_camera(args.camera)
    if not cap or not cap.isOpened():
        raise RuntimeError("Could not open camera. Is it connected and free?")

    # Camera warm-up
    time.sleep(1.0)

    writer = None
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 20.0

    print("Wear something RED and step into frame. Press 'q'/ESC to quit, 's' to save a snapshot.")
    snapshot_idx = 1

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        # Mirror for natural 'selfie' view
        frame = cv2.flip(frame, 1)

        # Resize background to match camera frame (once we know frame size)
        if bg.shape[:2] != frame.shape[:2]:
            bg = cv2.resize(bg, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_AREA)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cloak_mask = build_red_mask(hsv)
        inv_mask = cv2.bitwise_not(cloak_mask)

        # Regions
        background_part = cv2.bitwise_and(bg, bg, mask=cloak_mask)
        current_part = cv2.bitwise_and(frame, frame, mask=inv_mask)

        final = cv2.add(background_part, current_part)

        overlay = final.copy()
        cv2.putText(overlay, "Invisible Cloak (Red)  |  's': snapshot  'q'/ESC: quit",
                    (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.imshow("Invisible Cloak", overlay)

        # Lazy-init writer after first frame (ensures size known)
        if args.save and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v") if args.save.lower().endswith(".mp4") else cv2.VideoWriter_fourcc(*"XVID")
            writer = cv2.VideoWriter(args.save, fourcc, fps, (final.shape[1], final.shape[0]))

        if writer is not None:
            writer.write(final)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):  # ESC or 'q'
            break
        if key == ord('s'):
            name = f"snapshot_{snapshot_idx:02d}.png"
            cv2.imwrite(name, final)
            print(f"Saved {name}")
            snapshot_idx += 1

    cap.release()
    if writer is not None:
        writer.release()
        print(f"Saved video to {os.path.abspath(args.save)}")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
