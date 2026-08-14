# Nova AJ — Personal AI Assistant

Nova AJ is a voice-first personal AI assistant designed to grow through a controlled, modular skill system.

## Nova AJ v3

- 🎙️ Wake-word voice interaction
- 🧠 Local memory for approved facts and notes
- 💬 Short-term conversation context for more natural AI replies
- 🤖 Optional OpenAI-powered reasoning
- 🧩 Auto-discovered Python skills
- 📈 Missing-capability detection and reviewable skill proposals
- 🧮 Safe arithmetic calculator
- 🌐 Allowlisted browser launcher for common websites
- 🔄 Skill reload without restarting the assistant
- 🔐 Safe-by-default design: no arbitrary self-generated code execution

## Architecture

```text
Nova-AJ/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── core/
│   ├── assistant.py       # voice loop + orchestration
│   ├── listener.py        # microphone / wake word
│   ├── speaker.py         # text-to-speech
│   ├── base_skill.py      # skill contract
│   ├── skill_manager.py   # dynamic discovery and routing
│   ├── memory.py          # persistent local memory
│   ├── conversation.py    # short-term conversation buffer
│   ├── learning.py        # missing-skill proposals
│   ├── permissions.py     # action policy
│   └── ai_provider.py     # optional AI reasoning
├── skills/
│   ├── greeting_skill.py
│   ├── time_skill.py
│   ├── notes_skill.py
│   ├── memory_skill.py
│   ├── help_skill.py
│   ├── system_skill.py
│   ├── calculator_skill.py
│   ├── browser_skill.py
│   └── _skill_template.py
├── tests/
├── data/                  # local runtime data
├── proposals/             # proposed future skills
└── docs/SKILLS.md
```

## Quick start

1. Install Python 3.10+.
2. Install packages:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Add `OPENAI_API_KEY` if you want AI reasoning.
5. Run:
   `python main.py`
6. Say **"Nova AJ"** and then speak your command.

## Example commands

- "Nova AJ, what time is it?"
- "Nova AJ, calculate 25 * 4"
- "Nova AJ, open YouTube"
- "Nova AJ, remember that I use VS Code"
- "Nova AJ, what skills do you have?"
- "Nova AJ, show my memory"

## Skill growth

When Nova AJ receives a request it cannot safely handle, the learning engine records a missing capability as a proposal. A human can then implement, test, review, and enable that skill. This gives the assistant a path to become more capable without allowing uncontrolled self-modification.

## Security

Never commit API keys. Keep `.env` local. Review any skill before enabling it, especially skills that access files, the operating system, accounts, payments, or external services. Browser automation is intentionally allowlisted.
