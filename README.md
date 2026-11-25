# VidClean

Local, calibrated reverse compositing for video overlays. No cloud service, API key or AI model required. MIT licensed.

**Supported profile:** original Google Vids portrait exports, 1080 × 1920, with the same fixed overlay as the calibration sample. Other layouts, landscape, rotated or resized footage are not supported. The tool does not automatically detect overlays. Use only on footage you are authorized to modify; retain required provenance disclosures. Not affiliated with Google or Erasio.

## Install

Download the repository ZIP from GitHub (Code → Download ZIP), extract it, and open a terminal in the extracted folder. Keep `profile.bin` next to `vid_clean.py`.

### macOS (Apple Silicon and Intel)

Install Homebrew from https://brew.sh if needed. On Apple Silicon use a native ARM64 terminal (`uname -m` should say `arm64`); Homebrew normally lives in `/opt/homebrew`. On Intel it normally lives in `/usr/local`. Follow Homebrew's shell setup instructions.

```sh
brew install python@3.12 ffmpeg
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python vid_clean.py --help
```

### Windows 10/11 (PowerShell)

Install Python and FFmpeg using Windows Package Manager:

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id Gyan.FFmpeg
```

Close and reopen PowerShell, navigate to the extracted folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe vid_clean.py --help
```

No PowerShell execution policy change is necessary. If winget is unavailable, install Python from https://python.org and FFmpeg from https://ffmpeg.org/download.html and add FFmpeg's bin folder to PATH.

## Use

On macOS with the environment activated:

```sh
python vid_clean.py "input.mp4" --preview
python vid_clean.py "input.mp4" --preview --frame 100 --overwrite
python vid_clean.py "input.mp4" "clean.mp4"
```

On Windows:

```powershell
.\.venv\Scripts\python.exe vid_clean.py "input.mp4" --preview
.\.venv\Scripts\python.exe vid_clean.py "input.mp4" "clean.mp4"
```

Default output is `input_v3.mp4`; preview writes `input_v3.png`. Frame numbers start at zero. Use `--overwrite` only when replacing an existing output is intended. Original input is never intentionally overwritten. Use full quoted paths for files outside the repository. Preview first to verify the overlay matches the profile.

## How it works

The bundled binary profile contains a 90 × 90 × 4 little-endian float32 array: one fitted slope and three BGR offsets per pixel. The correction applies `(observed - offset) / slope` to the region x=855:945, y=1695:1785. The coefficients were independently fitted from paired original and processed footage; no third-party source code or original footage is bundled. This is an empirical inverse compositing approximation, not guaranteed lossless recovery. Video is re-encoded as H.264 and audio is stream-copied. Constant-frame-rate footage is recommended; variable frame timing and other metadata are not preserved reliably. Audio incompatible with MP4 may fail to mux.

## Troubleshooting

- Missing ffmpeg/ffprobe: run `ffmpeg -version` and `ffprobe -version`; ensure both are on PATH.
- Missing cv2 or numpy: install requirements using the same Python interpreter used to launch the script.
- Output exists: choose a different output or use `--overwrite`.
- Wrong resolution or visible artifacts: the bundled profile is not suitable for that export. Do not resize to force a match.
- Failed encoding: delete any incomplete output before retrying.

## License and contributions

MIT for the project code and bundled calibration data, subject to the publisher having rights to distribute them. Dependencies have their own licenses and are not bundled. Issues and pull requests welcome; do not upload private footage to public issues. Platform instructions target macOS Intel/Apple Silicon and Windows x64; native platform testing is still needed.
