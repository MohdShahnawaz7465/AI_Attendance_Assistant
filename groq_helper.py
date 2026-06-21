import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_ai(question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    user_question = input("Ask AI: ")
    answer = ask_ai(user_question)
    print(answer)