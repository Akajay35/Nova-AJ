"""
Central configuration for the assistant.
Change ASSISTANT_NAME to rename your assistant everywhere at once.
"""

ASSISTANT_NAME = "Nova AJ"
FULL_NAME = "Nova AJ"

# Wake word the assistant listens for before treating speech as a command.
# Keep it short and phonetically distinct so speech recognition catches it reliably.
WAKE_WORD = "nova aj"

# Text-to-speech voice settings
TTS_RATE = 175          # words per minute
TTS_VOLUME = 1.0        # 0.0 to 1.0

# Speech recognition settings
LISTEN_TIMEOUT = 5          # seconds to wait for speech to start
PHRASE_TIME_LIMIT = 8       # max seconds for a single command

# Folder where skill files live. Any .py file dropped here that follows
# the skill format is auto-loaded — no other code needs to change.
SKILLS_FOLDER = "skills"

# Simple on-disk memory (notes, reminders, etc.) used by built-in skills
DATA_FOLDER = "data"
