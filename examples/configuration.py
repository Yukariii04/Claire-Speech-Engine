"""Example showing how to configure the Claire Speech Engine."""

from cse import SpeechEngine
from cse.api.config import EngineConfig

def main():
    # You can configure the engine via a dictionary...
    engine1 = SpeechEngine({"runtime": {"debug": True}})
    
    # Or via the EngineConfig object...
    config = EngineConfig(overrides={"engine": {"name": "CSE Custom"}})
    engine2 = SpeechEngine(config)
    
    print("Engine 1 config debug:", engine1._config.overrides)
    print("Engine 2 config name:", engine2._config.overrides)
    
    engine1.shutdown()
    engine2.shutdown()

if __name__ == "__main__":
    main()
