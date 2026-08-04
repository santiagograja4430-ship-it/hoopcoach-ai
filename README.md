# # HoopCoach AI
<p align ="center">

![demo](IMAGES/Nombre.png)
    
</p>
<h2 align="center">
Computer vision tool that helps basketball players improve their shooting technique
</h2> 
<p>

Hi! We are Chanty_30 and Jerogonzax15, and we created **Hoop Coach AI** as a project for Hack Club’s Macondo program. My goal is to build a tool for basketball players to help them improve their performance and shooting mechanics.

You can find us on the Hack Club Slack as: `@Chanty_30` `@Jerogonzax15`

HoopCoach AI is a Python-based virtual basketball coach that uses Computer Vision and Artificial Intelligence to analyze basketball performance. The system captures real-time video through a webcam, detects and tracks the basketball using the YOLO object detection model, and analyzes its trajectory, speed, and movement to provide useful feedback during training sessions.
</p>

# libraries used

| Technology | Function  |
|------------|-----------------|
| Python |Main programming language |
| OpenCV | Video capture and image processing |
| MediaPipe  | Human pose detection |
| NumPy | Numerical computations |
| YOLO | Basketball detection and tracking |

## Download the program

You can download the executable version for Windows from the releases section:

[**Download HOOPCOACH-AI**](https://github.com/santiagograja4430-ship-it/hoopcoach-ai/releases/tag/v1.0.0)

### Usage Instructions

1. Download `HoopCoachAI-Windows-v1.0.zip`.
2. Extract the ZIP file.
3. Open the `HoopCoachAI` folder.
4. Run `HoopCoachAI.exe`.

> the executable must remain alongside the _internal folder and the other included files. If the folder is deleted, the executable will not work.
>
> # Installation

<h2>1. Clone the repository</h2>

```bash
git clone https://github.com/santiagograja4430-ship-it/hoopcoach-ai.git
```

<h2>2. Install the dependencies</h2>

```bash
pip install -r requirements.txt
```

<h2>3. Run the application</h2>

```bash
python App/main.py
```

# Current Status

HoopCoach AI can currently:

- Detect and track a basketball in real time using YOLO.
- Estimate the ball's speed.
- Draw the ball's trajectory.
- Display live camera analysis.
- Run as both a Python application and a Windows executable.

The project is still under development, and future versions will include:

- Basketball shooting form analysis.
- Automatic shooting feedback and recommendations.
- Shot angle and release analysis.
- Improved tracking accuracy.
- Performance statistics and training reports.

<p align="center">
    <img src="IMAGES/demo.png" width="500">
</p>

# License

This project was developed for educational purposes as part of Hack Club's Macondo program.
