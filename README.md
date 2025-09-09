# CricScore - Live Cricket Match Analysis

CricScore is a Python-based application that provides real-time cricket match analysis, including live score updates, commentary generation, and audio feedback. The application captures match data from live cricket websites, processes it using AI models, and generates audio commentary.

## Features

- Live score capture from cricket websites
- Real-time image-based score analysis
- AI-powered commentary generation
- Text-to-speech conversion of commentary
- Automatic monitoring of match updates
- Support for multiple cricket match formats

## Prerequisites

- Python 3.11 or higher
- Chrome WebDriver (for Selenium)
- CUDA-compatible GPU (optional, for faster processing)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd CricScore
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure the application:
   - Update the `config.properties` file with appropriate paths and URLs
   - Ensure the Chrome WebDriver is installed for Selenium

## Project Structure

- `config.properties` - Configuration settings for URLs, paths, and model parameters
- `generateCommentry.py` - Generates audio commentary from match data
- `getSSimages.py` - Captures screenshots of live match commentary
- `getScoreSSimages.py` - Captures screenshots of live match scorecards
- `image_infer_loop.py` - Processes captured images for commentary generation
- `score_image_infer_loop.py` - Analyzes scorecard images for match statistics
- `playCommentaryFiles.py` - Handles audio playback of generated commentary

## Configuration

The `config.properties` file contains important settings:

```properties
[DEFAULT]
IMAGE_FOLDER - Directory for storing captured images
RESPONSE_FOLDER - Directory for processed JSON responses
AUDIO_FOLDER - Directory for generated audio files
MODEL_NAME - AI model name (default: gemma3:4b)
CMTRY_URL - URL for live cricket commentary
SCORE_URL - URL for live cricket scorecard
```

## Usage

### Quick Start (Windows)

To start all components in separate terminals with the virtual environment:

1. First, ensure you have created and set up your virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the PowerShell script:
```powershell
.\start_all.ps1
```

This will open separate terminal windows for each component, each running in the virtual environment.

### Manual Start

1. Start the score capture:
```bash
python getScoreSSimages.py
```

2. Start the commentary capture:
```bash
python getSSimages.py
```

3. Start the image analysis:
```bash
python score_image_infer_loop.py
python image_infer_loop.py
```

4. Generate and play commentary:
```bash
python generateCommentry.py
python playCommentaryFiles.py
```

Alternatively, use the provided shell script to start all components:
```bash
./run_all.sh
```

## Directory Structure

```
CricScore/
├── config.properties
├── requirements.txt
├── run_all.sh
├── resources/
│   ├── commentry/
│   │   ├── audio/
│   │   ├── images/
│   │   └── response/
│   └── scores/
│       ├── images/
│       └── response/
```

## Dependencies

- torch - PyTorch for AI processing
- TTS - Text-to-speech conversion
- watchdog - File system monitoring
- ollama - AI model integration
- configparser - Configuration management
- selenium - Web automation
- simpleaudio - Audio playback
- Pillow - Image processing

## Note

- Ensure all directory paths in `config.properties` are correctly set for your system
- The application requires an active internet connection
- Some features may require specific hardware capabilities (GPU) for optimal performance
