#!/bin/bash

BOT_NAME="bot.py"
STOP_FILE="stop_loop.txt"

# Function to stop the bot
stop_bot() {
    echo "🛑 Stopping bot..."
    pkill -f "python3 $BOT_NAME"
    echo "stop" > "$STOP_FILE"  # Create a stop flag
    exit 0
}

# Ensure the bot keeps running unless stopped manually
while true; do
    if [[ -f "$STOP_FILE" ]]; then
        echo "🛑 Bot has been stopped."
        rm "$STOP_FILE"  # Remove stop flag for future restarts
        exit 0
    fi

    echo "✅ Starting bot..."
    python3 $BOT_NAME

    echo "🚨 Bot Crashed! Restarting in 5 seconds..."
    sleep 5
done