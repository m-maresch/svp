import random

import cv2

from player import open_with_mpv


class VideoMixer:
    def __init__(self, sample, base_duration, spread_duration):
        self.sample = sample
        self.base_duration = base_duration
        self.spread_duration = spread_duration

    def mix(self, files):
        video_segments = []
        if self.sample:
            start = _video_start_times(files, self.base_duration)
            min_duration = max(0, self.base_duration - self.spread_duration)
            max_duration = self.base_duration + self.spread_duration
            for idx, file_path in enumerate(files):
                selected_duration = random.randint(min_duration, max_duration)
                duration = min(selected_duration, _video_duration_sec(file_path))
                video_segments.append((file_path, start[idx], duration))
        else:
            for file_path in files:
                video_segments.append((file_path, 0.0, _video_duration_sec(file_path)))

        if not video_segments:
            return

        edl_entries = []
        for file_path, start_sec, duration_sec in video_segments:
            edl_entries.append(f"{file_path},{start_sec},{duration_sec}")

        edl_uri = "edl://" + ";".join(edl_entries)
        open_with_mpv(edl_uri)


def _video_duration_sec(file: str) -> float:
    video = cv2.VideoCapture(file)
    if not video.isOpened():
        return 0.0
    duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
    video.release()
    return duration


def _video_start_times(files, base_duration):
    total_files = len(files)
    if total_files == 0:
        return []

    start_times = []
    for i, file in enumerate(files):
        length = _video_duration_sec(file)
        if length <= base_duration:
            start_times.append(0.0)
            continue

        fraction = 0.0 if total_files == 1 else i / (total_files - 1)
        max_start = length - base_duration
        start_time = fraction * max_start

        start_times.append(round(start_time, 2))

    return start_times
