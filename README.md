# 🎬 DaVinci Director MCP

> **The Autonomous AI Video Director & Editor for DaVinci Resolve**  
> *Rhythm-synced cuts, algorithmic 3D LUT color grading, and hands-free Option C hybrid editing for Claude, Claude Code, Cursor, VS Code (Cline/Roo), OpenAI Codex, Antigravity, and any Model Context Protocol (MCP) client.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci%20Resolve-19%20%7C%2021-orange.svg)](https://www.blackmagicdesign.com/products/davinciresolve)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

---

## ⚡ Why DaVinci Director? (Feature Matrix)

Most existing DaVinci Resolve MCP servers are simple 1:1 API wrappers around Blackmagic's official Python API (`DaVinciResolveScript`). **They fail completely on DaVinci Resolve Free** (which locks external socket scripting behind the Studio paywall) and have zero creative editing intelligence.

**DaVinci Director** introduces **Option C (The Autonomous Hybrid)**: combining background API operations with Win32 ghost input, mathematical 3D LUT generation, and FCP 7 XML timeline synthesis.

| Capability | Basic API Wrappers | 🎬 DaVinci Director MCP |
| :--- | :---: | :---: |
| **DaVinci Resolve Free Compatibility** | ❌ Fails (Scripting paywalled) | ✅ **100% Fully Supported (Option C)** |
| **DaVinci Resolve Studio Compatibility** | ✅ Supported | ✅ **Supported** |
| **Audio Beat & Rhythm Detection** | ❌ None | ✅ **Automatic BPM, Onset Flux & Downbeats** |
| **Beat-Locked Timeline Assembly** | ❌ None | ✅ **1-Click 9:16 Vertical Reel Synthesis** |
| **Autonomous Color Grading** | ❌ None | ✅ **Algorithmic 33x33x33 .cube LUTs & ASC CDL** |
| **iPhone 10-bit HEVC Transcoding** | ❌ Shows "Media Offline" | ✅ **Hardware NVENC / VideoToolbox / CPU** |
| **Apple HEIC Photo Decoding** | ❌ Unsupported | ✅ **Lossless High-Res JPEG Conversion** |
| **Hands-Free Playback & Cutting** | ❌ API only | ✅ **Ghost Keystrokes (Ctrl+B, Space, Shift+Z)** |
| **Mouse Pointer Interference** | ⚠️ Hijacks Physical Mouse | ✅ **Zero Hijacking (Virtual AI Cursor Overlay)** |

---

## 🧠 Core Architecture (Option C: The Autonomous Hybrid)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               AI Clients (Claude Desktop, Claude Code, Cursor, VS Code, Antigravity)    │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ MCP Protocol (stdio / JSON-RPC)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               DaVinci Director MCP Server                              │
├───────────────────────┬────────────────────────┬───────────────────────────────────────┤
│  🎵 Audio Beat Finder │  🎨 3D Color Engine    │  💥 Dynamic Framing & Transitions     │
│  (BPM, Flux, Drops)   │  (.cube LUTs, ASC CDL) │  (Punch-in Zooms, Flash Transitions)  │
├───────────────────────┴────────────────────────┴───────────────────────────────────────┤
│                    ⚡ Smart Media Ingestion & Transcoder                                │
│                    (NVENC / VideoToolbox / CPU HEVC -> H.264 & HEIC -> JPG)            │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
┌───────────────────────────────────────┐       ┌───────────────────────────────────────┐
│   Native Support/LUT/Antigravity/     │       │   DaVinci Resolve 19 / 21 Engine      │
│   (Real-Time LUT System Directory)    │       │   (Timeline, Inspector, Color Page)   │
└───────────────────────────────────────┘       └───────────────────────────────────────┘
```

---

## 🚀 Key Superpowers

### 1. 🎵 Audio Beat & Rhythm Finder
* Evaluates spectral energy flux and autocorrelation across 65–175 BPM.
* Generates frame-accurate cut schedules:
  * `rapid`: 1-beat cuts for intense montage drops.
  * `standard`: 2-beat cuts (half-bars) for balanced pacing.
  * `bars`: 4-beat cuts for thematic scene transitions.
* Injects DaVinci timeline markers (cyan for downbeats, green for rhythm).

### 2. 🎨 Autonomous 3D LUT Color Engine
* Synthesizes mathematical $33 \times 33 \times 33$ `.cube` 3D LUT files and installs them directly into DaVinci Resolve's native directory:
  * **Windows:** `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\LUT\Antigravity\`
  * **macOS:** `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/Antigravity/`
  * **Linux:** `/opt/resolve/LUT/Antigravity/`
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

# Install dependencies in editable mode
pip install -e .
```

Or run directly with `uvx`:
```bash
uvx --from . davinci-director
```

---

## 🛠️ Step-by-Step Setup Guide for Any AI Tool

### 1. 🤖 Claude Desktop (macOS & Windows)
Open your Claude Desktop configuration file:
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the `davinci-director` server:
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
*(If using a virtual environment, replace `"python"` with the absolute path to your venv's python executable).*

---

### 2. 💻 Claude Code (Anthropic Official CLI)
Add the server with a single terminal command:
```bash
claude mcp add davinci-director -- python -m davinci_director.server
```

To verify:
```bash
claude mcp list
```

---

### 3. ⚡ Cursor IDE
1. Open Cursor and go to **Settings** (`Ctrl+,` or `Cmd+,`).
2. Navigate to **Features** > **MCP Servers**.
3. Click **Add New MCP Server**.
4. Fill in:
   * **Name:** `davinci-director`
   * **Type:** `command`
   * **Command:** `python -m davinci_director.server`

Or add directly to `.cursor/mcp.json`:
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

---

### 4. 📝 VS Code (Cline / Roo Code / Continue.dev)

#### Using Cline or Roo Code extension:
1. Open VS Code and click the Cline / Roo Code robot icon in the sidebar.
2. Click the **MCP Servers** (network/plugs) icon at the top.
3. Click **Configure MCP Servers** (or open `cline_mcp_settings.json`).
4. Paste the configuration:
```json
{
  "mcpServers": {
    "davinci-director": {
      "command": "python",
      "args": ["-m", "davinci_director.server"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### Using Continue.dev extension:
In `~/.continue/config.json`:
```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "davinci_director.server"]
        }
      }
    ]
  }
}
```

---

### 5. 🪐 Google Antigravity
In `~/.gemini/antigravity/mcp_config.json`:
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

### 6. 🌊 Windsurf / Zed Editor

#### Windsurf (Cascade):
In `~/.codeium/windsurf/mcp_config.json`:
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

#### Zed Editor:
In `~/.config/zed/settings.json`:
```json
{
  "experimental.mcp_servers": {
    "davinci-director": {
      "command": "python",
      "args": ["-m", "davinci_director.server"]
    }
  }
}
```

---

### 7. 🧠 OpenAI Codex / Custom Python AI Agents (LangChain, LlamaIndex, LiteLLM)
You can connect any custom Python LLM agent to `davinci-director` using the official `mcp` client library:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "davinci_director.server"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List all 21 available tools
            tools = await session.list_tools()
            print(f"Connected! Available tools: {len(tools.tools)}")
            
            # Autonomously build a beat-synced reel!
            result = await session.call_tool(
                "davinci_build_beat_synced_reel",
                arguments={
                    "timeline_name": "My_Epic_Reel",
                    "clip_paths": ["/path/to/shot1.mp4", "/path/to/shot2.mp4"],
                    "audio_path": "/path/to/music.wav",
                    "color_preset": "comic_noir",
                    "effects_style": "comic_dynamic"
                }
            )
            print(result)

asyncio.run(main())
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
| `davinci_seamless_click` | `x`, `y`, `label` | Localized click with AI badge, restores mouse pointer in <15ms. |
| `davinci_ai_cursor_move` | `x`, `y`, `label` | Displays virtual glowing AI cursor badge without moving mouse. |
| `davinci_ghost_click` | `x`, `y` | Dispatches background click message to DaVinci window. |
| `davinci_inspect_ui` | `x`, `y` | Captures micro-crop region and analyzes luminance telemetry. |

---

## 💬 Prompts to Try with Your AI Assistant

Once connected, you can give high-level creative instructions to your AI:

* *"Analyze the beat of `music.wav` and tell me the BPM and where the main drops happen."*
* *"Create a 15-second Spider-Man comic noir style vertical reel from the footage in my folder synced to `song.wav`."*
* *"Synthesize a Kodak 2383 3D LUT and apply it to my timeline."*
* *"Transcode all the raw iPhone footage in my downloads folder and import it into DaVinci Resolve."*
* *"Play the video in fullscreen and do a razor cut at the next drop."*

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
