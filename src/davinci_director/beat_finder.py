"""
Beat Finder & Rhythm Analysis Engine for DaVinci Resolve
Option C (Autonomous Hybrid) - Frame-Accurate Musical Synchronization
"""

import os
import sys
import wave
import subprocess
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"


class BeatFinder:
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg = ffmpeg_path or FFMPEG_EXE

    def _ensure_wav(self, audio_or_video_path: str) -> str:
        """Converts any audio or video file to a temporary 48kHz mono/stereo WAV for analysis."""
        ext = os.path.splitext(audio_or_video_path)[1].lower()
        if ext == ".wav":
            return audio_or_video_path

        wav_out = os.path.splitext(audio_or_video_path)[0] + "_temp_analysis.wav"
        if not os.path.exists(wav_out) or os.path.getsize(wav_out) == 0:
            cmd = [
                self.ffmpeg, "-y",
                "-i", audio_or_video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "48000",
                "-ac", "2",
                wav_out
            ]
            subprocess.run(cmd, capture_output=True, check=True)
        return wav_out

    def analyze_track(
        self,
        audio_path: str,
        fps: float = 24.0,
        max_duration_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyzes tempo (BPM), transient energy spikes, and generates 
        frame-locked cut markers for video editing at specified fps.
        """
        wav_path = self._ensure_wav(audio_path)

        with wave.open(wav_path, "rb") as w:
            nchannels = w.getnchannels()
            framerate = w.getframerate()
            total_frames = w.getnframes()
            dur = total_frames / float(framerate)

            read_seconds = min(dur, max_duration_seconds) if max_duration_seconds else dur
            read_frames = int(framerate * read_seconds)
            raw_data = w.readframes(read_frames)

        samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
        if nchannels == 2:
            samples = samples[::2]

        hop_size = 512
        num_hops = len(samples) // hop_size
        energy = np.zeros(num_hops, dtype=np.float32)
        for i in range(num_hops):
            chunk = samples[i * hop_size:(i + 1) * hop_size]
            energy[i] = np.sum(chunk ** 2)

        flux = np.diff(energy)
        flux = np.maximum(0, flux)

        corr = np.correlate(flux, flux, mode="full")
        corr = corr[len(corr) // 2:]

        min_lag = int(60.0 / 175.0 * (framerate / hop_size))
        max_lag = int(60.0 / 65.0 * (framerate / hop_size))
        search_range = corr[min_lag:max_lag]

        if len(search_range) > 0:
            best_lag = min_lag + int(np.argmax(search_range))
            detected_bpm = 60.0 / (best_lag * hop_size / framerate)
        else:
            detected_bpm = 120.0

        bpm = round(float(detected_bpm), 1)
        seconds_per_beat = 60.0 / bpm
        frames_per_beat = seconds_per_beat * fps
        total_video_frames = int(read_seconds * fps)

        first_window_frames = int(min(read_seconds, 2.5) * fps)
        samples_per_vframe = int(framerate / fps)
        frame_energy = []
        for f in range(first_window_frames):
            c = samples[f * samples_per_vframe:(f + 1) * samples_per_vframe]
            frame_energy.append(float(np.sqrt(np.mean(c ** 2))) if len(c) > 0 else 0.0)

        phase_offset_frame = int(np.argmax(frame_energy)) if frame_energy else 0
        if phase_offset_frame > frames_per_beat:
            phase_offset_frame = int(phase_offset_frame % frames_per_beat)

        beats = []
        downbeats = []
        cut_suggestions_standard = []
        cut_suggestions_rapid = []
        cut_suggestions_bars = []

        curr_frame_f = float(phase_offset_frame)
        beat_idx = 0
        bar_idx = 1

        while curr_frame_f < total_video_frames:
            f_int = int(round(curr_frame_f))
            sub_beat = (beat_idx % 4) + 1
            is_bar_start = (sub_beat == 1)

            beat_info = {
                "beat_index": beat_idx + 1,
                "bar": bar_idx,
                "sub_beat": sub_beat,
                "frame": f_int,
                "seconds": round(f_int / fps, 3),
                "is_downbeat": is_bar_start
            }
            beats.append(beat_info)

            cut_suggestions_rapid.append(f_int)
            if sub_beat in [1, 3]:
                cut_suggestions_standard.append(f_int)
            if is_bar_start:
                cut_suggestions_bars.append(f_int)
                downbeats.append(f_int)

            if sub_beat == 4:
                bar_idx += 1
            beat_idx += 1
            curr_frame_f += frames_per_beat

        davinci_markers = []
        for b in beats:
            if b["is_downbeat"]:
                davinci_markers.append({
                    "frame": b["frame"],
                    "color": "Cyan",
                    "name": f"Bar {b['bar']} Drop",
                    "note": f"Downbeat at {b['seconds']}s"
                })
            elif b["sub_beat"] == 3:
                davinci_markers.append({
                    "frame": b["frame"],
                    "color": "Green",
                    "name": f"Bar {b['bar']}.3",
                    "note": "Half-bar rhythm cut"
                })

        return {
            "success": True,
            "audio_file": os.path.basename(audio_path),
            "bpm": bpm,
            "fps": fps,
            "duration_seconds": round(read_seconds, 2),
            "total_video_frames": total_video_frames,
            "frames_per_beat": round(frames_per_beat, 2),
            "frames_per_bar": round(frames_per_beat * 4, 2),
            "phase_offset_frame": phase_offset_frame,
            "total_beats": len(beats),
            "total_bars": bar_idx,
            "cut_grids": {
                "rapid_1beat": cut_suggestions_rapid,
                "standard_2beats": cut_suggestions_standard,
                "bars_4beats": cut_suggestions_bars
            },
            "davinci_markers": davinci_markers
        }

    def generate_cut_schedule(
        self,
        audio_path: str,
        clip_count: int,
        pacing: str = "standard",
        fps: float = 24.0
    ) -> List[Tuple[int, int]]:
        analysis = self.analyze_track(audio_path, fps=fps)
        grids = analysis["cut_grids"]

        if pacing == "rapid":
            cut_points = grids["rapid_1beat"]
        elif pacing == "bars":
            cut_points = grids["bars_4beats"]
        else:
            cut_points = grids["standard_2beats"]

        schedule = []
        for i in range(clip_count):
            if i < len(cut_points) - 1:
                st = cut_points[i]
                dur = cut_points[i + 1] - cut_points[i]
            elif i < len(cut_points):
                st = cut_points[i]
                dur = int(round(analysis["frames_per_beat"] * 2))
            else:
                last_st = schedule[-1][0] + schedule[-1][1] if schedule else 0
                st = last_st
                dur = int(round(analysis["frames_per_beat"] * 2))
            schedule.append((st, max(1, dur)))

        return schedule


beat_engine = BeatFinder()
