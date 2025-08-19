# 🧥 Invisible Cloak (Python + OpenCV)

A fun computer vision project that creates a **real-life invisible cloak effect** using Python and OpenCV.  
When you wear a red/orange cloth, the program replaces it with the captured background — making you look invisible!

---

## 🎥 Demo
<p align="center">
  <img src="demo.gif" width="500"/>
</p>

---

## ⚙️ Features
- Capture a clean background once (`background.py`)
- Run the cloak effect live (`invisible_cloak.py`)
- Works with **red/orange cloaks** (can be extended to other colors)
- Snapshot saving (`s` key)
- Optional video recording (`--save output.mp4`)
- Runs in real-time using your webcam

---

## 🛠️ Requirements
- Python 3.8+
- OpenCV (`opencv-python`)
- NumPy

Install with:
```bash
pip install opencv-python numpy
