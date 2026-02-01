<!-- 
-- +==== BEGIN AsperBackend =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: AsperBackend
-- FILE: README.md
-- CREATION DATE: 01-02-2026
-- LAST Modified: 5:58:1 01-02-2026
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: This is the README for the Wource script.
-- // AR
-- +==== END AsperBackend =================+
-->
# Wource

## Name

It is a combination of **Windows + Gource**

## Purpose

This project is a Proof of Concept (POC) using the latest available compiled Gource version for Windows (0.53) to provide a functional Git repository visualizer that works reliably on modern systems.

## Reason

Modern Linux builds of Gource often fail to run due to incompatibilities with newer OpenGL versions and graphics drivers. Specifically:

* Older Gource shaders rely on `ftransform()`, which no longer exists in modern OpenGL.

* Attempting to run Gource on Linux may produce errors such as:

  ```
  terminate called after throwing an instance of 'ShaderException'
    what():  vertex shader 'shadow' failed to compile:
  0:5(16): error: no function with name 'ftransform'
        2 | {
        3 |   gl_TexCoord[0] = gl_MultiTexCoord0;
        4 |   gl_FrontColor  = gl_Color;
  ->    5 |   gl_Position    = ftransform();
        6 | }

  Aborted (core dumped)
  ```

* Fixing this would require modifying Gource’s source code to replace deprecated shader functionality, which is non-trivial and may introduce regressions.

The motivation for this script is **not** that starting Gource under Wine is difficult. In fact, the Windows binary can be launched successfully with only a few commands.
The primary issue is that the native Linux version cannot run on modern systems without significant code alterations.

This script works around the problem by running the Windows Gource binary via Wine, which has proven stable.

## Features

* Uses the Windows Gource 0.53 binary via Wine.
* Automatically checks for required dependencies (Wine, Gource, FFmpeg).
* Optional video rendering via FFmpeg (PPM stream to MP4).
* FFmpeg does **not** need to be installed system-wide; static binaries available in `PATH` are sufficient.
* Supports custom resolutions, animation speed, and Wine desktop mode.
* Provides warnings for outdated Bash versions (Bash 4+ recommended).
* Defensive checks before execution to prevent partial or broken runs.
* Designed to be self-contained and easily distributable.

## Quick Start

Run the script from within a Git repository:

```bash
./wource.sh
```

Generate a video (MP4):

```bash
./wource.sh --video
```

Generate a video with a custom output file:

```bash
./wource.sh --video my_history.mp4
```

Set a custom resolution:

```bash
./wource.sh --resolution 1280x720
```

Control animation speed:

```bash
./wource.sh --seconds-per-day 0.1
```

Run inside a Wine virtual desktop:

```bash
./wource.sh --wine-desktop 1920x1080
```

Show the script’s help message:

```bash
./wource.sh --help
```

## Minimal Dependency Table

| Dependency            | Required | Notes                                                  |
| --------------------- | -------- | ------------------------------------------------------ |
| Bash ≥ 4.0            | Yes      | macOS default Bash (3.2) is insufficient               |
| Git                   | Yes      | Repository must be a valid Git repo                    |
| Wine                  | Yes      | Tested with Wine 10.0                                  |
| Gource (Windows) 0.53 | Yes      | Included for convenience                               |
| FFmpeg                | Optional | Required only for `--video`; static binaries supported |

## Usage

The script must be run from within a Git repository.
All required binaries are checked before execution.

### Command-line Options

* `--help`
  Shows the script’s help message and exits.

* `--video [file]`
  Enables video mode and generates an MP4 file using FFmpeg.
  If `[file]` is omitted, a default output name is used.

* `--resolution WxH`
  Sets the Gource viewport resolution (e.g. `1280x720`).

* `--seconds-per-day N`
  Controls animation speed (floating-point values supported).

* `--wine-desktop WxH`
  Runs Gource inside a Wine virtual desktop with the specified resolution.

* `--dry-run`
  Executes all checks and setup steps without launching Gource or FFmpeg.
  Log directories are still created to preserve logging behavior.

* `--author`
  Displays the script author and exits.

* `--version`
  Displays the script version and exits.

## Configuration and Overrides

### Default Configuration

For ease of distribution, the script is configured to run Gource from the same directory it is shipped with.
If you wish to install or use the script globally, you should edit the `GOURCE_DIR` variable in the script to point to your preferred Gource location.

### Runtime Overrides

The following environment variables are intended as **runtime overrides**, allowing temporary configuration changes without modifying the script:

* `OVERRIDE_GOURCE_BIN` — full path to a custom Gource binary
* `OVERRIDE_WINE_BIN` — full path to a custom Wine binary
* `OVERRIDE_FFMPEG_BIN` — full path to a custom FFmpeg binary

Example:

```bash
OVERRIDE_FFMPEG_BIN=/opt/ffmpeg/ffmpeg ./wource.sh --video
```

These overrides take precedence over the script’s configured defaults.

## FFmpeg Notes

* FFmpeg is only required when using `--video`.
* Static Linux FFmpeg binaries are fully supported.
* Video format, codec, and quality can be customized by editing the FFmpeg argument array in the script.

## Development / Contributing

Contributions are welcome.
However, note that this script lives inside a broader **“script repository”** — a collection of small utilities and experiments (finished and unfinished) developed over time.

This README exists primarily to document and introduce this specific script rather than to define a long-term standalone project.

## Distribution and Licensing

* For ease of distribution, a deflated copy of Gource 0.53 (Windows) is included.
* The author does **not** claim ownership of Gource or any of its code.
* All rights to Gource remain with its original authors.
* The only original work in this project is the `wource.sh` Bash script.

## Tested System Specifications

This script was developed and tested on:

* **OS**: Ubuntu 24.04.3 LTS (64-bit)
* **Desktop**: GNOME 46 (Wayland)
* **Kernel**: Linux 6.8.0-94-generic
* **Wine**: 10.0
* **Gource**: Windows 0.53

Other configurations may work, but these are the only tested conditions.

## Disclaimer

This script is provided **as-is**, without warranty of any kind.
Use at your own risk.

While defensive programming was applied, the script was written and tested in a single development session and may still contain bugs.
