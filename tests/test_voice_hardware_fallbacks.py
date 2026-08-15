from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import Mock


def test_voice_listener_starts_without_microphone(monkeypatch):
    import speech_recognition as sr
    monkeypatch.setattr(sr, "Microphone", Mock(side_effect=RuntimeError("no microphone")))
    from core.listener import VoiceListener

    listener = VoiceListener()
    assert listener.microphone is None
    assert listener.listen() == ""


def test_speaker_starts_without_tts(monkeypatch):
    fake_pyttsx3 = SimpleNamespace(init=Mock(side_effect=RuntimeError("no audio backend")))
    monkeypatch.setitem(sys.modules, "pyttsx3", fake_pyttsx3)

    from core.speaker import Speaker

    speaker = Speaker()
    speaker.speak("hello")
    assert speaker.engine is None
