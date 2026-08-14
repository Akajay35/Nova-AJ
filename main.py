from dotenv import load_dotenv
load_dotenv()

from core.assistant import NovaAssistant

if __name__ == "__main__":
    NovaAssistant().run()
