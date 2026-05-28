import datetime
import os
import sys
import webbrowser
import glob
import pathlib
import json

import openai
import pyjokes
import pyttsx3
import pywhatkit
import psutil
import requests
import speech_recognition as sr
import wikipedia

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
except Exception:
    AutoModelForSeq2SeqLM = None
    AutoTokenizer = None
    pipeline = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

try:
    import wmi
except ImportError:
    wmi = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


class DummyTTS:
    def say(self, text):
        # DummyTTS should not duplicate console output; speak() handles printing.
        return None

    def runAndWait(self):
        return None

    def getProperty(self, name):
        if name == "voices":
            return []
        return None

    def setProperty(self, name, value):
        return None


def init_tts_engine():
    try:
        return pyttsx3.init()
    except Exception:
        return DummyTTS()


engine = init_tts_engine()
chat_history = []
gpt_retry_after = None
DEBUG = os.getenv("JARVIS_DEBUG", "").strip().lower() in ("1", "true", "yes")


def speak(text):
    message = str(text)
    print("Jarvis:", message)
    try:
        engine.say(message)
        engine.runAndWait()
    except Exception:
        print(message)


def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    speak(f"{greeting}. I am Jarvis. How can I help you?")


def listen_for_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=12)
        query = recognizer.recognize_google(audio)
        print("User:", query)
        return query.strip()
    except Exception:
        print("Jarvis: I couldn't hear that. Please try again.")
        try:
            # Ask the user to type the command as a fallback
            typed = input("Type your command (or press Enter to retry listening): ").strip()
            if typed:
                print("User (typed):", typed)
                return typed
        except Exception:
            pass
        return ""


def open_site(name, url):
    webbrowser.open(url)
    speak(f"Opening {name}")


def get_weather(city_name):
    api_key = "8ef61edcf1c576d65d836254e11ea420"
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    response = requests.get(base_url + f"appid={api_key}&q={city_name}")
    payload = response.json()

    if str(payload.get("cod")) == "404":
        speak("City not found")
        return

    main = payload.get("main", {})
    weather = payload.get("weather", [{}])[0]
    temperature = float(main.get("temp", 0)) - 273.15
    humidity = main.get("humidity", "unknown")
    description = weather.get("description", "unknown")

    speak(
        f"Temperature is {temperature:.2f} Celsius, humidity is {humidity} percent, and {description}."
    )


def read_news():
    api_key = "9bb9b456bf124f80aba6a0e09cc2f811"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        speak("Unable to fetch news right now.")
        return

    articles = response.json().get("articles", [])[:3]
    if not articles:
        speak("No news articles were returned.")
        return

    for article in articles:
        title = article.get("title")
        if title:
            speak(title)


def system_info():
    if wmi is None:
        speak("System information is unavailable on this machine.")
        return

    system = wmi.WMI().Win32_ComputerSystem()[0]
    speak(f"Manufacturer {system.Manufacturer}")
    speak(f"Model {system.Model}")


def _trim_chat_history(history, max_messages=12):
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]


def _create_openai_client(api_key):
    if OpenAI is None:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def _extract_chat_text(response):
    try:
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def _extract_completion_text(response):
    try:
        return response.choices[0].text.strip()
    except Exception:
        return ""


def _call_ollama(query, model="mistral", max_tokens=200):
    """Call local Ollama API for offline LLM inference.
    
    Requires Ollama installed and running on localhost:11434.
    Returns response text or empty string if unavailable.
    """
    try:
        import urllib.request
        import urllib.error
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": query,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": max_tokens,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            raw = response.read().decode("utf-8")
            try:
                result = json.loads(raw)
            except Exception:
                # If Ollama returned plain text, return it
                return raw.strip()

            # Flexible extraction: try common keys used by different Ollama versions
            text = ""
            if isinstance(result, dict):
                # direct 'response' field
                text = result.get("response", "") or result.get("result", "")
                # outputs (list)
                if not text:
                    outs = result.get("outputs") or result.get("choices")
                    if isinstance(outs, list) and outs:
                        parts = []
                        for o in outs:
                            if isinstance(o, dict):
                                # common keys
                                for k in ("text", "content", "response", "message"):
                                    v = o.get(k)
                                    if isinstance(v, str) and v:
                                        parts.append(v)
                                # nested message
                                msg = o.get("message")
                                if isinstance(msg, dict):
                                    v = msg.get("content") or msg.get("text")
                                    if isinstance(v, str) and v:
                                        parts.append(v)
                        text = "\n".join(parts)
                if not text:
                    # try top-level 'output' or other heuristics
                    for k in ("output", "text", "content"):
                        v = result.get(k)
                        if isinstance(v, str) and v:
                            text = v
                            break

            return (text or "").strip()
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError) as e:
        if DEBUG:
            print(f"Ollama connection error: {e}")
        return ""
    except Exception as e:
        if DEBUG:
            print(f"Ollama call error: {e}")
        return ""


