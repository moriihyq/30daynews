import os
import sys

def main():
    topic = os.environ.get('TOPIC', 'AI video tools')
    print(f"Running last30days for topic: {topic}")
    os.system(f"{sys.executable} scripts/last30days.py \"{topic}\"")
    
if __name__ == "__main__":
    main()