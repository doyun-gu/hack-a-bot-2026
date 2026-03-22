"""
GridBox — Packet Tracker
Sequence-based wireless reliability monitoring.

Tracks gaps in sequence numbers (0-255) to detect packet loss.
"""


class PacketTracker:
    def __init__(self):
        self.expected_seq = 0
        self.received = 0
        self.lost = 0
        self.total = 0

    def track(self, seq):
        self.total += 1
        if seq == self.expected_seq:
            # Normal — received in order
            self.received += 1
        else:
            # Gap detected — packets were lost
            if seq > self.expected_seq:
                gap = seq - self.expected_seq
            else:
                gap = (256 - self.expected_seq) + seq  # wrap-around
            self.lost += gap
            self.received += 1

        self.expected_seq = (seq + 1) & 0xFF

    def reliability(self):
        if self.total == 0:
            return 100.0
        return (self.received / (self.received + self.lost)) * 100.0

    def get_stats(self):
        return {
            'received': self.received,
            'lost': self.lost,
            'reliability': round(self.reliability(), 1),
        }
