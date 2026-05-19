# SVP: Smart Video Previewer

A hardware-accelerated desktop application built with Python, PySide6, and `mpv` to simultaneously preview multiple videos in a dynamic grid environment. It utilizes custom OpenGL widgets to render fluid previews, automatically skips through video timelines, and groups related files using automated filename prefix extraction.

https://github.com/user-attachments/assets/c3f97605-e6d6-4b95-853d-d7ca78b3576b

---

## Features

* **Smart Content Segmentation:**
    * **Library Grid:** Displays a randomized selection of videos from the target folder.
    * **Related Grid:** Groups and reveals files matching the prefix of the selected video.
* **Timeline Jump Cycles:** Automatically skips forward by 60 seconds every 10 seconds, providing an overview of video content over time.
* **Contextual Audio Hover:** Previews are muted by default. Hovering over a video for 2 seconds automatically unmutes its audio feed.
* **System Integration:** Double-clicking a preview or list item opens the file in an available player (via `startfile` on Windows, `VLC` on macOS, and `xdg-open` on Linux).
* **Multi-Stream OpenGL Rendering:** Uses native OpenGL bindings to draw hardware-accelerated video frames directly inside PySide6 widgets.

---

## Tech Stack

* **GUI Framework:** PySide6 (Qt for Python)
* **Video Back-end:** `mpv`
* **Rendering Engine:** OpenGL (via `QOpenGLWidget` & `MpvRenderContext`)

---

## Highlighted Interface Controls

* **↻ Restart:** Resets all active previews to the 0:00 timestamp.
* **▶▶ 1 min / 5 min:** Offsets all playing videos forward by the specified duration.
* **🎲 Randomize:** Refreshes the Library grid with a new random selection from the directory.
* **Prefix Dropdown:** Filters the side list to show only files belonging to a specific prefix.
* **Include Related Checkbox:** Toggles between random selection and chronological sequence for the "Related" panel.

---

## File Naming & Prefix Logic

The application uses regular expressions to calculate video relationships based on the directory's naming conventions.

### How Prefix Matching Works
The engine strips all **numerical digits**, **extensions**, and **trailing spaces** from a file's name to generate its structural "Prefix." This allows files sharing the same base alphabetical string to group together.
* `A1.mp4` → Prefix: `A`
* `A2.mp4` → Prefix: `A`
* `AB1.mov` → Prefix: `AB`
* `AB2.mp4` → Prefix: `AB`
* `B1.mov` → Prefix: `B`

### Natural Alphanumeric Sorting
The file manager uses a natural sorting algorithm. This makes it such that `Video2.mp4` appears before `Video10.mp4` in lists and "Related" match calculations.

---

## Installation

### Prerequisites
1.  **mpv Shared Library:** `mpv` must be installed.
    * E.g. on **macOS:** `brew install mpv`
2. **Video Player:** A supported video player must be available.
    * E.g. on **macOS**: VLC

### Setup
Clone the repository:

```
git clone https://github.com/m-maresch/svp
cd svp
```

Install dependencies in Python venv:

```
python -m venv .
source bin/activate
pip install PySide6 mpv
```

---

## Usage & CLI Arguments

Run the application from the terminal. You can optionally define the target folder and grid dimensions via positional arguments.

```bash
python main.py [folder_path] [related_rows] [related_cols] [library_rows] [library_cols]
```

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | String | *Prompt* | Path to the video folder. If omitted, a folder picker will open. |
| `related_rows` | Int | 2 | Number of rows for the **Related** panel. |
| `related_cols` | Int | 5 | Number of columns for the **Related** panel. |
| `library_rows` | Int | 2 | Number of rows for the **Library** panel. |
| `library_cols` | Int | 5 | Number of columns for the **Library** panel. |

**Note:** To use custom grid dimensions, you must provide all 5 arguments.

## Acknowledgments

This project was developed with the assistance of Google Gemini 3.

## Dependencies

Thanks to everyone contributing to any of the following projects:

- PySide6 (licensed under GPLv3)
- mpv (licensed under GPLv2 or later)

## License

This project is licensed under the GPLv3 License. See the LICENSE file for details.

SVP - Smart Video Previewer
Copyright (C) 2026  Maximilian Maresch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
