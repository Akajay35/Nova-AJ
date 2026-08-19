# Nova AJ — Personal AI Assistant

Nova AJ is a voice-first personal AI assistant designed to grow through a controlled, modular skill system.

## v286 rebuild

This branch is the clean v286 hardening rebuild. It is not considered verified until the GitHub Actions test workflow completes successfully.

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

## Security

Never commit API keys. Keep `.env` local. Review any skill before enabling it, especially skills that access files, the operating system, accounts, payments, or external services. Browser automation is intentionally allowlisted.
