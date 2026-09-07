"""
Standalone Demo Script for DaVinci Director
Demonstrates:
1. Algorithmic 3D LUT generation and system directory deployment.
2. Music beat detection and cut grid calculation.
"""

import sys
import os
from pathlib import Path

# Add src to path if running directly from repo
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from davinci_director.color_engine import color_engine
from davinci_director.beat_finder import beat_engine
from davinci_director.scene_effects import scene_effects


def run_demo():
    print("=" * 60)
    print("DaVinci Director - Standalone Feature Demo")
    print("=" * 60)

    # 1. Color Grading Demonstration
    print("\n1. Synthesizing Cinematic 3D LUTs...")
    results = color_engine.install_all_presets(size=33)
    for r in results:
        print(f" -> Installed '{r['preset']}': {r['lut_file']} ({r['size_kb']} KB)")

    print(f"\nDaVinci System LUT Location: {color_engine.lut_dir}")
    print(f"Total LUTs Deployed: {len(color_engine.list_installed_luts())}")

    # 2. Scene Effects Demonstration
    print("\n2. Rhythmic Punch-in Scaling Pattern (8 shots):")
    scales = scene_effects.calculate_punch_in_pattern(8, pattern="comic_dynamic")
    for i, s in enumerate(scales, 1):
        print(f"  Shot {i}: {s}% scale")

    # 3. Beat Finder Demonstration
    print("\n3. Testing Audio Beat Detection:")
    test_audio = sys.argv[1] if len(sys.argv) > 1 else None
    if test_audio and os.path.exists(test_audio):
        analysis = beat_engine.analyze_track(test_audio, fps=24.0, max_duration_seconds=15.0)
        print(f"  File: {analysis['audio_file']}")
        print(f"  Detected BPM: {analysis['bpm']}")
        print(f"  Frames per Beat: {analysis['frames_per_beat']}")
        print(f"  Total Markers Generated: {len(analysis['davinci_markers'])}")
        print(f"  Cut Schedule (first 5 cuts): {analysis['cut_grids']['standard_2beats'][:5]}")
    else:
        print("  Pass a WAV/MP3 file path as an argument to test beat detection on your own audio:")
        print("  python demo_beat_sync.py path/to/song.wav")

    print("\n" + "=" * 60)
    print("Demo Complete! Ready for DaVinci Resolve Autonomous Editing.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
