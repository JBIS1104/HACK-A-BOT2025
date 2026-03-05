<h1 align='center'><b>AI Classroom Assistant — HACK-A-BOT 2025</b></h1>
<p align='center'>
  A unified AI camera system that automates classroom <b>attendance tracking</b> and <b>attentiveness monitoring</b> in real time — built in under 24 hours, placing <b>3rd at the University of Manchester Hackathon 2025</b>.
</p>

## Project Demo

<p align='center'>
    <img src="assets/hackabot-demo.jpg" alt="HACK-A-BOT project demo" width="520" />
</p>

<p align='center'>
    <a href="https://youtube.com/shorts/Sxucuh2GTYQ?feature=share"><b>Watch AI Camera Demo Video</b></a>
</p>

---

## What it does

Traditional classrooms handle attendance and attentiveness as two separate, manual tasks. This project merges both into a single AI camera pipeline running on a **Raspberry Pi AI Camera (IMX500 vision sensor)**.

**The system outputs three live metrics per frame:**
| Metric | Description |
|---|---|
| `attendance` | % of expected students detected in frame (confidence > 0.3) |
| `questions` | Number of students with hands raised |
| `understand` | Number of students present but not raising their hand |

These are served in real time as a **JSON payload** via a Flask HTTP endpoint, consumable by any dashboard or display.

---

## How the code works

### Pipeline overview

```
Raspberry Pi AI Camera (IMX500)
        │
        ▼
   PoseNet model (on-device inference)
        │  17-point body keypoints per person
        ▼
   Confidence filter (> 0.3 threshold)
        │  valid detections only
        ▼
   is_hands_up() check per person
        │  wrist keypoints compared against shoulder keypoints
        ▼
   Attendance % + Questions + Understand counts
        │
        ▼
   JSON output via Flask  +  Annotated frame display
```

### Key implementation details

**1. On-device pose estimation (`hands_up_counter_json.py`)**
- Deploys a **PoseNet** model directly onto the IMX500 sensor using the `modlib` SDK
- Each detected person returns a 34-element flat array of keypoints, reshaped to **17 × 2 (x, y)** coordinates covering: nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles
- Skeleton lines are drawn between connected joints (arms, shoulders, torso, legs) using `cv2.line`

**2. Hand-raise detection (`is_hands_up`)**
- Checks whether **wrist keypoints (indices 9 & 10)** are positioned above the corresponding **shoulder keypoints (indices 5 & 6)** in pixel coordinates
- Only runs on keypoints with confidence > 0.3 to avoid false positives from occluded joints
- A green circle is drawn above the head of any student detected with hands raised

**3. Metrics calculation**
```python
attendance = (total_valid / total_student) * 100
questions  = hands_up_count          # raised hands
understand = total_valid - hands_up_count  # present, not raising hand
```

**4. JSON output & Flask server**
- Results per frame are packaged into a dict and served via Flask at `0.0.0.0:5050`
- The live annotated frame (with attendance %, Q count, understand count overlaid) is displayed via `frame.display()`

---

## Repository structure

```
final_code/
    hands_up_counter_json.py   # Final submission — Flask + JSON output
Group21_Works/
    hands_up_counter_json.py   # Development version
modlib/                        # Application Module Library (IMX500 SDK)
tests/                         # Unit tests for modlib
```

---

## Setup & installation

### 1. Raspberry Pi prerequisites
```bash
sudo apt update && sudo apt full-upgrade
sudo apt install imx500-all
sudo apt install python3-opencv python3-munkres python3-picamera2
```
Reboot if needed.

### 2. Install the modlib wheel
```bash
python -m venv .venv --system-site-packages
. .venv/bin/activate
pip install modlib-<version>-py3-none-any.whl
```

Or build the wheel from source:
```bash
make setup
make build
```

### 3. Run the classifier
```bash
. .venv/bin/activate
python final_code/hands_up_counter_json.py
```

The Flask server starts at port `5050`. JSON metrics are available at `http://<pi-ip>:5050`.

> Run tests: `make test`  
> Run linter: `make lint`

---

## License

[LICENSE](./LICENSE)