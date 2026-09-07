"""
High-Performance Ingestion, Beat-Sync, and Proxy Transcode Engine for DaVinci Resolve
Option C (Autonomous Hybrid) Architecture
"""

import os
import sys
import time
import subprocess
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

from .beat_finder import beat_engine
from .color_engine import color_engine
from .scene_effects import scene_effects

is_windows = sys.platform == "win32"
if is_windows:
    import ctypes
    from ctypes import wintypes
    import win32gui
    import win32con
    user32 = ctypes.windll.user32
else:
    user32 = None
    win32gui = None
    win32con = None


def attach_desktop():
    if is_windows and user32:
        try:
            hdesk = user32.OpenInputDesktop(0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
        except Exception:
            pass


class ImportManager:
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg = ffmpeg_path or FFMPEG_EXE
        self._detect_hardware_encoder()
        attach_desktop()

    def _detect_hardware_encoder(self):
        """Detects best available H.264 video encoder on this system."""
        self.preferred_encoder = "libx264"
        try:
            res = subprocess.run([self.ffmpeg, "-encoders"], capture_output=True, text=True, timeout=5)
            encoders_text = res.stdout.lower()
            if "h264_nvenc" in encoders_text:
                self.preferred_encoder = "h264_nvenc"
            elif "h264_videotoolbox" in encoders_text:
                self.preferred_encoder = "h264_videotoolbox"
        except Exception:
            pass

    def inspect_file(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        info = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "ext": ext,
            "size_mb": round(size_mb, 2),
            "is_hevc": False,
            "is_heic": ext in [".heic", ".heif"],
            "needs_conversion": False
        }

        if ext in [".mov", ".mp4", ".m4v"]:
            try:
                with open(file_path, "rb") as f:
                    head = f.read(min(1024 * 1024, os.path.getsize(file_path)))
                    if b"hvc1" in head or b"hev1" in head:
                        info["is_hevc"] = True
                        info["needs_conversion"] = True
                    else:
                        f.seek(-min(os.path.getsize(file_path), 5 * 1024 * 1024), os.SEEK_END)
                        tail = f.read()
                        if b"hvc1" in tail or b"hev1" in tail:
                            info["is_hevc"] = True
                            info["needs_conversion"] = True
            except Exception:
                pass
        elif info["is_heic"]:
            info["needs_conversion"] = True

        return info

    def transcode_video(self, src: str, dst: str) -> bool:
        """Transcodes HEVC video to H.264 using detected GPU encoder or CPU fallback."""
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if self.preferred_encoder == "h264_nvenc":
            cmd = [self.ffmpeg, "-y", "-i", src, "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dst]
        elif self.preferred_encoder == "h264_videotoolbox":
            cmd = [self.ffmpeg, "-y", "-i", src, "-c:v", "h264_videotoolbox", "-q:v", "65", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dst]
        else:
            cmd = [self.ffmpeg, "-y", "-i", src, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dst]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            return res.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 0
        except Exception:
            return False

    def convert_heic_to_jpg(self, src: str, dst: str) -> bool:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            img = Image.open(src)
            img.save(dst, "JPEG", quality=95)
            return os.path.exists(dst)
        except Exception:
            cmd = [self.ffmpeg, "-y", "-i", src, "-q:v", "2", dst]
            res = subprocess.run(cmd, capture_output=True)
            return res.returncode == 0

    def optimize_folder(self, folder_path: str, output_subfolder: str = "optimized", max_videos: Optional[int] = None) -> List[str]:
        out_dir = os.path.join(folder_path, output_subfolder)
        os.makedirs(out_dir, exist_ok=True)

        valid_exts = {".mov", ".mp4", ".m4v", ".heic", ".heif", ".jpg", ".jpeg", ".png"}
        candidates = []
        for root, _, files in os.walk(folder_path):
            if output_subfolder in root:
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_exts:
                    candidates.append(os.path.join(root, f))

        ready_files = []
        video_count = 0

        for file_path in sorted(candidates):
            info = self.inspect_file(file_path)
            base_name = os.path.splitext(info["filename"])[0]

            if info["ext"] in [".mov", ".mp4", ".m4v"]:
                if max_videos and video_count >= max_videos:
                    continue

                if info["is_hevc"]:
                    dst = os.path.join(out_dir, f"{base_name}_h264.mp4")
                    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
                        if self.transcode_video(file_path, dst):
                            ready_files.append(dst)
                            video_count += 1
                    else:
                        ready_files.append(dst)
                        video_count += 1
                else:
                    ready_files.append(file_path)
                    video_count += 1

            elif info["is_heic"]:
                dst = os.path.join(out_dir, f"{base_name}.jpg")
                if not os.path.exists(dst) or os.path.getsize(dst) == 0:
                    if self.convert_heic_to_jpg(file_path, dst):
                        ready_files.append(dst)
                else:
                    ready_files.append(dst)
            else:
                ready_files.append(file_path)

        return ready_files

    def _inject_xml_to_resolve(self, xml_file: str, timeline_name: str, total_duration: int, clip_count: int, fps: int = 24) -> Dict[str, Any]:
        if not is_windows:
            return {"success": True, "method": "xml_exported", "xml_path": xml_file, "timeline_name": timeline_name, "note": "XML generated. Import via File > Import > Timeline on macOS/Linux."}

        attach_desktop()
        hwnds = []
        def enum_cb(h, lparam):
            if win32gui.IsWindowVisible(h):
                txt = win32gui.GetWindowText(h)
                if "davinci resolve" in txt.lower() and "preferences" not in txt.lower():
                    lparam.append(h)
            return True
        win32gui.EnumWindows(enum_cb, hwnds)
        if not hwnds:
            return {"success": False, "error": "DaVinci Resolve window not found."}

        davinci_hwnd = hwnds[0]
        user32.ShowWindow(davinci_hwnd, 3)
        user32.SetForegroundWindow(davinci_hwnd)
        time.sleep(0.3)

        # Ctrl + Shift + I
        user32.keybd_event(0x11, 0, 0, 0)
        user32.keybd_event(0x10, 0, 0, 0)
        user32.keybd_event(0x49, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x49, 0, 2, 0)
        user32.keybd_event(0x10, 0, 2, 0)
        user32.keybd_event(0x11, 0, 2, 0)
        time.sleep(1.0)

        dlg = win32gui.FindWindow(None, "Select files to import")
        if not dlg:
            return {"success": False, "error": "Select files to import dialog did not open."}

        edit_hwnd = win32gui.GetDlgItem(dlg, 1148)
        if not edit_hwnd:
            combo_ex = win32gui.FindWindowEx(dlg, 0, "ComboBoxEx32", None)
            if combo_ex:
                combo = win32gui.FindWindowEx(combo_ex, 0, "ComboBox", None)
                if combo:
                    edit_hwnd = win32gui.FindWindowEx(combo, 0, "Edit", None)

        if not edit_hwnd:
            return {"success": False, "error": "Edit control not found in import dialog."}

        win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, xml_file)
        time.sleep(0.3)
        btn_open = win32gui.GetDlgItem(dlg, 1)
        win32gui.SendMessage(btn_open, win32con.BM_CLICK, 0, 0)
        time.sleep(1.5)

        # Confirm Load XML
        fore = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(fore)
        ok_x = rect[2] - 85
        ok_y = rect[3] - 42
        user32.SetCursorPos(ok_x, ok_y)
        time.sleep(0.05)
        user32.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.03)
        user32.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(1.5)

        # Handle modal popup
        fore = user32.GetForegroundWindow()
        title = win32gui.GetWindowText(fore)
        if "message" in title.lower() or "input" in title.lower():
            user32.keybd_event(0x0D, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(0x0D, 2, 0, 0)
            time.sleep(1.0)

        # Shift + Z (Zoom to fit)
        user32.keybd_event(0x10, 0, 0, 0)
        user32.keybd_event(0x5A, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x5A, 0, 2, 0)
        user32.keybd_event(0x10, 0, 2, 0)

        return {
            "success": True,
            "timeline_name": timeline_name,
            "clip_count": clip_count,
            "duration_frames": total_duration,
            "duration_seconds": round(total_duration / fps, 2),
            "resolution": "1080x1920 (9:16 vertical)",
            "xml_path": xml_file
        }

    def inject_to_resolve_dialog(self, file_paths: List[str], chunk_size: int = 15) -> bool:
        if not file_paths or not is_windows:
            return False
        attach_desktop()

        for i in range(0, len(file_paths), chunk_size):
            batch = file_paths[i:i + chunk_size]
            hwnds = []
            def enum_cb(h, lparam):
                if win32gui.IsWindowVisible(h):
                    txt = win32gui.GetWindowText(h)
                    if "davinci resolve" in txt.lower() and "preferences" not in txt.lower():
                        lparam.append(h)
                return True
            win32gui.EnumWindows(enum_cb, hwnds)
            if not hwnds:
                return False

            davinci_hwnd = hwnds[0]
            user32.ShowWindow(davinci_hwnd, 3)
            user32.SetForegroundWindow(davinci_hwnd)
            time.sleep(0.3)

            user32.keybd_event(0x11, 0, 0, 0)
            user32.keybd_event(0x49, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(0x49, 0, 2, 0)
            user32.keybd_event(0x11, 0, 2, 0)
            time.sleep(1.0)

            dialog_hwnds = []
            def enum_dlg(h, lparam):
                if win32gui.IsWindowVisible(h):
                    cls = win32gui.GetClassName(h)
                    txt = win32gui.GetWindowText(h)
                    if cls == "#32770" and any(k in txt.lower() for k in ["open", "import", "select"]):
                        lparam.append(h)
                return True
            win32gui.EnumWindows(enum_dlg, dialog_hwnds)
            if not dialog_hwnds:
                return False

            dlg = dialog_hwnds[0]
            edit_hwnd = win32gui.GetDlgItem(dlg, 1148)
            if not edit_hwnd:
                combo_ex = win32gui.FindWindowEx(dlg, 0, "ComboBoxEx32", None)
                if combo_ex:
                    combo = win32gui.FindWindowEx(combo_ex, 0, "ComboBox", None)
                    if combo:
                        edit_hwnd = win32gui.FindWindowEx(combo, 0, "Edit", None)

            if not edit_hwnd:
                return False

            formatted_input = " ".join([f'"{p}"' for p in batch])
            win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, formatted_input)
            time.sleep(0.4)

            btn_open = win32gui.GetDlgItem(dlg, 1)
            if btn_open:
                win32gui.SendMessage(btn_open, win32con.BM_CLICK, 0, 0)
            else:
                win32gui.SendMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.SendMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

            time.sleep(1.2)

        return True

    def create_beat_synced_timeline_xml(
        self,
        timeline_name: str,
        clip_paths: List[str],
        audio_path: str,
        pacing: str = "standard",
        color_preset: Optional[str] = "comic_noir",
        effects_style: Optional[str] = "comic_dynamic",
        fps: float = 24.0
    ) -> Dict[str, Any]:
        valid_clips = [p for p in clip_paths if os.path.exists(p)]
        if not valid_clips:
            return {"success": False, "error": "No valid clips provided."}

        if not os.path.exists(audio_path):
            return {"success": False, "error": f"Audio file not found: {audio_path}"}

        analysis = beat_engine.analyze_track(audio_path, fps=fps)
        cut_schedule = beat_engine.generate_cut_schedule(audio_path, clip_count=len(valid_clips), pacing=pacing, fps=fps)
        total_duration = cut_schedule[-1][0] + cut_schedule[-1][1]

        punch_scales = scene_effects.calculate_punch_in_pattern(len(valid_clips), pattern=effects_style or "none") if effects_style != "none" else [100.0] * len(valid_clips)

        cdl_xml = ""
        if color_preset and color_preset != "none":
            cdl_xml = color_engine.get_cdl_xml_block(color_preset)
            try:
                color_engine.install_preset(color_preset)
            except Exception:
                pass

        fps_int = int(round(fps))
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE xmeml>',
            '<xmeml version="5">',
            '  <sequence id="sequence-1">',
            f'    <name>{timeline_name}</name>',
            f'    <duration>{total_duration}</duration>',
            '    <rate>',
            f'      <timebase>{fps_int}</timebase>',
            '      <ntsc>FALSE</ntsc>',
            '    </rate>',
            '    <timecode>',
            f'      <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
            '      <string>01:00:00:00</string>',
            '      <frame>86400</frame>',
            '    </timecode>',
            '    <media>',
            '      <video>',
            '        <format>',
            '          <samplecharacteristics>',
            f'            <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
            '            <width>1080</width>',
            '            <height>1920</height>',
            '            <pixelaspectratio>square</pixelaspectratio>',
            '          </samplecharacteristics>',
            '        </format>',
            '        <track>'
        ]

        for i, (fpath, (st_f, dur_f)) in enumerate(zip(valid_clips, cut_schedule), 1):
            fname = os.path.basename(fpath)
            url = "file://localhost/" + urllib.parse.quote(fpath.replace(chr(92), "/"), safe=":/")
            end_f = st_f + dur_f
            scale_val = punch_scales[i - 1] if i - 1 < len(punch_scales) else 100.0
            motion_filter = scene_effects.build_motion_filter_xml(scale=scale_val) if scale_val != 100.0 else ""

            clip_lines = [
                f'          <clipitem id="clipitem-v{i}">',
                f'            <name>{fname}</name>',
                f'            <duration>{dur_f}</duration>',
                f'            <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
                f'            <start>{st_f}</start>',
                f'            <end>{end_f}</end>',
                f'            <in>12</in>',
                f'            <out>{12 + dur_f}</out>',
                f'            <file id="file-{fname}">',
                f'              <name>{fname}</name>',
                f'              <pathurl>{url}</pathurl>',
                f'              <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
                f'              <duration>{dur_f + 500}</duration>',
                '              <media>',
                '                <video>',
                '                  <samplecharacteristics>',
                f'                    <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
                '                    <width>1080</width>',
                '                    <height>1920</height>',
                '                  </samplecharacteristics>',
                '                </video>',
                '              </media>',
                '            </file>'
            ]
            if cdl_xml:
                clip_lines.append(f'            {cdl_xml}')
            if motion_filter:
                clip_lines.append(motion_filter)
            clip_lines.append('          </clipitem>')
            xml_lines.extend(clip_lines)

        xml_lines.extend(['        </track>', '      </video>'])

        aname = os.path.basename(audio_path)
        a_url = "file://localhost/" + urllib.parse.quote(audio_path.replace(chr(92), "/"), safe=":/")
        xml_lines.extend([
            '      <audio>',
            '        <track>',
            '          <clipitem id="clipitem-a1">',
            f'            <name>{aname}</name>',
            f'            <duration>{total_duration}</duration>',
            f'            <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
            '            <start>0</start>',
            f'            <end>{total_duration}</end>',
            '            <in>0</in>',
            f'            <out>{total_duration}</out>',
            '            <file id="file-audio-1">',
            f'              <name>{aname}</name>',
            f'              <pathurl>{a_url}</pathurl>',
            f'              <rate><timebase>{fps_int}</timebase><ntsc>FALSE</ntsc></rate>',
            f'              <duration>{total_duration + 500}</duration>',
            '              <media><audio><samplecharacteristics><samplerate>48000</samplerate><depth>16</depth></samplecharacteristics></audio></media>',
            '            </file>',
            '          </clipitem>',
            '        </track>',
            '      </audio>'
        ])

        markers_xml = [
            f'    <marker><name>{m["name"]}</name><comment>{m["note"]}</comment><in>{m["frame"]}</in><out>{m["frame"]}</out></marker>'
            for m in analysis.get("davinci_markers", []) if m["frame"] <= total_duration
        ]
        xml_lines.extend(['    </media>', *markers_xml, '  </sequence>', '</xmeml>'])

        out_dir = os.path.dirname(valid_clips[0])
        xml_file = os.path.join(out_dir, f"{timeline_name.replace(' ', '_')}.xml")
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write("\n".join(xml_lines))

        res = self._inject_xml_to_resolve(xml_file, timeline_name, total_duration, len(valid_clips), fps=fps_int)
        res.update({"bpm": analysis["bpm"], "total_beats": analysis["total_beats"], "color_preset": color_preset, "effects_style": effects_style})
        return res


importer = ImportManager()