def _call_ollama_with_retry(query, model="mistral", max_tokens=200, retries=1):
    """Call Ollama once - timeouts skip to offline, no retry loops."""
    try:
        result = _call_ollama(query, model, max_tokens)
        if result:
            return result
    except Exception as e:
        if DEBUG:
            print(f"Ollama call failed: {type(e).__name__}")
    return ""


def _get_ollama_installed_models():
    """Return a list of installed Ollama model names from the local server."""
    try:
        import urllib.request

        url = "http://localhost:11434/api/tags"
        with urllib.request.urlopen(url, timeout=5) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
            models = []
            for item in data.get("models", []):
                name = item.get("name") if isinstance(item, dict) else None
                if isinstance(name, str) and name:
                    models.append(name)
            return models
    except Exception as e:
        if DEBUG:
            print(f"Ollama tags error: {e}")
        return []


def _ollama_is_healthy():
    """Quick health check to see if Ollama is responding and can generate."""
    try:
        import urllib.request
        # Test actual API response with a very short timeout
        payload = '{"model":"mistral:latest","prompt":"ok","stream":false,"num_predict":1}'
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload.encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        # Only 3 second timeout for health check - if Ollama can't respond in 3s, skip it
        with urllib.request.urlopen(req, timeout=3) as response:
            response.read()
        return True
    except Exception:
        return False


def answer_with_ollama(query):
    """Try to answer using local Ollama LLM if available."""
    # Quick health check: if Ollama isn't responding, skip immediately
    if not _ollama_is_healthy():
        if DEBUG:
            print("Ollama health check failed, skipping to offline")
        return False
    # Try installed Ollama models first; fall back to common names only if tags are unavailable.
    preferred_models = ["mistral", "neural-chat", "llama2", "dolphin-mixtral"]
    installed_models = _get_ollama_installed_models()

    models = []
    if installed_models:
        for preferred in preferred_models:
            for installed in installed_models:
                if installed == preferred or installed.startswith(f"{preferred}:"):
                    models.append(installed)
                    break
        for installed in installed_models:
            if installed not in models:
                models.append(installed)

    if not models:
        models = preferred_models

    for model in models:
        try:
            # Use a simpler, more direct prompt format
            prompt = (
                "Answer the following question concisely in 1-2 sentences. "
                f"Question: {query}\nAnswer:"
            )
            response = _call_ollama_with_retry(prompt, model=model, max_tokens=180, retries=2)
            if response:
                if DEBUG:
                    print(f"Responder=OLLAMA model={model}")
                speak(response)
                return True
            else:
                # small delay and try next model
                continue
        except Exception as e:
            if DEBUG:
                print(f"answer_with_ollama error for model {model}: {e}")
            continue
    if DEBUG:
        print("Responder=OLLAMA none")
    return False


