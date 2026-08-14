# Nova AJ — Personal Voice Assistant

A voice-controlled personal AI assistant with a **self-expanding skill system**.
Drop a new skill file into `skills/`, restart, and Nova AJ can do it — no core
code edits required.

## Features

- Wake-word activated (says "Nova AJ" to start listening)
- Offline text-to-speech (pyttsx3)
- Google Speech Recognition for voice-to-text
- Auto-discovering skills architecture
- Built-in skills: time/date, greetings, notes, help/skill-listing

## Setup

1. Install Python 3.9+.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   > On Linux you may also need `sudo apt install portaudio19-dev` before
   > installing PyAudio. On Mac, `brew install portaudio`.
3. Run it:
   ```
   python main.py
   ```
4. Say **"Nova AJ"**, wait for "Yes?", then speak your command.

## Renaming your assistant

Change `ASSISTANT_NAME`, `FULL_NAME`, and `WAKE_WORD` in `config.py`. Everything else
updates automatically.

## Adding a new skill (this is how it "automatically increases")

1. Copy `skills/_skill_template.py` to `skills/your_skill_name.py`.
2. Rename the class, set `keywords` to the phrases that should trigger it,
   and write your logic in `handle()`.
3. Restart the assistant — it's auto-loaded. That's it.

Example minimal skill:

```python
from core.base_skill import BaseSkill

class JokeSkill(BaseSkill):
    name = "joke"
    keywords = ["tell me a joke", "make me laugh"]

    def handle(self, query: str) -> str:
        return "I'd tell you a UDP joke, but you might not get it."
```

## Project structure

```
aj-assistant/
├── main.py                 # entry point
├── config.py                # name, wake word, and behavior settings
├── core/
│   ├── assistant.py          # main listen -> route -> speak loop
│   ├── listener.py           # microphone input, wake word detection
│   ├── speaker.py             # text-to-speech output
│   ├── skill_manager.py        # auto-discovers and routes to skills
│   └── base_skill.py            # base class every skill implements
├── skills/
│   ├── _skill_template.py        # copy this to make a new skill
│   ├── time_skill.py
│   ├── greeting_skill.py
│   ├── notes_skill.py
│   └── help_skill.py
└── requirements.txt
```

## Ideas for skills to add next

- Smart home control (Home Assistant / Philips Hue API)
- Music playback (Spotify API)
- Web search / weather (needs an API key)
- Calendar reading
- App/website launcher
