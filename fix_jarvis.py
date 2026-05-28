import re
import datetime

# Read the file
with open('jarvis.py', 'r') as f:
    content = f.read()

# Find the answer_with_offline_model function and replace it with a clean version
pattern = r'def answer_with_offline_model\(query\):.*?(?=\ndef answer_with_gpt\(query\):)'

replacement = '''def answer_with_offline_model(query):
    """Offline fallback with rule-based answers for common questions."""
    
    q_lower = query.lower().strip()
    
    # Rule-based answers - simplified keys for flexible matching
    offline_knowledge = {
        "ai": "Artificial Intelligence is the field of computer science focused on creating machines and systems that can perform tasks typically requiring human intelligence.",
        "machine learning": "Machine learning is a subset of AI where systems learn patterns from data without being explicitly programmed for every task.",
        "deep learning": "Deep learning is a method of machine learning using neural networks with many layers to identify complex patterns in data.",
        "python": "Python is a popular, easy-to-learn programming language used widely in data science, web development, and automation.",
        "your name": "I am Jarvis, your voice assistant.",
        "who made": "I was created as a Python-based voice assistant project.",
        "what can you do": "I can tell you the time and date, look up information on Wikipedia, open websites, play music, check the weather, read news, and answer general questions.",
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.date.today().isoformat(),
    }
    
    for key, answer in offline_knowledge.items():
        if key in q_lower:
            speak(answer)
            return
    
    speak("I don't have that information available offline right now. Try asking about AI, machine learning, time, date, or what I can do.")


'''

# Replace using regex with DOTALL flag to match across newlines
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the file back
with open('jarvis.py', 'w') as f:
    f.write(content)

print("File fixed successfully!")
