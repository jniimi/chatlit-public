import google.generativeai as genai


def get_response_chatgpt(prompt, messages, client, model_id):
    """Get response from ChatGPT"""
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model_id, 
        messages=messages
    )
    return response.choices[0].message.content


def get_response_claude(prompt, messages, client, model_id):
    """Get response from Claude"""
    claude_messages = []
    for msg in messages:
        if msg["role"] == "user":
            claude_messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            claude_messages.append({"role": "assistant", "content": msg["content"]})
    claude_messages.append({"role": "user", "content": prompt})
    
    response = client.messages.create(
        model=model_id,
        max_tokens=4000,
        messages=claude_messages
    )
    return response.content[0].text


def get_response_gemini(prompt, messages, model_id):
    """Get response from Gemini"""
    model = genai.GenerativeModel(model_id)
    
    conversation_history = []
    for msg in messages[:-1]:
        conversation_history.append(f"{msg['role'].title()}: {msg['content']}")
    
    if conversation_history:
        full_prompt = "\n".join(conversation_history) + f"\nUser: {prompt}\nAssistant:"
    else:
        full_prompt = prompt
    
    response = model.generate_content(full_prompt)
    return response.text