import os
from groq import Groq

# Directly pass the API key (for testing only, NOT recommended for production)
client = Groq(api_key="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")

def generate_prompt():
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Generate an insightful query for researching the growth rate of company with regards to saleshow it has been performing marginal improvements capex differences",
                }
            ],
            model="llama-3.3-70b-versatile",  # Ensure this model is available
            stream=False,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    prompt_text = generate_prompt()
    print("Generated Prompt:", prompt_text)
