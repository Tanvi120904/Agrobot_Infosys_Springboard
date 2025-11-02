# chatbot_model.py
import random # Used to select a random response from a list [cite: 1, 2, 3]

# Agriculture chatbot responses
# This is a dictionary where each key is a category of questions [cite: 27, 28]
responses = {
    "greeting": [
        "Hello! I'm your agriculture assistant. 🌱 How can I help you today?", # [cite: 465]
        "Hi there! Ask me anything about farming and crops. 🚜 " # [cite: 466]
    ],
    "fertilizer": [
        "For better yield, use organic compost and nitrogen-rich fertilizer like urea.", # [cite: 469]
        "Consider using phosphorus and potassium-based fertilizers for root growth." # [cite: 470]
    ],
    "pest": [
        "Neem oil spray is effective for many pests.", # [cite: 473]
        "Introduce natural predators like ladybugs to control pest population." # [cite: 474]
    ],
    "weather": [
        "Please check the local forecast before sowing seeds.", # [cite: 477]
        "Avoid watering plants if heavy rain is predicted." # [cite: 478]
    ],
    "default": [
        "I'm not sure about that. Could you please rephrase?", # [cite: 481]
        "Sorry, I don't understand. Can you ask another question?" # [cite: 482]
    ]
}

def get_response(user_input):
    """
    Takes user input, checks for keywords, and returns a random response.
    """
    user_input = user_input.lower() # Convert input to lowercase for case-insensitive matching [cite: 40, 486]

    if "hello" in user_input or "hi" in user_input: # [cite: 487]
        return random.choice(responses["greeting"]) # [cite: 488]
    elif "fertilizer" in user_input: # [cite: 489]
        return random.choice(responses["fertilizer"]) # [cite: 490]
    elif "pest" in user_input: # [cite: 491]
        return random.choice(responses["pest"]) # [cite: 492]
    elif "weather" in user_input: # [cite: 493]
        return random.choice(responses["weather"]) # [cite: 494]
    else: # If no keyword is found [cite: 54]
        return random.choice(responses["default"]) # [cite: 496]