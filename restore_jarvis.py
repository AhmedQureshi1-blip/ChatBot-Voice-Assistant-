import os

# Read the current jarvis.py file
with open('jarvis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where answer_with_gpt starts and remove everything after answer_with_offline_model until answer_with_gpt begins
# Then rebuild properly

# First, let's find the clean parts
start_idx = 0
end_idx = len(lines)

# Find the line with "def answer_with_offline_model"
for i, line in enumerate(lines):
    if "def answer_with_offline_model(query):" in line:
        start_idx = i
        break

# Find the line with "def answer_with_gpt"
for i, line in enumerate(lines[start_idx:], start_idx):
    if "def answer_with_gpt(query):" in line:
        end_idx = i
        break

# Now reconstruct the file
before_offline = lines[:start_idx]

clean_offline = '''def answer_with_offline_model(query):
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

after_offline = lines[end_idx:]

# Write the fixed file
with open('jarvis.py', 'w', encoding='utf-8') as f:
    f.writelines(before_offline)
    f.write(clean_offline)
    f.writelines(after_offline)

print("File restored!")
