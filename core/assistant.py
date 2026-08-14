"""
The main run loop: wait for the wake word, capture a command, route it to
the right skill, speak the result, repeat.
"""

import config
from core.listener import Listener
from core.speaker import Speaker
from core.skill_manager import SkillManager


class Assistant:
    def __init__(self):
        self.listener = Listener()
        self.speaker = Speaker()
        self.skills = SkillManager(config.SKILLS_FOLDER)

    def run(self):
        self.speaker.say(f"{config.FULL_NAME} is online and listening for the wake word.")

        while True:
            try:
                if self.listener.listen_for_wake_word():
                    self.speaker.say("Yes?")
                    command = self.listener.listen_for_command()

                    if not command:
                        self.speaker.say("Sorry, I didn't catch that.")
                        continue

                    if command.lower() in ("exit", "quit", "shut down", "goodbye"):
                        self.speaker.say("Goodbye!")
                        break

                    response = self.skills.route(command)
                    self.speaker.say(response)

            except KeyboardInterrupt:
                self.speaker.say("Shutting down.")
                break
