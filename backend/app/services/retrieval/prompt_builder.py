
SYSTEM_PROMPT = (
    "You are an expert AI/ML Professor teaching computer science students at a top Indian engineering college.\n\n"

    "Your task is to explain AI/ML research papers in a simple, educational, and technically accurate manner.\n\n"

    "Rules:\n"
    "1. Write in natural educational Hinglish using ONLY the Roman (Latin) script. Never use Devanagari.\n"
    "2. Maintain a professional classroom teaching style. Avoid slang or casual internet language.\n"
    "3. Keep all AI/ML technical terms in English (e.g., Transformer, Gradient Descent, Backpropagation, Loss Function, Attention, Embedding).\n"
    "4. Explain concepts with intuition first before mentioning technical details whenever appropriate.\n"
    "5. Base every explanation only on the provided Research Paper Context. Never invent results, datasets, experiments, or metrics.\n"
    "6. If the Research Paper Context does not contain enough information to answer the user's question, reply exactly with:\n"
    "'I couldn't find this information in the uploaded research paper.'\n"
    "7. Keep explanations well-structured with short paragraphs for readability."
)

GENERAL_SYSTEM_PROMPT=(
                  "You are an expert AI/ML Professor teaching computer science students at a top Indian engineering college.\n\n"
    "Rules:\n"
    "1. Write in natural educational Hinglish using ONLY the Roman (Latin) script. Never use Devanagari.\n"
    "2. Maintain a professional classroom teaching style. Avoid slang or casual internet language.\n"
    "3. Keep all AI/ML technical terms in English (e.g., Transformer, Gradient Descent, Backpropagation, Loss Function, Attention, Embedding).\n"
    "4. Explain concepts clearly with intuition first before technical details.\n"
    "5. Keep explanations well-structured with short paragraphs."

)
#--------for general user query without pdf----------#
def build_general_prompt( query: str,chat_history: list[dict] = None) -> list[dict]:

    messages = [
        {
            "role": "system",
            "content": GENERAL_SYSTEM_PROMPT,
        }
    ]

    if chat_history:
        for msg in chat_history[-4:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

    messages.append({
        "role": "user",
        "content": query,
    })

    return messages




#------------for rag phase---------------#
def build_prompt(query: str, reranked_docs: list[dict], chat_history: list[dict] = None) -> list[dict]:
    
    # 1. Safely extract and flatten candidate text chunks using .get() to avoid KeyErrors
    context_str = "\n\n".join(
        [f"[Source: {doc.get('source', 'Unknown')}, Page: {doc.get('page', 1)}]: {doc.get('text', '')}" 
         for doc in reranked_docs]
    )
    
    # 2. Initialize the chat message array beginning with  academic persona instruction
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
    
    # 3. Dynamic Sliding Window: If chat history is present, slice and append the last 4 interactions
    if chat_history:
        # Appends the conversation chronologically right before the new task sequence
        for msg in chat_history[-4:]:
            messages.append({
              "role": msg.get("role", "user"),
              "content": msg.get("content", "")
})
            
    # 4. Construct the current user execution context matching the fine-tuning token signatures
    user_payload = (
        f"Task:\n{query}\n\n"
        f"Research Paper Context:\n{context_str if context_str else 'No relevant context found.'}"
    )
    
    messages.append({
        "role": "user",
        "content": user_payload
    })
    
    return messages
#this messages will be given to llm_service these are in qwen-chatml format
   
   