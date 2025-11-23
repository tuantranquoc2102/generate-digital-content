import os
import openai
from typing import Optional

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def format_as_dialogue(text: str) -> str:
    """
    Format transcription text as dialogue between two speakers
    Returns formatted text in format: Speaker1: text; Speaker2: text
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert at formatting transcribed audio into natural dialogue.
                    
Your task:
1. Identify different speakers in the transcription
2. Format as dialogue with speaker labels
3. Use format: Speaker1: text; Speaker2: text
4. Make the dialogue natural and conversational
5. Preserve the original meaning and content

Guidelines:
- Use "Speaker1:", "Speaker2:" etc. as labels
- Separate each speaker's turn with semicolon (;)
- Keep the content accurate to original
- Make it flow naturally as conversation
- If it's clearly one person speaking, format as "Speaker1: [entire text]"
"""
                },
                {
                    "role": "user", 
                    "content": f"Format this transcription as dialogue:\n\n{text}"
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI formatting failed: {str(e)}")

def generate_image_prompt(dialogue_text: str) -> str:
    """
    Generate a detailed image prompt from dialogue text
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Create a detailed, vivid image prompt based on dialogue text.
                    
Your task:
1. Analyze the dialogue content and context
2. Create a visual scene description
3. Include setting, characters, mood, atmosphere
4. Make it suitable for DALL-E image generation
5. Keep it under 400 characters

Guidelines:
- Describe the scene, not the conversation
- Include visual details (lighting, colors, setting)
- Make it cinematic and engaging
- Avoid text or speech bubbles
- Focus on the mood and atmosphere of the conversation
"""
                },
                {
                    "role": "user",
                    "content": f"Create an image prompt for this dialogue:\n\n{dialogue_text[:1000]}"
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"A scene depicting: {dialogue_text[:200]}..."

def generate_image_with_dalle(prompt: str) -> str:
    """
    Generate image using DALL-E
    Returns URL of generated image
    """
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        return response.data[0].url
    except Exception as e:
        raise Exception(f"DALL-E image generation failed: {str(e)}")