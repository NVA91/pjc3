import anthropic

client = anthropic.Anthropic()
conversation_history = []

system = "You are a helpful assistant. Be concise and friendly."

print("Chatbot gestartet. Tippe 'quit' zum Beenden.\n")

while True:
    user_input = input("Du: ").strip()

    if not user_input:
        continue
    if user_input.lower() in ("quit", "exit", "bye"):
        print("Tschüss!")
        break

    conversation_history.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        system=system,
        messages=conversation_history,
        max_tokens=500
    )

    reply = response.content[0].text
    print(f"Claude: {reply}\n")
    conversation_history.append({"role": "assistant", "content": reply})
