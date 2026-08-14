from __future__ import annotations

class VoiceLoop:
    """State machine for standby/active voice sessions; audio capture is injected."""
    def __init__(self, detector, pipeline):
        self.detector = detector
        self.pipeline = pipeline
        self.active = False

    def handle_transcript(self, transcript: str):
        if self.detector.is_stop(transcript):
            self.active = False
            return "sleep"
        if not self.active:
            if not self.detector.detect(transcript):
                return "standby"
            self.active = True
            command = self.detector.strip_wake_word(transcript)
            if not command:
                return "activated"
            return self._process_text(command)
        return self._process_text(transcript)

    def _process_text(self, text: str):
        response = self.pipeline.assistant(text)
        if response:
            self.pipeline.tts.speak(response)
        return response
