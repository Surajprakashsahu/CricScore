import ollama

# Send a single text prompt
import ollama

# The model must be a multimodal one, like gemma3 or llava
# Make sure you have the model pulled: `ollama pull gemma3:4b`
response = ollama.chat(
    model='gemma3:4b', 
    messages=[
        {
            'role': 'user', 
            'content': 'What is this image about? Give me a detailed description.',
            'images': ['/Users/surabhibehera/Downloads/Aligners-India.jpg']  # Replace with the actual image path
        }
    ]
)
print(response['message']['content'])