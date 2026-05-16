import logging
import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

from svp import SVP


def main():
    os.environ["QT_LOGGING_RULES"] = "qt.multimedia.ffmpeg*=false"
    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)

    folder_path = ""
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        folder_path = QDir.toNativeSeparators(os.path.abspath(folder))

    related_rows = 2
    related_previews_per_row = 3
    library_rows = 2
    library_previews_per_row = 4
    if len(sys.argv) == 6:
        related_rows = int(sys.argv[2])
        related_previews_per_row = int(sys.argv[3])
        library_rows = int(sys.argv[4])
        library_previews_per_row = int(sys.argv[5])

    logging.info(
        f"Using related grid={related_rows}x{related_previews_per_row} and library grid={library_rows}x{library_previews_per_row}"
    )

    window = SVP(
        folder_path,
        related_rows,
        related_previews_per_row,
        library_rows,
        library_previews_per_row,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
