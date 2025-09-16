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
   ```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with live cricket data
5. Submit a pull request

## License

[Your License Here]
