# SVP: Smart Video Previewer

A hardware-accelerated desktop application built with Python, PySide6, and `mpv` to simultaneously preview multiple videos in a dynamic grid. It provides browsing functionality, automatically skips through video timelines, and groups related files using filename prefix extraction.

https://github.com/user-attachments/assets/c3f97605-e6d6-4b95-853d-d7ca78b3576b

The previews above show recordings of a video from the [VisDrone-VID2019 dataset](https://github.com/VisDrone/VisDrone-Dataset) being processed by [VATE](https://github.com/m-maresch/vate).

## Features

* **Content Segmentation:**
    * **Library Grid:** Displays a randomized selection of videos from the target folder.
    * **Related Grid:** Groups and reveals files matching the prefix of the selected video.
* **Timeline Jump Cycles:** Automatically skips forward by 60 seconds every 10 seconds, providing an overview of video content over time.
* **Contextual Audio Hover:** Previews are muted by default. Hovering over a video for 2 seconds automatically unmutes its audio feed.
* **External Player Integration:** Double-clicking a preview or list item opens the file in an external player (using `VLC` on macOS/via `startfile` on Windows and `xdg-open` on Linux).
* **Multi-Stream Rendering:** Uses OpenGL to draw video frames from `mpv` directly inside PySide6 widgets.

## Highlighted Interface Controls

* **↻ Restart:** Resets all active previews to the 0:00 timestamp.
* **▶▶ 1 min / 5 min:** Offsets all playing videos forward by the specified duration.
* **🎲 Randomize:** Refreshes the grids with a new random selection from the directory.
* **Prefix Dropdown:** Filters the side list to show only files with a specific prefix.
* **Include Related Checkbox:** Toggles between random selection and ordered sequence for the "Related" grid.

## Tech Stack

* **Language:** Python
* **GUI Framework:** PySide6 (Qt for Python)
* **Video Back-End:** `mpv`

## Installation

### Prerequisites
`mpv` must be installed.
 * E.g. on **macOS:** `brew install mpv`

On **macOS**, VLC must be available for usage as an external player.

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

## Usage & CLI Arguments

Run the application from the terminal. You can optionally define the target folder and grid dimensions via positional arguments.

```
./svp.sh [folder_path] [related_rows] [related_cols] [library_rows] [library_cols]
```

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | String | *Prompt* | Path to the video folder. If omitted, a folder picker will open. |
| `related_rows` | Int | 2 | Number of rows for the **Related** grid. |
| `related_cols` | Int | 5 | Number of columns for the **Related** grid. |
| `library_rows` | Int | 2 | Number of rows for the **Library** grid. |
| `library_cols` | Int | 5 | Number of columns for the **Library** grid. |

## File Naming & Prefix Logic

The application uses regular expressions to calculate video relationships based on the directory's naming conventions.

### How Prefix Matching Works
SVP strips all digits and extensions from a file's name to generate its structural "prefix". This allows files sharing the same prefix to be grouped together.
* `A1.mp4` → Prefix: `A`
* `A2.mp4` → Prefix: `A`
* `AB1.mov` → Prefix: `AB`
* `AB2.mp4` → Prefix: `AB`
* `B1.mov` → Prefix: `B`

### Natural Sorting
SVP uses a natural sorting algorithm. This makes it such that `Video2.mp4` appears before `Video10.mp4` in lists and "Related" match calculations.

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
