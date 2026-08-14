from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ContinuousVoiceResult:
    cycles: int
    stopped: bool

class ContinuousVoice:
    """Run bounded microphone cycles through the existing voice pipeline."""
    def __init__(self, microphone, pipeline, max_cycles: int = 10):
        self.microphone = microphone
        self.pipeline = pipeline
        self.max_cycles = max(1, max_cycles)
        self.running = False

    def run(self) -> ContinuousVoiceResult:
        self.running = True
        cycles = 0
        try:
            while self.running and cycles < self.max_cycles:
                audio = self.microphone.listen()
                result = self.pipeline.process_once(audio)
                cycles += 1
                if result.heard.strip().lower() in {"stop", "shutdown", "exit"}:
                    self.running = False
        finally:
            self.running = False
        return ContinuousVoiceResult(cycles=cycles, stopped=not self.running)

    def stop(self) -> None:
        self.running = False
