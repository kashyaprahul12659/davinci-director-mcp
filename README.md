# DaVinci Director MCP

A Python MCP integration for AI-assisted DaVinci Resolve workflows: audio rhythm analysis, timeline preparation, LUT generation, and editor controls.

## Project at a glance

- **Interface:** MCP over stdio, with 21 registered tools in `src/davinci_director/server.py`.
- **Implementation:** NumPy audio-energy analysis, generated FCP XML, mathematical `.cube` LUTs, a native Resolve scripting bridge, and Windows UI helpers.
- **Examples:** [Beat-sync example](examples/demo_beat_sync.py) and [sample client configuration](examples/sample_client_configs.json).
- **License:** [MIT](LICENSE).

## Capabilities and boundaries

| Area | Implementation in this repository | Validation boundary |
| --- | --- | --- |
| Rhythm analysis | NumPy energy/positive-flux autocorrelation, beat grids, and marker suggestions | Tempo and bar positions are estimates, not guaranteed musical ground truth |
| Timeline preparation | Generated XML and clip scheduling | Verify imports, framing, transitions, and audio in the target Resolve version |
| Color presets | Generated 3D LUTs and CDL values | Creative approximations; preset names do not establish measured film-stock accuracy |
| Native editor operations | Resolve scripting bridge | Require an available native API connection; availability varies with the installed environment |
| UI fallback | Win32 input and cursor helpers | Windows-specific; this refresh did not validate macOS or Linux operation |

Edition-wide claims such as full support for every Free/Studio workflow are not established by the current validation evidence. Check `davinci_status` and the returned operation results for the actual environment.

## Installation

Python 3.10+ is declared in `pyproject.toml`. Clone the repository, create a virtual environment, then install with `python -m pip install -e .`. Windows UI helpers additionally use the `windows` extra: `python -m pip install -e ".[windows]"`.

A compatible MCP library, Resolve installation, and the media dependencies are required. The current server imports `MCPServer` from `mcp.server.mcpserver`; verify that this API exists in the installed MCP version before starting the server. The package currently does not pin a tested MCP version.

Start with `python -m davinci_director.server` or the `davinci-director` entry point. Configure an MCP client with that command using the client's documented stdio settings. See the sample configuration for examples; client configuration formats can change.

## Tool groups

- **Status and navigation:** `davinci_status`, `davinci_switch_page`, `davinci_set_vertical_resolution`.
- **Media:** `davinci_smart_ingest`, `davinci_import_audio`, `davinci_import_media`.
- **Projects and timelines:** `davinci_create_vertical_project`, `davinci_create_vertical_timeline`, `davinci_build_beat_synced_reel`.
- **Rhythm and markers:** `davinci_analyze_audio_beats`, `davinci_add_beat_marker`.
- **Color:** `davinci_generate_and_install_lut`, `davinci_list_luts`, `davinci_apply_lut`.
- **Framing and output:** `davinci_micro_adjust`, `davinci_render`.
- **UI helpers:** `davinci_transport`, `davinci_seamless_click`, `davinci_ai_cursor_move`, `davinci_ghost_click`, `davinci_inspect_ui`.

## Source structure

`beat_finder.py` handles rhythm analysis; `color_engine.py` generates LUTs; `import_manager.py` handles media and XML workflows; `resolve_bridge.py` wraps the native API; `ghost_input.py` and `ai_cursor_overlay.py` provide Windows interactions; `server.py` exposes MCP tools.

## Validation status

The documentation was checked against the source and registered-tool list on 29 October 2026. No Resolve timeline render, installation smoke test, or operating-system compatibility matrix was executed during that documentation review. A recorded end-to-end demo, pinned dependency validation, and automated tests remain useful next steps. Repository documentation should distinguish source capabilities from verified execution results.

## Portfolio context

This project demonstrates API integration, Python automation, media-processing workflows, and tool design. It is separate from any employer's systems or confidential data.

[GitHub profile](https://github.com/kashyaprahul12659) · [LinkedIn](https://www.linkedin.com/in/kashyaprahul535/)