def answer_with_offline_model(query):
    """Offline fallback with rule-based answers for common questions."""
    
    q_lower = query.lower().strip()
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "do", "for", "from", "go", "how", "i",
        "in", "is", "it", "me", "my", "of", "on", "or", "our", "so", "the", "to", "we", "what", "when",
        "where", "which", "who", "why", "with", "you", "your"
    }

    # Career/advice override: intercept comparative or "should I" style questions
    career_triggers = [
        "should i",
        "should i go",
        "which is better",
        "which should i",
        "vs",
        "difference",
        "or",
        "computer science or",
        "software engineering or",
        "cs or",
    ]
    if ("computer science" in q_lower or "cs" in q_lower) and ("software engineering" in q_lower or "software engineer" in q_lower or any(t in q_lower for t in career_triggers)):
        answer_text = (
            "Computer science (CS) emphasizes the theory of computing, algorithms, and systems, while "
            "software engineering (SE) focuses on applying engineering principles to design, build, and maintain software. "
            "Choose CS if you enjoy math, theory, research, or building foundational systems; choose SE if you prefer practical software development, project workflows, and engineering processes. "
            "Both paths lead to strong software careers; you can study CS for a broad theoretical base and pick up SE practices on the job or via a focused program. "
            "If you like both, start with CS fundamentals and take SE courses or internships to gain applied experience."
        )
        speak(answer_text)
        return
    
    # Rule-based answers - massively expanded
    offline_knowledge = {
         # === Core AI/ML concepts ===
         "ai": "Artificial Intelligence (AI) is the branch of computer science concerned with creating machines that can perform tasks that normally require human intelligence, such as perception, reasoning, decision-making, and language understanding.",
         "artificial intelligence": "Artificial Intelligence (AI) is the branch of computer science concerned with creating machines that can perform tasks that normally require human intelligence, such as perception, reasoning, decision-making, and language understanding.",
         "machine learning": "Machine learning (ML) is a subset of AI where algorithms learn patterns from data to make predictions or decisions. ML systems are trained on examples and improve with more data.",
         "ml": "Machine learning (ML) is a subset of AI where algorithms learn patterns from data to make predictions or decisions. ML systems are trained on examples and improve with more data.",
         "deep learning": "Deep learning is a type of ML that uses multi-layered neural networks (deep neural networks) to automatically learn hierarchical features from raw data, excelling at tasks like image and speech recognition.",
         "dl": "Deep learning is a type of ML that uses multi-layered neural networks (deep neural networks) to automatically learn hierarchical features from raw data, excelling at tasks like image and speech recognition.",
         "neural network": "Neural networks are composed of input, hidden, and output layers. During training, inputs propagate forward and gradients propagate backward to update weights using optimizers like gradient descent.",
         "ann": "An Artificial Neural Network (ANN) is a computational model inspired by biological neurons. It has layers of interconnected nodes (neurons) where each connection has a weight. Training adjusts weights to minimize error.",
         "multilayer perceptron": "A Multilayer Perceptron (MLP) is a feedforward neural network with one or more hidden layers. It consists of an input layer, hidden layers, and an output layer, capable of learning non-linear relationships in data.",
         "multi layer perceptron": "A Multilayer Perceptron (MLP) is a feedforward neural network with one or more hidden layers. It consists of an input layer, hidden layers, and an output layer, capable of learning non-linear relationships in data.",
         "mlp": "MLP (Multilayer Perceptron) is a feedforward neural network with input, hidden, and output layers. It uses backpropagation to train and can approximate any continuous function.",
         "perceptron": "A perceptron is the simplest type of neural network, consisting of a single layer of neurons. It was one of the earliest neural network models and can solve linearly separable problems.",
         "backpropagation": "Backpropagation is a key algorithm for training neural networks. It computes gradients of the loss function with respect to weights and updates them to minimize error through multiple passes.",
         "forward propagation": "Forward propagation is the process where input data passes through a neural network layer by layer, computing predictions. Each neuron applies weights and an activation function to produce outputs.",
         "hidden layer": "Hidden layers are layers between input and output layers in a neural network. They extract features and learn representations from the data, enabling the network to learn complex patterns.",
         "activation function": "Activation functions (ReLU, Sigmoid, Tanh) introduce non-linearity into neural networks. They allow networks to learn non-linear relationships and determine if a neuron fires based on its input.",
         "relu": "ReLU (Rectified Linear Unit) is an activation function that returns 0 for negative inputs and the input value for positive inputs. It is widely used due to computational efficiency and effectiveness in deep networks.",
         "sigmoid": "Sigmoid is an activation function that maps inputs to values between 0 and 1. It is often used in the output layer for binary classification problems.",
         "softmax": "Softmax is an activation function that converts a vector of numbers into a probability distribution. It is commonly used in the output layer for multi-class classification problems.",
         "convolutional": "Convolutional Neural Networks (CNNs) use convolutional layers to apply filters across spatial data. They are highly effective for image processing, computer vision, and pattern recognition tasks.",
         "recurrent": "Recurrent Neural Networks (RNNs) have connections that loop back on themselves, allowing them to process sequential data. They maintain internal state and are used for time series and natural language processing.",
         "lstm": "LSTM (Long Short-Term Memory) is a type of RNN that can learn long-range dependencies. It has memory cells that control information flow through gates (input, forget, output), solving the vanishing gradient problem.",
         "gru": "GRU (Gated Recurrent Unit) is a simpler alternative to LSTM with fewer parameters. It also uses gating mechanisms to handle long-range dependencies in sequential data.",
         "dropout": "Dropout is a regularization technique that randomly disables a fraction of neurons during training. It prevents overfitting by forcing the network to learn redundant representations.",
         "batch normalization": "Batch normalization normalizes layer inputs by subtracting mean and dividing by standard deviation. It speeds up training, reduces internal covariate shift, and acts as a regularizer.",
         "gradient": "Gradients measure how much the loss function changes with respect to model parameters. They are computed via backpropagation and used to update weights during training via optimizers.",
         "llm": "An LLM (Large Language Model) is a neural network with billions of parameters trained on vast amounts of text data. LLMs like GPT, Claude, and Mistral can understand and generate human-like text for any topic.",
         "large language model": "A Large Language Model (LLM) is trained on billions of text documents to understand and generate language. Modern LLMs use transformer architecture and can perform diverse tasks including question answering, translation, and code generation.",
         "transformer": "Transformers use attention mechanisms to model relationships between all input positions simultaneously and are the basis for modern large language models. They excel at processing sequential data like text.",
         "attention": "Attention mechanisms score how much each input token should contribute when computing representations; they enable transformers to focus on relevant context across the entire sequence.",
         "rag": "RAG (Retrieval-Augmented Generation) is an AI technique that combines retrieval and generation: it searches a knowledge base or documents to find relevant context, then uses an LLM to generate answers based on that retrieved information. This improves accuracy and allows AI to answer questions about specific documents.",
         "retrieval augmented generation": "Retrieval-Augmented Generation (RAG) retrieves relevant documents or data from a knowledge base and feeds them to an LLM to generate informed responses. It enables AI systems to answer questions grounded in specific sources rather than relying only on training data.",
         "langchain": "LangChain is an open-source framework for building applications powered by large language models (LLMs). It provides tools and abstractions to integrate LLMs with external data sources, APIs, and other components for creating AI-powered applications.",
         "nlp": "Natural Language Processing (NLP) is the branch of AI that deals with interactions between computers and human language. Tasks include translation, sentiment analysis, question answering, and text classification.",
         "computer vision": "Computer vision is the field of AI focused on enabling computers to interpret and understand visual information from images and videos, enabling tasks like object detection, facial recognition, and image classification.",
         "supervised learning": "Supervised learning trains models on labeled data (inputs paired with correct outputs). Common tasks are classification (predicting categories) and regression (predicting numeric values).",
         "unsupervised learning": "Unsupervised learning finds structure in unlabeled data through clustering (grouping similar items) and dimensionality reduction (simplifying high-dimensional data).",
         "reinforcement learning": "Reinforcement learning trains an agent to make sequences of decisions by rewarding desired behaviors and penalizing bad ones; commonly used in robotics, game-playing, and control systems.",

         # === Programming & Software Development ===
         "python": "Python is a high-level, interpreted programming language known for simplicity and readability. It is widely used in data science, machine learning, web development, automation, and scripting.",
         "java": "Java is an object-oriented, strongly-typed programming language designed for portability across platforms. It is widely used in enterprise applications, Android development, and large-scale systems.",
         "javascript": "JavaScript is a lightweight, interpreted language primarily used for web development. It runs in browsers and can also run on servers using Node.js, enabling full-stack web development.",
         "c plus plus": "C++ is a compiled, low-level programming language offering high performance and fine-grained memory control. It is used in systems software, game engines, and performance-critical applications.",
         "sql": "SQL (Structured Query Language) is used to query and manage relational databases. Common operations include SELECT (retrieve), INSERT (add), UPDATE (modify), and DELETE (remove) records.",
         "function": "A function is a reusable block of code that performs a specific task. Functions improve code readability, reduce duplication, and enable modular programming.",
         "loop": "Loops are control structures that repeat a block of code multiple times. Common types are for loops (fixed iterations) and while loops (condition-based).",
         "variable": "A variable is a named container that stores data values. Variables have names, types, and scopes; they enable storing and manipulating information in programs.",
         "array": "An array is an ordered collection of elements (typically of the same type) accessed by numeric indices. Arrays are fundamental for storing and processing lists of data efficiently.",
         "object oriented": "Object-oriented programming (OOP) organizes code into objects (instances of classes) that combine data and methods. Key principles are encapsulation, inheritance, and polymorphism.",
         "database": "A database is an organized collection of structured data stored for efficient retrieval and management. Relational databases use tables; NoSQL databases offer flexible schemas.",
         "api": "An API (Application Programming Interface) is a set of rules that allows different software applications to communicate and exchange data. APIs enable integration between systems.",
         "rest": "REST (Representational State Transfer) is an architectural style for building web services using HTTP methods (GET, POST, PUT, DELETE) to operate on resources identified by URLs.",
         "cloud computing": "Cloud computing is the delivery of computing services (compute, storage, networking) over the internet from remote servers. Common providers are AWS, Azure, and Google Cloud.",

         # === IT & Systems ===
         "cybersecurity": "Cybersecurity is the practice of protecting computer systems, networks, and data from unauthorized access, theft, or damage. It includes firewalls, encryption, authentication, and incident response.",
         "firewall": "A firewall is a network security system that monitors and filters incoming and outgoing network traffic. It blocks unauthorized access while allowing legitimate traffic.",
         "encryption": "Encryption converts readable data (plaintext) into unreadable code (ciphertext) using mathematical algorithms and keys. Only those with the correct key can decrypt the data.",
         "network": "A computer network is a collection of interconnected devices (computers, servers, etc.) that share resources and communicate. Types include LAN (local), WAN (wide), and the internet.",
         "server": "A server is a computer or software that provides resources, services, or data to client computers over a network. Examples are web servers, mail servers, and database servers.",
         "operating system": "An operating system (OS) is system software that manages hardware resources and enables user and application software to run. Examples are Windows, macOS, Linux, and Android.",
         "virtual machine": "A virtual machine (VM) is software that simulates a complete computer, allowing multiple OS instances to run on a single physical machine, improving resource utilization.",
         "kubernetes": "Kubernetes is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications across clusters of machines.",
         "docker": "Docker is a containerization platform that packages applications with their dependencies into lightweight, portable containers. Containers ensure consistency across different environments.",
         "git": "Git is a distributed version control system used to track code changes, enable collaboration, and manage project history. It supports branching, merging, and reverting changes.",

         # === Web Development ===
         "html": "HTML (HyperText Markup Language) is the standard markup language for creating web pages. It uses tags to define structure and content like headings, paragraphs, links, and images.",
         "css": "CSS (Cascading Style Sheets) is used to style and layout web pages. It controls colors, fonts, spacing, positioning, and responsive design across different screen sizes.",
         "react": "React is a JavaScript library for building user interfaces using reusable components. It uses a virtual DOM for efficient rendering and supports state management.",
         "vue": "Vue.js is a progressive JavaScript framework for building user interfaces. It offers simplicity and reactivity, making it popular for both small and large-scale applications.",
         "angular": "Angular is a full-featured JavaScript framework maintained by Google for building dynamic web applications. It includes routing, forms, and HTTP client utilities.",
         "node.js": "Node.js is a JavaScript runtime that allows running JavaScript outside the browser, typically on servers. It is widely used for building backend services and APIs.",
         "web development": "Web development is the process of creating and maintaining websites and web applications. It involves frontend (user interface), backend (server logic), and database design.",
         "responsive design": "Responsive design is an approach to web design that makes websites adapt to different screen sizes and devices, providing an optimal viewing experience on mobile, tablet, and desktop.",

         # === Finance & Loans ===
         "loan": "A loan is money borrowed from a lender that must be repaid with interest over time. Types include personal loans, mortgages, auto loans, and student loans.",
         "loan offer": "A loan offer specifies the amount, interest rate, term length (duration), monthly payment, and fees. Before accepting, compare offers and calculate the total cost.",
         "interest rate": "An interest rate is the percentage of the loan amount charged by the lender as the cost of borrowing. Higher rates mean higher total repayment; fixed rates stay constant, variable rates change.",
         "credit score": "A credit score (typically 300-850) reflects your creditworthiness based on payment history, debt levels, and credit inquiries. Higher scores get better loan rates.",
         "mortgage": "A mortgage is a long-term loan used to purchase real estate (homes). It is typically repaid over 15-30 years with monthly installments including principal and interest.",
         "investment": "Investment is allocating money into assets (stocks, bonds, real estate) with the goal of generating returns over time. Investments involve risk but offer potential for wealth growth.",
         "stock market": "The stock market is a platform where shares of publicly-traded companies are bought and sold. Stock prices fluctuate based on company performance and market conditions.",
         "budgeting": "Budgeting is planning how to allocate income to expenses, savings, and investments. A good budget helps control spending and build financial security.",

         # === General Knowledge ===
         "quantum computing": "Quantum computing uses quantum bits (qubits) instead of classical bits, leveraging quantum mechanics to solve complex problems exponentially faster than classical computers. Applications include cryptography, optimization, and drug discovery.",
         "future of it": "The future of IT includes AI/ML integration, cloud-native architectures, edge computing, cybersecurity advancement, quantum computing, blockchain, and increased automation.",
         "blockchain": "Blockchain is a distributed ledger technology that records transactions in blocks linked cryptographically. It enables transparency and security in cryptocurrencies and other applications.",
         "cryptocurrency": "Cryptocurrency is digital money using cryptography for security. Bitcoin and Ethereum are popular examples; transactions are recorded on a blockchain.",
         "internet of things": "The Internet of Things (IoT) is a network of physical devices embedded with sensors and connectivity, enabling them to collect and exchange data over the internet.",
         "5g": "5G is the fifth generation of cellular network technology offering faster speeds (up to 10 Gbps), lower latency, and improved connectivity compared to 4G LTE.",
         "augmented reality": "Augmented Reality (AR) overlays digital content onto the real world using cameras and displays. Applications include mobile games, navigation, and industrial training.",
         "virtual reality": "Virtual Reality (VR) creates immersive 3D digital environments that users experience through headsets. Applications include gaming, training, and virtual tourism.",
         "big data": "Big data refers to very large and complex datasets that exceed traditional data processing capabilities. It involves volume, velocity, and variety; analyzed using specialized tools and ML.",
         "algorithm": "An algorithm is a step-by-step procedure or formula for solving a problem or performing a task. Algorithms are fundamental to computer science and software development.",
         "data structure": "A data structure is a way of organizing and storing data to enable efficient access and modification. Examples include arrays, linked lists, trees, graphs, and hash tables.",
         "time complexity": "Time complexity measures how an algorithm's runtime grows with input size. Common notations are O(1) constant, O(n) linear, O(n^2) quadratic, O(log n) logarithmic.",
         "debugging": "Debugging is the process of identifying, analyzing, and fixing bugs (errors) in software. Techniques include logging, breakpoints, stepping through code, and code review.",

         # === Career & Personal ===
         "your name": "I am Jarvis, your voice assistant.",
         "who made": "I was created as a Python-based voice assistant project.",
         "what can you do": "I can answer questions on AI, ML, IT, programming, databases, web development, finance, tell you the time and date, check weather, read news, open websites, play music, and more.",
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.date.today().isoformat(),
    }

    # First try EXACT word boundary matches (words not substrings of other words)
    # Sort by key length DESC so longer, more specific keys match first
    sorted_keys = sorted(offline_knowledge.keys(), key=lambda x: len(x), reverse=True)
    
    for key in sorted_keys:
        # Match if key is a separate word or phrase in the query
        key_words = key.split()
        query_words = q_lower.split()
        
        # Clean query words by removing punctuation
        import string
        query_words_clean = [word.strip(string.punctuation) for word in query_words]
        
        # If all words in the key appear in the query (order-independent), it's a match
        key_set = set(key_words)
        query_set = set(query_words_clean)
        if key_set.issubset(query_set):
            if DEBUG:
                print(f"Responder=OFFLINE key={key}")
            answer = offline_knowledge[key]
            if answer and isinstance(answer, str):
                speak(answer)
            return

    # Skip local doc search - it causes false positives
    # Instead, try fuzzy matching for similar offline keys
    try:
        from difflib import get_close_matches

        candidates = list(offline_knowledge.keys())
        closest = get_close_matches(q_lower, candidates, n=1, cutoff=0.6)
        if closest:
            if DEBUG:
                print(f"Responder=OFFLINE fuzzy={closest[0]}")
            speak(offline_knowledge[closest[0]])
            return
    except Exception:
        pass

    # No match in offline knowledge - try Wikipedia or let caller handle it
    try:
        if (q_lower.startswith("what is") or q_lower.startswith("who is") or q_lower.startswith("define")) and len(q_lower.split()) <= 10:
            topic = q_lower.replace("what is", "").replace("who is", "").replace("define", "").strip()
            if topic:
                try:
                    summary = wikipedia.summary(topic, sentences=2)
                    if summary:
                        if DEBUG:
                            print("Responder=WIKIPEDIA")
                        speak(summary)
                        return
                except Exception:
                    pass
    except Exception:
        pass

    if DEBUG:
        print("Responder=NONE")
    speak("I don't have that information available offline right now. Try asking about AI, machine learning, programming, databases, web development, IT, finance, or what I can do.")


