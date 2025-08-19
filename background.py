# background.py
"""
Capture a clean background image for the invisible cloak effect.
Stand out of frame. Press SPACE to capture; ESC to exit.
Saves: background.jpg (median of several frames for a clean, noise-free background)
"""

import cv2
import numpy as np
import time
import argparse
import os

def open_camera(index: int):
    # Use DirectShow on Windows to avoid long camera open delays
    cap = None
    try:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(index)
    except Exception:
        cap = cv2.VideoCapture(index)
    return cap

def main():
    parser = argparse.ArgumentParser(description="Capture background image.")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--frames", type=int, default=60, help="Frames to average for background (default: 60)")
    parser.add_argument("--output", type=str, default="background.jpg", help="Output filename (default: background.jpg)")
    args = parser.parse_args()

    cap = open_camera(args.camera)
    if not cap or not cap.isOpened():
        raise RuntimeError("Could not open camera. Is it connected and free?")

    # Warm up camera
    time.sleep(1.0)

    print("Remove yourself from the frame. Press SPACE to capture background, ESC to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        # Mirror for natural 'selfie' view; keep consistent with main script
        frame = cv2.flip(frame, 1)
        overlay = frame.copy()
        cv2.putText(overlay, "Remove yourself from frame", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(overlay, "Press SPACE to capture clean background", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(overlay, "ESC to exit", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
        cv2.imshow("Background Capture", overlay)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        if key == 32:  # SPACE
            print("Capturing background... please keep the scene still.")
            frames = []
            for _ in range(args.frames):
                ok2, f = cap.read()
                if not ok2:
                    continue
                f = cv2.flip(f, 1)
                frames.append(f)
                cv2.waitKey(1)

            if not frames:
                print("Failed to capture frames. Try again.")
                continue

            median = np.median(np.stack(frames, axis=0), axis=0).astype(np.uint8)
            cv2.imwrite(args.output, median)
            print(f"Saved background to {os.path.abspath(args.output)}")
            cv2.imshow("Saved Background", median)
            cv2.waitKey(1000)
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
