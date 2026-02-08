# YouTube Audio Download Skill

A Claude Code skill for downloading YouTube playlists or individual videos, enhancing the audio with professional stage sound effects, and outputting high-quality MP3 files.

## Installation

The skill is already installed at: `~/.claude/skills/youtube-audio-download/`

## Requirements

Before using this skill, ensure you have:

1. **yt-dlp** - YouTube downloader
   ```bash
   # Install via homebrew (macOS)
   brew install yt-dlp

   # Or via pip
   pip install yt-dlp
   ```

2. **ffmpeg** - Audio processing tool
   ```bash
   # Install via homebrew (macOS)
   brew install ffmpeg
   ```

## Usage

### In Claude Code:

```
/youtube-audio-download
```

Or simply ask Claude:
```
"Download and enhance this YouTube playlist: [URL]"
```

### Interactive Prompts

When you invoke the skill, Claude will ask you for:

1. **YouTube URL**
   - Paste the YouTube playlist or video URL
   - Example: `https://www.youtube.com/playlist?list=PLzFTGYa_evXhB2O1lSbmqBOfFcVgAhLFH`

2. **Output Directory** (optional)
   - Default: `~/Downloads/youtube/`
   - Claude will suggest this, press Enter to accept or provide your own path

3. **Collection Name** (optional)
   - Claude will extract the playlist/video title and suggest a sanitized name
   - Example: "Ys Piano Collection 2" → `Ys_Piano_Collection_2`
   - Press Enter to accept or provide your own name

### Output Structure

The skill creates this directory structure:

```
~/Downloads/youtube/
├── YYYYMMDD/
│   ├── raw/           # Original WAV downloads
│   ├── enhanced/      # Stage-enhanced WAV files
│   └── final/         # High-quality MP3 files (320kbps)
└── {Collection_Name}/ # Final organized collection (copies of MP3s)
```

## Audio Enhancement

The skill applies professional stage sound effects:

- **Concert Hall Reverb**: Adds spatial depth and ambience
- **EQ Warmth**: +2dB boost at 250Hz for warmth and body
- **EQ Presence**: +3dB boost at 3.5kHz for clarity
- **EQ Air**: +1.5dB boost at 10kHz for brightness
- **Stereo Widening**: Enhances stereo field
- **Loudness Normalization**: EBU R128 standard (-14 LUFS)
- **Peak Limiting**: Prevents clipping at -0.3 dBTP

## Example Session

```
User: /youtube-audio-download

Claude: What's the YouTube URL (playlist or individual video)?
User: https://www.youtube.com/playlist?list=PLzFTGYa_evXhB2O1lSbmqBOfFcVgAhLFH

Claude: I found the playlist: "Ys Piano Collection 2" with 12 tracks.
        Where should I save the files? (default: ~/Downloads/youtube/)
User: [press Enter for default]

Claude: What should I name this collection? (suggested: Ys_Piano_Collection_2)
User: [press Enter for suggested name]

Claude: Starting download and enhancement process...
        [Progress updates]
        ✅ All 12 tracks complete!
        Final collection: ~/Downloads/youtube/Ys_Piano_Collection_2/
```

## Technical Details

### Download Command
```bash
yt-dlp -x --audio-format wav --audio-quality 0 \
  --output "%(playlist_index)02d - %(title)s.%(ext)s" \
  "{youtube_url}"
```

### Enhancement Filter Chain
```bash
ffmpeg -i input.wav -af \
  "aecho=0.8:0.72:60:0.25,\
   equalizer=f=250:t=q:w=1.2:g=2,\
   equalizer=f=3500:t=q:w=1.5:g=3,\
   equalizer=f=10000:t=q:w=1.0:g=1.5,\
   stereotools=slev=1.1:mlev=0.95,\
   loudnorm=I=-14:TP=-0.3:LRA=11,\
   alimiter=limit=0.95:level=disabled" \
  output.wav
```

### MP3 Conversion
```bash
ffmpeg -i input.wav -codec:a libmp3lame -b:a 320k -q:a 0 output.mp3
```

## Troubleshooting

### yt-dlp not found
```bash
# Check if installed
yt-dlp --version

# Install if missing
brew install yt-dlp
```

### ffmpeg not found
```bash
# Check if installed
ffmpeg -version

# Install if missing
brew install ffmpeg
```

### Download fails
- Check the YouTube URL is valid
- Some videos may be region-restricted or age-restricted
- Try updating yt-dlp: `yt-dlp -U`

### Processing takes too long
- Large playlists will take time to process
- Each track goes through: download → enhance → convert
- You can monitor progress in the terminal output

## Notes

- Original files are preserved in dated directories
- MP3 files use LAME encoder at 320kbps for highest quality
- Enhanced files are upsampled to 192kHz before final MP3 conversion
- The skill handles both playlists and individual videos

## Version

**v1.0.0** - Initial release

## License

Created for personal use with Claude Code.
