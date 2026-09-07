# 🎬 DaVinci Director MCP

> **The Autonomous AI Video Director & Editor for DaVinci Resolve**  
> *Rhythm-synced cuts, algorithmic 3D LUT color grading, and hands-free Option C hybrid editing for Claude, Cursor, Antigravity, and any Model Context Protocol (MCP) client.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci%20Resolve-19%20%7C%2021-orange.svg)](https://www.blackmagicdesign.com/products/davinciresolve)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

---

## ⚡ Why DaVinci Director? (Feature Matrix)

Most existing DaVinci Resolve MCP servers are simple 1:1 API wrappers around Blackmagic's official Python API. **They fail completely on DaVinci Resolve Free** (which locks external socket scripting behind the Studio paywall) and have no creative intelligence.

**DaVinci Director** introduces **Option C (The Autonomous Hybrid)**: combining background API operations with Win32 ghost input, mathematical 3D LUT generation, and FCP 7 XML timeline synthesis.

| Capability | Basic API Wrappers | 🎬 DaVinci Director MCP |
| :--- | :---: | :---: |
| **DaVinci Resolve Free Compatibility** | ❌ Fails (Scripting locked) | ✅ **100% Fully Supported (Option C)** |
| **DaVinci Resolve Studio Compatibility** | ✅ Supported | ✅ **Supported** |
| **Audio Beat & Rhythm Detection** | ❌ None | ✅ **Automatic BPM, Onset Flux & Downbeats** |
| **Beat-Locked Timeline Assembly** | ❌ None | ✅ **1-Click 9:16 Vertical Reel Synthesis** |
| **Autonomous Color Grading** | ❌ None | ✅ **Algorithmic 33x33x33 .cube LUTs & ASC CDL** |
| **iPhone 10-bit HEVC Transcoding** | ❌ Shows "Media Offline" | ✅ **Hardware NVENC / VideoToolbox / CPU** |
| **Apple HEIC Photo Decoding** | ❌ Unsupported | ✅ **Lossless High-Res JPEG Conversion** |
| **Hands-Free Playback & Cutting** | ❌ API only | ✅ **Ghost Win32 Keystrokes (Ctrl+B, Space)** |
| **Mouse Pointer Interference** | ⚠️ Hijacks Physical Mouse | ✅ **Zero Hijacking (Virtual AI Cursor)** |

---

## 🧠 Core Architecture (Option C: The Autonomous Hybrid)

```
┌─────────────────────────────────────────────────────────────┐
│             AI Client (Claude / Cursor / Antigravity)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ MCP Protocol (stdio)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 DaVinci Director MCP Server                 │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Audio Beat     │  Color Grade    │  Scene Effects          │
│  Finder Engine  │  Engine         │  Engine                 │
│  (BPM & Drops)  │  (3D .cube LUT) │  (Zooms & Transitions)  │
├─────────────────┴─────────────────┴─────────────────────────┤
│                  Smart Media Ingest & Transcoder            │
│                  (NVENC HEVC -> H.264 / HEIC -> JPEG)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────────┐       ┌─────────────────────────┐
│   Native Support/LUT/     │       │   DaVinci Resolve 21    │
│   Antigravity System Dir  │       │   (Timeline, Inspector, │
│   (Real-Time LUT Gallery) │       │   Color Page, Playhead) │
└───────────────────────────┘       └─────────────────────────┘
```

---

## 🚀 Key Superpowers

### 1. 🎵 Audio Beat & Rhythm Finder
* Evaluates spectral energy flux and autocorrelation (65–175 BPM range).
* Generates frame-accurate cut schedules:
  * `rapid`: 1-beat cuts for intense montage drops.
  * `standard`: 2-beat cuts (half-bars) for balanced pacing.
  * `bars`: 4-beat cuts for thematic scene transitions.
* Injects DaVinci timeline markers (cyan for downbeats, green for rhythm).

### 2. 🎨 Autonomous 3D LUT Color Engine
* Synthesizes mathematical $33 \times 33 \times 33$ `.cube` 3D LUT files and installs them directly into DaVinci Resolve's native directory:
  * **Windows:** `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\LUT\Antigravity\`
  * **macOS:** `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/Antigravity/`
* Built-in Hollywood look profiles:
  * `comic_noir`: Spider-Man Comic Noir, deep crushed blacks, crimson/amber accents.
  * `kodak_2383`: Classic 2383 film print emulation, warm skin tones, teal shadows.
  * `bleach_bypass`: Gritty silver retention, 40% desaturation, crisp specular highlights.
  * `cyberpunk_neon`: Electric cyan & hot magenta split toning with deep navy shadows.
  * `clean_commercial`: Punchy vibrant commercial grade with neutral whites.
* Injects ASC CDL parameters (Slope, Offset, Power, Saturation) directly into timeline clips.

### 3. 💥 Dynamic Framing & Scene Effects
* Alternating sub-pixel camera punch-in scaling (`100%`, `118%`, `108%`, `125%`, `130%`) to eliminate static shots on vertical reels.
* Automatically schedules impact flash transitions (`Dip to White`) on major drops and `Cross Dissolve` on phrase boundaries.

### 4. ⚡ Hardware-Accelerated Ingest
* Automatically transcodes iPhone 10-bit HEVC (`hvc1`) footage (which shows as audio-only in DaVinci Free) into 8-bit Rec.709 H.264 using NVIDIA NVENC, Apple Silicon VideoToolbox, or CPU fallback.
* Converts Apple `.heic` photos to full-resolution JPEG.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Pooja/davinci-director-mcp.git
cd davinci-director-mcp

# Install dependencies
pip install -e .
```

Or run directly with `uvx`:
```bash
uvx --from . davinci-director
```

---

## 🛠️ MCP Client Configuration

### Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "davinci-director": {
      "command": "python",
      "args": ["-m", "davinci_director.server"]
    }
  }
}
```

### Cursor IDE
Add to your Cursor MCP settings:
```json
{
  "mcpServers": {
    "davinci-director": {
      "command": "python",
      "args": ["-m", "davinci_director.server"]
    }
  }
}
```

### Google Antigravity
Add to `~/.gemini/antigravity/mcp_config.json`:
```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "python",
      "args": ["-m", "davinci_director.server"]
    }
  }
}
```

---

## 🧰 Available MCP Tools (21 Tools)

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `davinci_status` | - | Returns DaVinci window state, active project, and API connection. |
| `davinci_analyze_audio_beats` | `audio_path`, `fps`, `max_duration_seconds` | Detects BPM, downbeats, bars, and frame cut points. |
| `davinci_build_beat_synced_reel` | `timeline_name`, `clip_paths`, `audio_path`, `pacing`, `color_preset`, `effects_style` | Autonomously assembles beat-synced 9:16 vertical reel with color and motion. |
| `davinci_generate_and_install_lut` | `preset_name`, `size` | Synthesizes and installs 3D `.cube` LUTs in DaVinci's system LUT directory. |
| `davinci_list_luts` | - | Lists custom Antigravity LUTs installed in DaVinci Resolve. |
| `davinci_smart_ingest` | `folder_path`, `max_videos` | GPU NVENC transcoding for HEVC + HEIC conversion + batch import. |
| `davinci_import_audio` | `path_or_url`, `destination_folder` | Imports audio or downloads YouTube URL audio as 48kHz WAV. |
| `davinci_create_vertical_project`| `project_name`, `fps` | Configures 1080x1920 @ 24fps project settings. |
| `davinci_create_vertical_timeline`| `timeline_name`, `clip_names` | Assembles vertical timeline from Media Pool clips. |
| `davinci_micro_adjust` | `clip_index`, `zoom`, `pan_x`, `pan_y` | Sub-pixel framing and camera adjustments. |
| `davinci_transport` | `action` ('play', 'cut', 'zoom_fit', 'fullscreen') | Dispatches background playback and cutting shortcuts. |
| `davinci_switch_page` | `page` ('edit', 'color', 'cut', 'media') | Switches DaVinci Resolve workspace page. |
| `davinci_apply_lut` | `clip_index`, `lut_path` | Deploys look preset or applies LUT to clip node. |
| `davinci_add_beat_marker` | `frame`, `color`, `note` | Injects timeline ruler marker at specific frame. |
| `davinci_render` | `output_dir`, `filename` | Triggers 1080x1920 MP4 timeline export. |

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