def _search_local_docs(query, max_snippets=3):
    """Search local markdown/text files for lines or paragraphs matching query tokens.
    
    Uses word-boundary matching and stop-word filtering to prevent false positives.
    Returns a short concatenated snippet or empty string.
    """
    try:
        q_lower = query.lower()
        snippets = []
        base = pathlib.Path(__file__).parent
        patterns = ["README.md", "*.md", "Documentation/*.md", "*.txt"]
        seen = set()
        
        # Stop words to exclude from matching
        stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'in', 'of', 'to', 'for', 'from', 'be', 'that', 'with', 'as', 'by', 'at', 'on', 'it', 'this', 'was', 'are', 'were', 'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'could'}
        
        # Get meaningful query tokens (length > 3 and not stop words)
        q_tokens = set([t for t in q_lower.split() if len(t) > 3 and t not in stop_words])
        
        if not q_tokens:
            return ""
        
        for pat in patterns:
            for path in base.glob(pat):
                try:
                    text = path.read_text(encoding="utf-8")
                except Exception:
                    continue
                # split into paragraphs
                for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
                    pl = para.lower()
                    # Use word-boundary matching: all meaningful query tokens must appear as whole words
                    para_tokens = set([t for t in pl.split() if len(t) > 3 and t not in stop_words])
                    
                    # Check if query tokens are word boundaries in the paragraph
                    token_matches = 0
                    for qt in q_tokens:
                        # Check if query token appears as a whole word in any paragraph token
                        if any(qt in pt for pt in para_tokens):
                            token_matches += 1
                    
                    # Require at least 50% of query tokens to match
                    if token_matches >= len(q_tokens) * 0.5:
                        key = (path.as_posix(), para[:200])
                        if key in seen:
                            continue
                        seen.add(key)
                        snippets.append(f"From {path.name}: {para.strip()}")
                        if len(snippets) >= max_snippets:
                            break
                if len(snippets) >= max_snippets:
                    break
            if len(snippets) >= max_snippets:
                break

        if snippets:
            # Return best matching snippet
            best = snippets[0]
            # truncate long paragraphs for voice
            if len(best) > 800:
                best = best[:800].rsplit('.', 1)[0] + '.'
            return best
    except Exception:
        return ""
    return ""


