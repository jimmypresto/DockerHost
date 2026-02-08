# YouTube Audio Enhance

Download YouTube playlists or individual videos as high-quality audio, enhance with professional stage sound effects, and output as MP3.

## Capabilities

- Download YouTube playlists or individual videos as highest quality audio
- Extract and suggest collection names from YouTube metadata
- Apply professional stage sound enhancement:
  - Concert hall reverb
  - EQ warmth and presence boost
  - Stereo widening
  - Loudness normalization without clipping
- Output as high-quality MP3 (320kbps)

## Workflow

When this skill is invoked:

1. **Get YouTube URL**
   - Ask the user for the YouTube URL (playlist or individual video)
   - Use yt-dlp to extract the title/playlist name
   - Suggest this as the collection name

2. **Get Output Configuration**
   - Ask for output directory (default: `~/Downloads/youtube/`)
   - Ask for collection name (default: extracted from YouTube metadata)
   - Sanitize the collection name (replace spaces with underscores, remove special characters)

3. **Create Directory Structure**
   ```
   {output_dir}/{date}/raw/          # Original WAV files
   {output_dir}/{date}/enhanced/     # Enhanced WAV files
   {output_dir}/{date}/final/        # Final MP3 files
   {output_dir}/{collection_name}/   # Final organized collection
   ```

4. **Download Audio**
   - Use yt-dlp to download as WAV format with highest quality
   - Command: `yt-dlp -x --audio-format wav --audio-quality 0 --output "{dir}/%(playlist_index)02d - %(title)s.%(ext)s" "{url}"`
   - For individual videos, use simpler naming

5. **Enhance Audio**
   - Apply stage sound effects to each WAV file:
     ```bash
     ffmpeg -y -i "$input" -af \
     "aecho=0.8:0.72:60:0.25,\
     equalizer=f=250:t=q:w=1.2:g=2,\
     equalizer=f=3500:t=q:w=1.5:g=3,\
     equalizer=f=10000:t=q:w=1.0:g=1.5,\
     stereotools=slev=1.1:mlev=0.95,\
     loudnorm=I=-14:TP=-0.3:LRA=11,\
     alimiter=limit=0.95:level=disabled" \
     "$output"
     ```

6. **Convert to MP3**
   - Convert enhanced WAV files to MP3 at 320kbps:
     ```bash
     ffmpeg -y -i "$input" -codec:a libmp3lame -b:a 320k -q:a 0 "$output"
     ```

7. **Organize Final Collection**
   - Copy final MP3 files to `{output_dir}/{collection_name}/`
   - List the completed files for the user

## Audio Enhancement Details

- **Reverb**: Concert hall ambience (aecho filter with 60ms delay)
- **EQ Warmth**: +2dB at 250Hz for body and warmth
- **EQ Presence**: +3dB at 3.5kHz for clarity and presence
- **EQ Air**: +1.5dB at 10kHz for brightness
- **Stereo Width**: Slight stereo enhancement (side level 1.1x)
- **Normalization**: EBU R128 loudness normalization to -14 LUFS
- **Peak Limiting**: True peak limited to -0.3 dBTP to prevent clipping

## Error Handling

- Verify yt-dlp is available before starting
- Check if output directory exists or can be created
- Handle download failures gracefully
- Report progress for each stage (download, enhance, convert)

## Example Usage

User: `/youtube-audio-enhance`

Assistant asks:
1. "What's the YouTube URL?"
2. Extracts title: "Ys Piano Collection"
3. "Where should I save the files? (default: ~/Downloads/youtube/)"
4. "What should I name this collection? (suggested: Ys_Piano_Collection)"
5. Proceeds with download, enhancement, and conversion
6. Reports completion with file count and location

## Notes

- This skill requires `yt-dlp` and `ffmpeg` to be installed
- Processing time depends on playlist size and audio length
- Enhanced files will have higher sample rate (192kHz) before MP3 conversion
- Original WAV and enhanced WAV files are preserved in dated directories
