#!/usr/bin/env bash
# Generate narration MP3s for 黑白无常 using Edge TTS.
# EN: female voice, normal speed. ZH: male voice, slowed 5%.
set -euo pipefail
cd "$(dirname "$0")/.."

EN_VOICE="en-US-MichelleNeural"     # female, news/novel, friendly
ZH_VOICE="zh-CN-YunjianNeural"      # male, novel, solemn
ZH_RATE="-5%"

mkdir -p audio/en audio/zh

echo "→ Generating English audio (${EN_VOICE})"
for f in content/en/*.txt; do
  name=$(basename "$f" .txt)
  edge-tts -v "$EN_VOICE" -f "$f" --write-media "audio/en/${name}.mp3"
  echo "  ✓ audio/en/${name}.mp3"
done

echo "→ Generating Chinese audio (${ZH_VOICE} @ ${ZH_RATE})"
for f in content/zh/*.txt; do
  name=$(basename "$f" .txt)
  edge-tts -v "$ZH_VOICE" --rate="$ZH_RATE" -f "$f" --write-media "audio/zh/${name}.mp3"
  echo "  ✓ audio/zh/${name}.mp3"
done

echo "✅ Audio generation complete."
