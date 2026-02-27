import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


def generate_questions(topic, num_questions=3):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=f"You are an expert on {topic}. Generate thought-provoking questions about this topic.",
        messages=[
            {"role": "user", "content": f"Generate {num_questions} questions about {topic} as a numbered list."}
        ],
        stop_sequences=[f"{num_questions + 1}."]
    )
    print(response.content[0].text)


if __name__ == "__main__":
    generate_questions(topic="free will", num_questions=3)
