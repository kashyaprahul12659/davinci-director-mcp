"""
DaVinci Resolve Python Bridge
Auto-discovers and connects to DaVinci Resolve's native scripting engine across Windows, macOS, and Linux.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


def auto_configure_resolve_paths():
    """Detects and configures DaVinci Resolve environment variables automatically."""
    if sys.platform == "win32":
        api_path = os.environ.get("RESOLVE_SCRIPT_API", r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting")
        lib_path = os.environ.get("RESOLVE_SCRIPT_LIB", r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll")
    elif sys.platform == "darwin":
        api_path = os.environ.get("RESOLVE_SCRIPT_API", "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting")
        lib_path = os.environ.get("RESOLVE_SCRIPT_LIB", "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")
    else:
        api_path = os.environ.get("RESOLVE_SCRIPT_API", "/opt/resolve/Developer/Scripting")
        lib_path = os.environ.get("RESOLVE_SCRIPT_LIB", "/opt/resolve/libs/Fusion/fusionscript.so")

    os.environ["RESOLVE_SCRIPT_API"] = api_path
    os.environ["RESOLVE_SCRIPT_LIB"] = lib_path

    modules_path = os.path.join(api_path, "Modules")
    if os.path.exists(modules_path) and modules_path not in sys.path:
        sys.path.append(modules_path)


auto_configure_resolve_paths()

try:
    import DaVinciResolveScript as dvr_script
except ImportError:
    dvr_script = None


class DaVinciBridge:
    def __init__(self):
        self.resolve = None
        self.project_manager = None
        self.current_project = None

    def connect(self) -> bool:
        if dvr_script is None:
            return False
        try:
            self.resolve = dvr_script.scriptapp("Resolve")
            if self.resolve is not None:
                self.project_manager = self.resolve.GetProjectManager()
                self.current_project = self.project_manager.GetCurrentProject()
                return True
            return False
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        if not self.connect():
            return {
                "connected": False,
                "message": (
                    "DaVinci Resolve scripting is not connected. "
                    "(Note: DaVinci Resolve Free disables external socket scripting; "
                    "Option C Autonomous Hybrid features operate independently)."
                )
            }

        version = self.resolve.GetVersionString()
        product_name = self.resolve.GetProductName()
        project_name = self.current_project.GetName() if self.current_project else "No active project"

        timeline_info = None
        if self.current_project:
            timeline = self.current_project.GetCurrentTimeline()
            if timeline:
                timeline_info = {
                    "name": timeline.GetName(),
                    "duration_frames": timeline.GetEndFrame() - timeline.GetStartFrame(),
                    "tracks": {
                        "video": timeline.GetTrackCount("video"),
                        "audio": timeline.GetTrackCount("audio")
                    }
                }

        return {
            "connected": True,
            "product": product_name,
            "version": version,
            "active_project": project_name,
            "active_timeline": timeline_info
        }

    def create_vertical_project(self, project_name: str, fps: int = 24) -> Dict[str, Any]:
        if not self.connect() or not self.project_manager:
            return {"success": False, "error": "DaVinci Resolve scripting not connected."}

        project = self.project_manager.CreateProject(project_name)
        if not project:
            project = self.project_manager.LoadProject(project_name)

        if not project:
            return {"success": False, "error": f"Could not create or load project '{project_name}'."}

        self.current_project = project
        project.SetSetting("timelineResolutionWidth", "1080")
        project.SetSetting("timelineResolutionHeight", "1920")
        project.SetSetting("timelineFrameRate", str(fps))

        return {
            "success": True,
            "project_name": project_name,
            "resolution": "1080x1920 (9:16 vertical)",
            "framerate": f"{fps}fps"
        }

    def import_media(self, file_paths: List[str], bin_name: str = "Footage") -> Dict[str, Any]:
        if not self.connect() or not self.project_manager.GetCurrentProject():
            return {"success": False, "error": "No active project."}

        project = self.project_manager.GetCurrentProject()
        media_pool = project.GetMediaPool()
        root_folder = media_pool.GetRootFolder()

        target_folder = None
        for folder in root_folder.GetSubFolderList() or []:
            if folder.GetName() == bin_name:
                target_folder = folder
                break
        if not target_folder:
            target_folder = media_pool.AddSubFolder(root_folder, bin_name)

        media_pool.SetCurrentFolder(target_folder)
        imported_clips = media_pool.ImportMedia(file_paths)

        return {
            "success": bool(imported_clips),
            "imported_count": len(imported_clips) if imported_clips else 0,
            "bin": bin_name
        }

    def create_timeline_from_clips(self, timeline_name: str, clip_names: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.connect() or not self.project_manager.GetCurrentProject():
            return {"success": False, "error": "No active project."}

        project = self.project_manager.GetCurrentProject()
        media_pool = project.GetMediaPool()
        root_folder = media_pool.GetRootFolder()

        clips_to_add = []
        def gather_clips(folder):
            for clip in folder.GetClipList() or []:
                if not clip_names or clip.GetName() in clip_names:
                    clips_to_add.append(clip)
            for sub in folder.GetSubFolderList() or []:
                gather_clips(sub)

        gather_clips(root_folder)
        if not clips_to_add:
            return {"success": False, "error": "No matching clips found in Media Pool."}

        timeline = media_pool.CreateTimelineFromClips(timeline_name, clips_to_add)
        if not timeline:
            return {"success": False, "error": f"Failed to create timeline '{timeline_name}'."}

        project.SetCurrentTimeline(timeline)
        return {
            "success": True,
            "timeline_name": timeline_name,
            "clip_count": len(clips_to_add),
            "resolution": f"{project.GetSetting('timelineResolutionWidth')}x{project.GetSetting('timelineResolutionHeight')}"
        }

    def micro_adjust_clip(
        self,
        clip_index: int,
        zoom: Optional[float] = None,
        pan_x: Optional[float] = None,
        pan_y: Optional[float] = None,
        rotation: Optional[float] = None,
        opacity: Optional[float] = None
    ) -> Dict[str, Any]:
        if not self.connect() or not self.project_manager.GetCurrentProject():
            return {"success": False, "error": "No active project."}

        timeline = self.project_manager.GetCurrentProject().GetCurrentTimeline()
        if not timeline:
            return {"success": False, "error": "No active timeline."}

        items = timeline.GetItemListInTrack("video", 1) or []
        if not (1 <= clip_index <= len(items)):
            return {"success": False, "error": f"Clip index {clip_index} out of range."}

        item = items[clip_index - 1]
        adjustments = {}
        if zoom is not None:
            item.SetProperty("ZoomX", zoom)
            item.SetProperty("ZoomY", zoom)
            adjustments["zoom"] = zoom
        if pan_x is not None:
            item.SetProperty("Pan", pan_x)
            adjustments["pan_x"] = pan_x
        if pan_y is not None:
            item.SetProperty("Tilt", pan_y)
            adjustments["pan_y"] = pan_y
        if rotation is not None:
            item.SetProperty("RotationAngle", rotation)
            adjustments["rotation"] = rotation
        if opacity is not None:
            item.SetProperty("Opacity", opacity)
            adjustments["opacity"] = opacity

        return {"success": True, "clip_index": clip_index, "clip_name": item.GetName(), "adjustments": adjustments}

    def add_marker(self, frame_number: int, color: str = "Blue", name: str = "Beat", note: str = "") -> Dict[str, Any]:
        if not self.connect() or not self.project_manager.GetCurrentProject():
            return {"success": False, "error": "No active project."}
        timeline = self.project_manager.GetCurrentProject().GetCurrentTimeline()
        if not timeline:
            return {"success": False, "error": "No active timeline."}
        success = timeline.AddMarker(frame_number, color, name, note, 1.0, "")
        return {"success": success, "frame": frame_number, "color": color, "name": name, "note": note}

    def apply_lut(self, clip_index: int, lut_path: str, node_index: int = 1) -> Dict[str, Any]:
        if not self.connect() or not self.project_manager.GetCurrentProject():
            return {"success": False, "error": "No active project."}
        timeline = self.project_manager.GetCurrentProject().GetCurrentTimeline()
        if not timeline:
            return {"success": False, "error": "No active timeline."}
        items = timeline.GetItemListInTrack("video", 1) or []
        if not (1 <= clip_index <= len(items)):
            return {"success": False, "error": f"Clip index {clip_index} out of range."}
        item = items[clip_index - 1]
        success = item.SetLUT(node_index, lut_path)
        return {"success": success, "clip_name": item.GetName(), "node_index": node_index, "lut_path": lut_path}

    def render_timeline(self, target_dir: str, custom_name: str) -> Dict[str, Any]:
        if not self.connect() or not self.project_manager.GetCurrentProject():
            return {"success": False, "error": "No active project."}
        project = self.project_manager.GetCurrentProject()
        project.SetRenderSettings({"TargetDir": target_dir, "CustomName": custom_name, "ExportVideo": True, "ExportAudio": True})
        job_id = project.AddRenderJob()
        if not job_id:
            return {"success": False, "error": "Failed to add render job."}
        project.StartRendering(job_id)
        return {"success": True, "job_id": job_id, "target_file": os.path.join(target_dir, f"{custom_name}.mp4")}


bridge = DaVinciBridge()
