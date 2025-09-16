## Running the Front End (Live Web Scoreboard & Audio)

You can serve the live scoreboard and commentary audio web page using Python's built-in HTTP server. This allows you to view the live score and listen to commentary from any device on your network.

### Start the Front End Server

From the project root directory, run:

```sh
python -m http.server 8080 --bind 0.0.0.0
```

This will serve all files (including `score_live_stream.html` and audio) at [http://localhost:8080/](http://localhost:8080/).

### Open the Live Scoreboard

- On your computer: Open [http://localhost:8080/score_live_stream.html](http://localhost:8080/score_live_stream.html)
- On your mobile (same WiFi): Find your computer's IP (e.g., `192.168.1.10`) and open:
   ```
   http://<your-computer-ip>:8080/score_live_stream.html
   ```
   (Replace `<your-computer-ip>` with your actual IP address.)

The page will auto-refresh and play the latest Hindi commentary audio as soon as it's available.

# CricScore - Live Cricket Match Analysis (HTML-Based)

CricScore is a Python-based application that provides real-time cricket match analysis, including live score updates, commentary generation, and audio feedback. The application now crawls HTML directly from cricket websites instead of taking screenshots, making it faster and more reliable.

## Features

- **HTML-based data extraction** from cricket websites (no more screenshots!)
- Real-time score and commentary data crawling
- AI-powered commentary enhancement
- Text-to-speech conversion of commentary
- Automatic monitoring of match updates
- Support for multiple cricket match formats
- Faster processing and reduced resource usage

## Prerequisites

- Python 3.11 or higher
- Internet connection for web crawling
- Optional: CUDA-compatible GPU (for faster TTS processing)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd CricScore
```

2. Create and activate virtual environment:
```bash
python3.11 -m venv crickScore_venv
source crickScore_venv/bin/activate  # On macOS/Linux
# or
crickScore_venv\Scripts\activate  # On Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure the application:
   - Update the `config.properties` file with appropriate URLs and paths

## New Architecture (HTML-Based)

The application now uses HTML crawling instead of screenshot analysis:

### Core Components

1. **`getScoreHTML.py`** - Crawls live match scorecards from HTML
2. **`getCommentaryHTML.py`** - Crawls live match commentary from HTML  
3. **`score_data_processor.py`** - Processes and enhances score data
4. **`commentary_data_processor.py`** - Enhances commentary for better TTS
5. **`generateCommentry.py`** - Generates audio commentary from enhanced data
6. **`playCommentaryFiles.py`** - Handles audio playback

### Key Improvements

- ✅ **No more screenshots** - Direct HTML parsing
- ✅ **Faster processing** - No AI image analysis needed  
- ✅ **More reliable** - Less dependent on page layout changes
- ✅ **Better data extraction** - Structured HTML parsing
- ✅ **Reduced resource usage** - No image processing overhead

## Configuration

The `config.properties` file contains important settings:

```properties
[DEFAULT]
# Data folders
RESPONSE_FOLDER=/path/to/commentary/responses
AUDIO_FOLDER=/path/to/audio/files
SCORE_RESPONSE_FOLDER=/path/to/score/responses

# AI Model
MODEL_NAME=gemma3:4b

# URLs for cricket data
CMTRY_URL=https://www.cricbuzz.com/live-cricket-full-commentary/[match-id]
SCORE_URL=https://www.cricbuzz.com/live-cricket-scorecard/[match-id]
```

## Usage

### Quick Start (macOS/Linux)

1. Make the script executable and run:
```bash
chmod +x run_all.sh
./run_all.sh
```

### Quick Start (Windows)

1. Run the PowerShell script:
```powershell
.\start_all.ps1
```

### Manual Start

Start each component in separate terminals:

1. **Start score data crawling:**
```bash
python getScoreHTML.py
```

2. **Start commentary data crawling:**
```bash
python getCommentaryHTML.py
```

3. **Start data processors:**
```bash
python score_data_processor.py
python commentary_data_processor.py
```

4. **Generate and play commentary:**
```bash
python generateCommentry.py
python playCommentaryFiles.py
```

## Data Flow

```
Web Pages (HTML) → HTML Crawlers → JSON Data → Data Processors → Enhanced JSON → TTS → Audio → Playback
```

1. **HTML Crawlers** extract data from cricket websites
2. **Data Processors** enhance and structure the data
3. **TTS Generator** creates audio from enhanced commentary
4. **Audio Player** plays the generated commentary

## Directory Structure

```
CricScore/
├── config.properties
├── requirements.txt
├── run_all.sh / start_all.ps1
├── 
├── # HTML Crawlers
├── getScoreHTML.py
├── getCommentaryHTML.py
├── 
├── # Data Processors  
├── score_data_processor.py
├── commentary_data_processor.py
├── 
├── # Audio Generation & Playback
├── generateCommentry.py
├── playCommentaryFiles.py
├── 
├── # Data Storage
├── Resposes/
│   ├── *.json (commentary data)
│   └── audio-files/*.wav
└── Scores/
    └── Responses/*.json (score data)
```

## Dependencies

- **requests** - HTTP requests for web crawling
- **beautifulsoup4** - HTML parsing and data extraction
- **lxml** - Fast XML/HTML parser
- **torch** - PyTorch for TTS processing
- **TTS** - Text-to-speech conversion
- **watchdog** - File system monitoring
- **configparser** - Configuration management
- **simpleaudio** - Audio playback

## Troubleshooting

### Common Issues
1. **Import errors for bs4**: Install beautifulsoup4
   ```bash
   pip install beautifulsoup4

2. **Network timeouts**: Check internet connection and URL accessibility

3. **Audio not playing**: Ensure simpleaudio is properly installed

4. **Data not updating**: Check if URLs in config.properties are correct

### Logs and Monitoring

- Each component prints timestamped logs
- Monitor the console output for processing status
- Check JSON files in response folders for data structure

## Migration from Image-Based System

If migrating from the old screenshot-based system:

1. **Removed files** (no longer needed):
   - `getSSimages.py` 
   - `getScoreSSimages.py`
   - `image_infer_loop.py`
   - `score_image_infer_loop.py`

2. **New files** (HTML-based):
   - `getScoreHTML.py`
   - `getCommentaryHTML.py` 
   - `score_data_processor.py`
   - `commentary_data_processor.py`

3. **Updated configuration**: Remove image folders and add response folders

## CricScore Live Streaming

### Features
- Fetches and parses live cricket scorecard and commentary from Cricbuzz
- Translates latest ball commentary to Hindi using Ollama (gemma3:4b)
- Generates Hindi audio for latest ball using gTTS
- Plays audio as live commentary
- Dynamic web page for live score display and auto-refresh

### Requirements
- Python 3.9+
- Chrome browser and ChromeDriver (for Selenium)
- ffmpeg (for pydub audio conversion)
- See `requirements.txt` for Python packages

### Setup
1. Install Python packages:
   ```sh
   pip install -r requirements.txt
   ```
2. Install ffmpeg (for macOS):
   ```sh
   brew install ffmpeg
   ```
3. Ensure ChromeDriver matches your Chrome version and is in your PATH.

### Usage

#### Live Commentary & Audio
Run the live flow script (updates every 30s by default, configurable in `config.properties`):
```sh
python live_commentary_flow.py
```

#### Live Web Scoreboard
1. Start a local HTTP server:
   ```sh
   python -m http.server 8000
   ```
2. Open [http://localhost:8000/score_live_stream.html](http://localhost:8000/score_live_stream.html) in your browser.
   - The page auto-refreshes every 10 seconds and shows both teams, batsmen, bowlers, and a ball-by-ball ticker.

### Configuration
- Edit `config.properties` to set URLs, model, and update interval.

### Notes
- Ollama server must be running locally for translation.
- Audio playback uses gTTS (Google Text-to-Speech) and simpleaudio (via pydub conversion).
- For any CORS issues, always use the HTTP server to view HTML files.

### Folders
- `resource/score/` — Scorecard JSON
- `resource/cmtry/` — Commentary JSON
- `resource/cmtry-audio/` — Hindi commentary audio files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with live cricket data
5. Submit a pull request

## License

[Your License Here]
