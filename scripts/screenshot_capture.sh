#!/bin/bash
# ============================================================
# QuickTime Screenshot Capture Tool
# ============================================================
# Controls:
#   ENTER  = Toggle capture ON/OFF (pause/resume)
#   n      = New subfolder (while paused)
#   q      = Quit and show summary
#
# Usage:
#   chmod +x screenshot_capture.sh
#   ./screenshot_capture.sh
#
# Optional: set interval in seconds (default 2)
#   ./screenshot_capture.sh 3
# ============================================================

INTERVAL="${1:-2}"
BASE_DIR="$HOME/Desktop/ScreenCaptures"
CAPTURING=false
TOTAL_COUNT=0

# Temp files for communicating with background capture loop
CAPTURE_FLAG="/tmp/screenshot_capturing"
FOLDER_FILE="/tmp/screenshot_folder"
COUNT_FILE="/tmp/screenshot_count"

# Find the next available folder number
FOLDER_NUM=1
if [ -d "$BASE_DIR" ]; then
    LAST_FOLDER=$(ls -1d "$BASE_DIR"/[0-9]* 2>/dev/null | sort -t/ -k$(echo "$BASE_DIR/" | tr -cd '/' | wc -c | xargs expr 1 +) -n | tail -1)
    if [ -n "$LAST_FOLDER" ]; then
        LAST_NUM=$(basename "$LAST_FOLDER")
        # If the last folder has files in it, start a new one
        if [ "$(ls -A "$LAST_FOLDER" 2>/dev/null)" ]; then
            FOLDER_NUM=$((LAST_NUM + 1))
        else
            FOLDER_NUM=$LAST_NUM
        fi
    fi
fi

# Create output directory
mkdir -p "$BASE_DIR/$FOLDER_NUM"

# Write initial state to temp files
echo "$BASE_DIR/$FOLDER_NUM" > "$FOLDER_FILE"
echo "0" > "$COUNT_FILE"

# Prevent display from sleeping
caffeinate -d &
CAFFEINATE_PID=$!

# Get QuickTime Player window region (x,y,w,h) using Quartz
get_quicktime_region() {
    python3 -c "
import Quartz
windows = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
for w in windows:
    owner = w.get('kCGWindowOwnerName', '')
    name = w.get('kCGWindowName', '')
    if owner == 'QuickTime Player' and name and name != '':
        b = w['kCGWindowBounds']
        print(f\"{int(b['X'])},{int(b['Y'])},{int(b['Width'])},{int(b['Height'])}\")
        break
" 2>/dev/null
}

take_screenshot() {
    local OUT_DIR
    local COUNT
    OUT_DIR=$(cat "$FOLDER_FILE" 2>/dev/null)
    COUNT=$(cat "$COUNT_FILE" 2>/dev/null)
    COUNT=$((COUNT + 1))
    echo "$COUNT" > "$COUNT_FILE"

    FILENAME="${OUT_DIR}/capture_$(printf '%04d' $COUNT).png"

    REGION=$(get_quicktime_region)

    if [ -n "$REGION" ]; then
        screencapture -R "$REGION" -x "$FILENAME" 2>/dev/null
    else
        osascript -e 'tell application "QuickTime Player" to activate' 2>/dev/null
        sleep 0.3
        screencapture -x "$FILENAME" 2>/dev/null
    fi

    # Audio feedback
    afplay /System/Library/Sounds/Tink.aiff &

    echo "  📸 #$COUNT saved: $(basename "$FILENAME")"
}

# ============================================================
# Main
# ============================================================
clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║       QuickTime Screenshot Capture Tool               ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  ENTER  = Start / Pause capturing                    ║"
echo "║  n      = New subfolder (while paused)               ║"
echo "║  q      = Quit                                       ║"
echo "║                                                      ║"
echo "║  Interval: every ${INTERVAL} seconds                         ║"
echo "║  Saving to: ~/Desktop/ScreenCaptures/${FOLDER_NUM}/              ║"
echo "║  Display sleep: disabled                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "⏸  PAUSED — Press ENTER to start capturing..."
echo ""

# Background capture loop
capture_loop() {
    while true; do
        if [ -f "$CAPTURE_FLAG" ]; then
            take_screenshot
            sleep "$INTERVAL"
        else
            sleep 0.2
        fi
    done
}

# Clean up on exit
cleanup() {
    rm -f "$CAPTURE_FLAG" "$FOLDER_FILE" "$COUNT_FILE"
    kill "$CAFFEINATE_PID" 2>/dev/null
    kill $(jobs -p) 2>/dev/null
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "  Done! Captured $TOTAL_COUNT screenshots total."
    echo "  Saved in: $BASE_DIR"
    echo "════════════════════════════════════════════════════════"
    exit 0
}

trap cleanup EXIT INT TERM

# Remove any stale flag
rm -f "$CAPTURE_FLAG"

# Start background capture loop
capture_loop &

# Read user input for controls
while true; do
    read -rsn1 input

    if [ "$input" = "q" ] || [ "$input" = "Q" ]; then
        exit 0
    fi

    # N key — new subfolder (only while paused)
    if [ "$input" = "n" ] || [ "$input" = "N" ]; then
        if [ "$CAPTURING" = false ]; then
            FOLDER_NUM=$((FOLDER_NUM + 1))
            mkdir -p "$BASE_DIR/$FOLDER_NUM"
            echo "$BASE_DIR/$FOLDER_NUM" > "$FOLDER_FILE"
            echo "0" > "$COUNT_FILE"
            echo ""
            echo "📁 Created new folder: $FOLDER_NUM/"
            echo "⏸  PAUSED — Press ENTER to start capturing into folder $FOLDER_NUM/..."
            echo ""
        else
            echo "  (Pause first before creating a new folder)"
        fi
    fi

    # ENTER key (empty input from read)
    if [ -z "$input" ]; then
        if [ "$CAPTURING" = true ]; then
            CAPTURING=false
            rm -f "$CAPTURE_FLAG"
            local_count=$(cat "$COUNT_FILE" 2>/dev/null)
            echo ""
            echo "⏸  PAUSED (${local_count} in folder $FOLDER_NUM/) — Press ENTER to resume, N for new folder..."
            echo ""
        else
            CAPTURING=true
            echo ""
            echo "⏳ Waiting 4s for controls to fade..."
            sleep 4
            touch "$CAPTURE_FLAG"
            echo "🔴 CAPTURING into folder $FOLDER_NUM/ every ${INTERVAL}s — Press ENTER to pause..."
            echo ""
        fi
    fi
done
