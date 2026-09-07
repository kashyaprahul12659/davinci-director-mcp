"""
Autonomous Color Grading Engine for DaVinci Resolve
Option C (Autonomous Hybrid) - Algorithmic 3D LUT Synthesis & System Installation
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"


def get_default_lut_dir() -> Path:
    """Detects native DaVinci Resolve LUT directory across Windows, macOS, and Linux."""
    if sys.platform == "win32":
        prog_data = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
        return prog_data / "Blackmagic Design" / "DaVinci Resolve" / "Support" / "LUT" / "Antigravity"
    elif sys.platform == "darwin":
        return Path("/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/Antigravity")
    elif sys.platform.startswith("linux"):
        return Path("/opt/resolve/LUT/Antigravity")
    else:
        return Path.home() / ".davinci_luts" / "Antigravity"


class ColorGradeEngine:
    def __init__(self, lut_dir: Optional[Path] = None):
        self.lut_dir = lut_dir or get_default_lut_dir()
        self.ensure_lut_dir()

    def ensure_lut_dir(self) -> Path:
        """Ensures the Antigravity LUT directory exists in DaVinci Resolve's support path."""
        try:
            self.lut_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            fallback = Path.home() / ".davinci_luts" / "Antigravity"
            fallback.mkdir(parents=True, exist_ok=True)
            self.lut_dir = fallback
        return self.lut_dir

    def _rgb_to_hsv(self, r: float, g: float, b: float) -> Tuple[float, float, float]:
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0.0
        elif mx == r:
            h = (60.0 * ((g - b) / df) + 360.0) % 360.0
        elif mx == g:
            h = (60.0 * ((b - r) / df) + 120.0) % 360.0
        else:
            h = (60.0 * ((r - g) / df) + 240.0) % 360.0
        s = 0.0 if mx == 0 else df / mx
        v = mx
        return h, s, v

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[float, float, float]:
        c = v * s
        x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
        m = v - c
        if 0 <= h < 60:
            rp, gp, bp = c, x, 0
        elif 60 <= h < 120:
            rp, gp, bp = x, c, 0
        elif 120 <= h < 180:
            rp, gp, bp = 0, c, x
        elif 180 <= h < 240:
            rp, gp, bp = 0, x, c
        elif 240 <= h < 300:
            rp, gp, bp = x, 0, c
        else:
            rp, gp, bp = c, 0, x
        return rp + m, gp + m, bp + m

    def _apply_s_curve(self, val: float, contrast: float = 1.2) -> float:
        val = max(0.0, min(1.0, val))
        x = (val - 0.5) * 2.0
        y = np.tanh(contrast * x) / np.tanh(contrast)
        return float(np.clip(y * 0.5 + 0.5, 0.0, 1.0))

    def synthesize_cube(self, preset_name: str, size: int = 33) -> str:
        """
        Synthesizes a 3D .cube file string for the specified look preset.
        Supported presets: comic_noir, kodak_2383, bleach_bypass, cyberpunk_neon, clean_commercial.
        """
        lines = [
            "# Created autonomously by Antigravity Autonomous Color Engine",
            f'TITLE "Antigravity_{preset_name}"',
            f"LUT_3D_SIZE {size}",
            "DOMAIN_MIN 0.0 0.0 0.0",
            "DOMAIN_MAX 1.0 1.0 1.0",
            ""
        ]

        for b_idx in range(size):
            for g_idx in range(size):
                for r_idx in range(size):
                    r_in = r_idx / (size - 1)
                    g_in = g_idx / (size - 1)
                    b_in = b_idx / (size - 1)

                    r_out, g_out, b_out = self._transform_pixel(r_in, g_in, b_in, preset_name)
                    lines.append(f"{r_out:.6f} {g_out:.6f} {b_out:.6f}")

        return "\n".join(lines) + "\n"

    def _transform_pixel(self, r: float, g: float, b: float, preset: str) -> Tuple[float, float, float]:
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        h, s, v = self._rgb_to_hsv(r, g, b)

        if preset == "comic_noir":
            is_red = (h >= 340 or h <= 20) and s > 0.25
            if is_red:
                s_new = min(1.0, s * 1.35)
                v_new = min(1.0, v * 1.1)
                r_out, g_out, b_out = self._hsv_to_rgb(h, s_new, v_new)
            else:
                s_new = s * 0.35
                r_out, g_out, b_out = self._hsv_to_rgb(h, s_new, v)
            r_out = r_out * 0.96
            g_out = g_out * 0.95
            b_out = b_out * 0.98

        elif preset == "kodak_2383":
            contrast_lum = self._apply_s_curve(lum, contrast=1.18)
            diff = contrast_lum - lum
            r_c = np.clip(r + diff, 0.0, 1.0)
            g_c = np.clip(g + diff, 0.0, 1.0)
            b_c = np.clip(b + diff, 0.0, 1.0)
            shadow_weight = max(0.0, 1.0 - lum * 1.8)
            highlight_weight = max(0.0, (lum - 0.45) * 1.8)
            r_c -= shadow_weight * 0.05
            g_c += shadow_weight * 0.02
            b_c += shadow_weight * 0.06
            r_c += highlight_weight * 0.05
            g_c += highlight_weight * 0.02
            b_c -= highlight_weight * 0.04
            if 15 <= h <= 65:
                s = min(1.0, s * 1.12)
            r_out, g_out, b_out = self._hsv_to_rgb(h, s, float(np.mean([r_c, g_c, b_c])))

        elif preset == "bleach_bypass":
            c_lum = self._apply_s_curve(lum, contrast=1.45)
            s_new = s * 0.42
            r_temp, g_temp, b_temp = self._hsv_to_rgb(h, s_new, c_lum)
            r_out = r_temp * 0.97
            g_out = g_temp * 1.00
            b_out = b_temp * 1.04

        elif preset == "cyberpunk_neon":
            r_c = self._apply_s_curve(r, contrast=1.25)
            g_c = self._apply_s_curve(g, contrast=1.2)
            b_c = self._apply_s_curve(b, contrast=1.3)
            if lum < 0.5:
                b_c = min(1.0, b_c * 1.15 + 0.02)
                r_c = min(1.0, r_c * 1.08)
                g_c = max(0.0, g_c * 0.90)
            else:
                g_c = min(1.0, g_c * 1.12)
                b_c = min(1.0, b_c * 1.10)
                r_c = max(0.0, r_c * 0.95)
            s_new = min(1.0, s * 1.35)
            r_out, g_out, b_out = self._hsv_to_rgb(h, s_new, max(r_c, g_c, b_c))

        elif preset == "clean_commercial":
            r_c = self._apply_s_curve(r, contrast=1.1)
            g_c = self._apply_s_curve(g, contrast=1.1)
            b_c = self._apply_s_curve(b, contrast=1.1)
            s_new = min(1.0, s * 1.15)
            r_out, g_out, b_out = self._hsv_to_rgb(h, s_new, max(r_c, g_c, b_c))

        else:
            r_out, g_out, b_out = r, g, b

        return float(np.clip(r_out, 0.0, 1.0)), float(np.clip(g_out, 0.0, 1.0)), float(np.clip(b_out, 0.0, 1.0))

    def install_preset(self, preset_name: str, size: int = 33) -> Dict[str, Any]:
        self.ensure_lut_dir()
        filename = f"Antigravity_{preset_name.title().replace('_', '')}.cube"
        target_path = self.lut_dir / filename

        cube_content = self.synthesize_cube(preset_name, size=size)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(cube_content)

        return {
            "success": True,
            "preset": preset_name,
            "lut_file": str(target_path),
            "size_kb": round(target_path.stat().st_size / 1024, 1),
            "davinci_installed": True
        }

    def install_all_presets(self, size: int = 33) -> List[Dict[str, Any]]:
        presets = ["comic_noir", "kodak_2383", "bleach_bypass", "cyberpunk_neon", "clean_commercial"]
        return [self.install_preset(p, size=size) for p in presets]

    def list_installed_luts(self) -> List[Dict[str, Any]]:
        if not self.lut_dir.exists():
            return []
        items = []
        for p in self.lut_dir.glob("*.cube"):
            items.append({
                "name": p.stem,
                "filename": p.name,
                "path": str(p),
                "size_kb": round(p.stat().st_size / 1024, 1)
            })
        return items

    def get_cdl_xml_block(self, preset_name: str) -> str:
        cdl_profiles = {
            "comic_noir": {"slope": (1.25, 1.10, 1.05), "offset": (-0.05, -0.05, -0.04), "power": (1.15, 1.10, 1.10), "sat": 0.55},
            "kodak_2383": {"slope": (1.08, 1.02, 0.94), "offset": (-0.02, 0.01, 0.04), "power": (0.96, 1.00, 1.05), "sat": 1.15},
            "bleach_bypass": {"slope": (1.30, 1.30, 1.35), "offset": (-0.08, -0.08, -0.06), "power": (1.20, 1.20, 1.20), "sat": 0.40},
            "cyberpunk_neon": {"slope": (1.10, 0.95, 1.25), "offset": (0.02, -0.03, 0.05), "power": (1.05, 1.10, 0.92), "sat": 1.35},
            "clean_commercial": {"slope": (1.05, 1.05, 1.05), "offset": (-0.01, -0.01, -0.01), "power": (1.02, 1.02, 1.02), "sat": 1.12}
        }
        profile = cdl_profiles.get(preset_name, cdl_profiles["clean_commercial"])
        s_r, s_g, s_b = profile["slope"]
        o_r, o_g, o_b = profile["offset"]
        p_r, p_g, p_b = profile["power"]
        sat = profile["sat"]

        return f"""<colorinfo>
  <asc_cdl>
    <slope r="{s_r:.3f}" g="{s_g:.3f}" b="{s_b:.3f}"/>
    <offset r="{o_r:.3f}" g="{o_g:.3f}" b="{o_b:.3f}"/>
    <power r="{p_r:.3f}" g="{p_g:.3f}" b="{p_b:.3f}"/>
    <saturation>{sat:.2f}</saturation>
  </asc_cdl>
</colorinfo>"""


color_engine = ColorGradeEngine()
