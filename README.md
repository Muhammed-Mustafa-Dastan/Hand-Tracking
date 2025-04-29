# Hand-Tracking

<details>
  <summary>Volume Two Hand Control</summary>

This Python script enables **real-time control of system volume** using **two-hand gestures** via webcam.

## Features

- Detects **pinch gesture** using thumb and index fingers.
- Maps the **distance between hands** to system volume level.
- If both hands perform a pinch, the volume is adjusted **smoothly** using a low-pass filter.
- Visual indicators:
  - Circles and lines showing finger positions.
  - Real-time FPS and volume percentage displayed on screen.

## Requirements

- Python 3.x
- OpenCV
- A `HandTrackingModule` (based on MediaPipe)
- pycaw (for controlling Windows audio)

## Usage

1. Make sure `HandTrackingModule.py` is available.
2. Install required libraries:

    `pip install pycaw comtypes`
3. Run the script:

    `python VolumeTwoHandControl.py`

## Control Logic

- **Pinch gesture (fingers closed)**: Activates volume control.
- **Distance between hands**: Mapped to volume range.
- **If second hand is also pinching**: Volume is updated more slowly for smooth transition.

## Notes

- Only works on **Windows**, due to pycaw dependency.
- Requires webcam access.

</details>
