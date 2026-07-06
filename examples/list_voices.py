"""Example showing how to list available voices."""

from cse import SpeechEngine

def main():
    engine = SpeechEngine()
    
    voices = engine.list_voices()
    
    print(f"Found {len(voices)} voices:")
    for v in voices:
        print(f" - {v}")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
