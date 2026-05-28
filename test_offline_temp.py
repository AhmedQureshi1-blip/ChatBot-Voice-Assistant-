from jarvis import answer_with_offline_model

queries = [
    'what is machine learning',
    'what is deep learning',
    'what is python',
    'what can you do',
    'what is the time',
    'tell me about aliens',
]

for q in queries:
    print('Q:', q)
    answer_with_offline_model(q)
    print()
