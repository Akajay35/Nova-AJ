# Nova AJ — Personal AI Assistant

Nova AJ is a voice-first personal AI assistant designed to grow through a controlled, modular skill system.

## Vision

- 🎙️ Voice-first interaction with a configurable wake word
- 🧠 Local memory for approved preferences, notes, and conversation context
- 🧩 Auto-discovered skills that can be added without changing the core router
- 📈 Skill-growth engine that records missing capabilities and creates reviewable skill proposals
- 🔐 Permission gates for actions that can change files, apps, accounts, or external services
- 🤖 Optional OpenAI-powered reasoning when `OPENAI_API_KEY` is configured
- 📴 Core functionality remains useful without an AI API key

> Nova AJ does not silently write or execute arbitrary code. New skills are proposed, validated, and explicitly enabled.

## Project structure

```text
Nova-AJ/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── core/
│   ├── assistant.py
│   ├── listener.py
│   ├── speaker.py
│   ├── base_skill.py
│   ├── skill_manager.py
│   ├── memory.py
│   ├── learning.py
│   ├── permissions.py
│   └── ai_provider.py
├── skills/
│   ├── greeting_skill.py
│   ├── time_skill.py
│   ├── notes_skill.py
│   ├── help_skill.py
│   ├── memory_skill.py
│   ├── system_skill.py
│   └── _skill_template.py
├── data/
├── proposals/
└── docs/SKILLS.md
```

## Quick start

1. Install Python 3.10+.
2. Install packages: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and optionally add an OpenAI API key.
4. Run: `python main.py`
5. Say **"Nova AJ"**, wait for the response, and give a command.

On Linux, PyAudio may require PortAudio development packages. On Windows, use a current Python version and a working microphone.

## Voice examples

- "Nova AJ, what time is it?"
- "Nova AJ, remember my favorite editor is VS Code."
- "Nova AJ, take a note: finish the dashboard tomorrow."
- "Nova AJ, what skills do you have?"
- "Nova AJ, show my memory."

## Automatic skill growth

1. Nova AJ receives a request.
2. The router looks for an installed capability.
3. If no safe skill matches, the learning engine records the missing capability.
4. A reviewable proposal is created in `proposals/`.
5. A developer/user implements and tests the skill.
6. The skill is enabled only after validation.

This makes Nova AJ expandable without giving the assistant unrestricted permission to modify or execute its own source code.

## Security

Never commit API keys. Keep `.env` local. Review new skills before enabling them, especially skills that access files, the operating system, accounts, payments, or external APIs.
