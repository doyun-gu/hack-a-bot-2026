#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  Wireless Reliability Implementation"
echo "========================================="

tmux kill-session -t wireless 2>/dev/null

tmux new-session -d -s wireless \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 100 \
    -p 'Read docs/02-electrical/wireless-reliability.md for the full spec. Pull latest main first.

Implement the wireless reliability protocol in the MicroPython firmware. Do NOT touch any files in c_sdk/ folders (another worker is editing those).

Task 1: Create src/master-pico/micropython/packet_tracker.py
- PacketTracker class with track(seq), reliability(), get_stats()
- Exactly as specified in the wireless-reliability doc
Commit: \"Add PacketTracker for sequence-based reliability monitoring\"

Task 2: Update src/master-pico/micropython/main.py
- Add send_packet() wrapper with retry logic for critical packets
- ALERT packets sent 3 times, COMMAND packets sent 2 times
- Track send success/fail stats
- Add wireless_stats to serial JSON output
- Do NOT rewrite the whole file — only add/modify the wireless send section
Commit: \"Add redundant sends for critical packets\"

Task 3: Create src/slave-pico/micropython/packet_tracker.py
- Same PacketTracker class (copy from master)
Commit: \"Add PacketTracker to slave Pico\"

Task 4: Update src/slave-pico/micropython/main.py
- Add PacketTracker to the receive loop
- Track sequence numbers from received packets
- Add wireless reliability % to telemetry dict
- Add graceful degradation: values grey after 1s, LINK LOST after 3s (already exists, verify)
- Do NOT rewrite the whole file — only add/modify the receive section
Commit: \"Add sequence tracking and reliability monitoring to slave\"

Task 5: Update src/shared/protocol.py
- Verify sequence counter is working in pack functions
- Add packet loss stats to the HEARTBEAT packet if there is room in the 32 bytes
Commit: \"Update protocol with reliability stats in heartbeat\"

Done. Push all changes.'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'wireless'"
echo ""
echo "  Watch:    tmux attach -t wireless"
echo "  Progress: git log --oneline -10"
echo "  Stop:     tmux kill-session -t wireless"