def answer_with_gpt(query):
    global gpt_retry_after
    # Prefer Ollama for offline-first answers. If Ollama replies, return immediately.
    try:
        if answer_with_ollama(query):
            return
    except Exception:
        pass

    if gpt_retry_after is not None and datetime.datetime.now() < gpt_retry_after:
        answer_with_offline_model(query)
        return

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    # If no OpenAI key is present, continue with offline fallback after Ollama
    if not api_key:
        answer_with_offline_model(query)
        return

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    openai.api_key = api_key
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    system_prompt = (
        "You are Jarvis, an advanced voice assistant. "
        "Answer tough questions carefully and directly. "
        "If a question is ambiguous, ask one short clarifying question instead of guessing. "
        "If the answer is technical, explain it clearly and accurately. "
        "Keep answers concise for voice, but include enough detail to be useful."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Current date and time: {current_time}."},
    ]

    messages.extend(_trim_chat_history(chat_history))
    messages.append({"role": "user", "content": query})

    client = _create_openai_client(api_key)
    last_error = None

    if client is not None:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=180,
            )
            answer = _extract_chat_text(response)
            if answer:
                chat_history.append({"role": "user", "content": query})
                chat_history.append({"role": "assistant", "content": answer})
                del chat_history[:-12]
                speak(answer)
                return
        except Exception as error:
            last_error = error

    try:
        prompt = (
            "You are Jarvis, an advanced voice assistant. Answer the question clearly, accurately, and directly.\n\n"
            f"Question: {query}\nAnswer:"
        )
        if client is not None and hasattr(client, "completions"):
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=180,
                temperature=0.1,
            )
            answer = _extract_completion_text(response)
        else:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=180,
                temperature=0.1,
            )
            answer = response["choices"][0]["text"].strip()
        if answer:
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": answer})
            del chat_history[:-12]
            speak(answer)
            return
    except Exception as error:
        if last_error is None:
            last_error = error

    if last_error is not None:
        print(f"GPT error: {last_error}")
        error_text = str(last_error).lower()
        if "quota" in error_text or "billing" in error_text or "rate limit" in error_text:
            gpt_retry_after = datetime.datetime.now() + datetime.timedelta(hours=2)
        
        # Try Ollama if OpenAI fails
        if answer_with_ollama(query):
            return
        
        # Fall back to rule-based offline
        answer_with_offline_model(query)
        return

    # No error but no response; try Ollama then offline fallback
    if answer_with_ollama(query):
        return
    
    answer_with_offline_model(query)


def process_query(query):
    if not query:
        return

    text = query.lower().strip()

    if text in {"stop", "exit", "quit", "bye", "close"}:
        speak("Goodbye.")
        sys.exit(0)

    if "help" in text:
        speak(
            "Try saying Wikipedia, open YouTube, search Google, play music, weather, news, time, date, battery, system info, or ask a question."
        )
        return

    # Only use Wikipedia when the user explicitly asks for it.
    if "wikipedia" in text or text.startswith("who is"):
        topic = text.replace("wikipedia", "").replace("who is", "").strip()
        if not topic:
            speak("What should I search on Wikipedia?")
            topic = listen_for_command()
        if topic:
            try:
                result = wikipedia.summary(topic, sentences=2)
                speak(result)
                return
            except Exception:
                pass

    if "open youtube" in text:
        open_site("YouTube", "https://www.youtube.com")
        return

    if "open google" in text:
        open_site("Google", "https://www.google.com")
        return

    if "open instagram" in text:
        open_site("Instagram", "https://www.instagram.com")
        return

    if "open facebook" in text:
        open_site("Facebook", "https://www.facebook.com")
        return

    if "open whatsapp" in text:
        open_site("WhatsApp", "https://web.whatsapp.com")
        return

    if "search youtube" in text:
        speak("What should I search on YouTube?")
        search_term = listen_for_command()
        if search_term:
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            )
        return

    if "search google" in text or ("google" in text and "search" in text):
        speak("What should I search on Google?")
        search_term = listen_for_command()
        if search_term:
            webbrowser.open(
                f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            )
        return

    if text.startswith("play ") or text == "play":
        song = text.replace("play", "", 1).strip()
        if not song:
            speak("What should I play?")
            song = listen_for_command()
        if song:
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)
        return

    if "time" in text:
        speak(datetime.datetime.now().strftime("%H:%M:%S"))
        return

    if "date" in text:
        speak(datetime.date.today().isoformat())
        return

    if "joke" in text:
        speak(pyjokes.get_joke())
        return

    if "weather" in text:
        speak("Which city?")
        city = listen_for_command()
        if city:
            get_weather(city)
        return

    if "news" in text:
        read_news()
        return

    if "system" in text:
        system_info()
        return

    if "battery" in text:
        battery = psutil.sensors_battery()
        if battery is None:
            speak("Battery information is unavailable.")
        else:
            speak(f"Battery is at {battery.percent} percent.")
        return

    if "volume up" in text and pyautogui is not None:
        pyautogui.press("volumeup")
        speak("Volume increased.")
        return

    if "volume down" in text and pyautogui is not None:
        pyautogui.press("volumedown")
        speak("Volume decreased.")
        return

    if "mute" in text and pyautogui is not None:
        pyautogui.press("volumemute")
        speak("Muted.")
        return

    if "brightness" in text:
        if sbc is None:
            speak("Brightness control is unavailable here.")
            return
        speak("What brightness level should I set?")
        try:
            level = int(listen_for_command())
            sbc.set_brightness(level)
            speak(f"Brightness set to {level} percent.")
        except Exception:
            speak("I could not change brightness.")
        return

    if "screenshot" in text:
        if pyautogui is None:
            speak("Screenshot capture is unavailable here.")
            return
        filename = f"screenshot_{int(datetime.datetime.now().timestamp())}.png"
        pyautogui.screenshot(filename)
        speak(f"Screenshot saved as {filename}.")
        return

    if "ip address" in text:
        ip = requests.get("https://api.ipify.org").text
        speak(f"Your IP address is {ip}")
        return

    if "open" in text:
        targets = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.x.com",
            "linkedin": "https://www.linkedin.com",
            "reddit": "https://www.reddit.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "whatsapp": "https://web.whatsapp.com",
        }
        for key, url in targets.items():
            if key in text:
                open_site(key.capitalize(), url)
                return

    answer_with_gpt(query)


def main():
    wish_me()
    while True:
        query = listen_for_command()
        if not query:
            continue
        process_query(query)


if __name__ == "__main__":
    main()