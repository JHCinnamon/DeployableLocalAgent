import argparse
from datetime import datetime
from uuid import uuid4

import pandas as pd
from pydantic import BaseModel, Field
from timescale_vector.client import uuid_from_time

from database.vector_store import VectorStore
from services.llm_factory import LLMFactory


class ChatAnswer(BaseModel):
    answer: str = Field(description="Assistant reply to the user")


SYSTEM_PROMPT = """
You are a helpful AI assistant.

You are given:
- The current user message
- Retrieved long-term memory snippets from previous turns in this same conversation

Rules:
1. Use memory snippets when they are relevant and helpful.
2. If memory is not relevant, ignore it.
3. Do not invent facts that are not in the memory or current message.
4. Keep responses concise and practical.
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interactive chat with vector-based long-term memory."
    )
    parser.add_argument(
        "--conversation-id",
        default=str(uuid4()),
        help="Conversation ID used to group and retrieve memory turns.",
    )
    parser.add_argument(
        "--memory-limit",
        type=int,
        default=6,
        help="How many relevant past turns to retrieve per reply.",
    )
    return parser.parse_args()


def _memory_context_json(df: pd.DataFrame) -> str:
    if df.empty:
        return "[]"

    keep_columns = [c for c in ["content", "role", "created_at", "distance"] if c in df.columns]
    view = df[keep_columns].copy()
    return view.to_json(orient="records", indent=2)


def _store_turn(vec: VectorStore, conversation_id: str, role: str, text: str) -> None:
    now = datetime.now()
    contents = f"{role}: {text}"
    embedding = vec.get_embedding(contents)

    row = pd.DataFrame(
        [
            {
                "id": str(uuid_from_time(now)),
                "metadata": {
                    "source": "conversation",
                    "conversation_id": conversation_id,
                    "role": role,
                    "created_at": now.isoformat(),
                },
                "contents": contents,
                "embedding": embedding,
            }
        ]
    )
    vec.upsert(row)


def _generate_reply(vec: VectorStore, conversation_id: str, user_text: str, memory_limit: int) -> str:
    memory_df = vec.search(
        user_text,
        limit=memory_limit,
        metadata_filter={"source": "conversation", "conversation_id": conversation_id},
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "# Retrieved conversation memory\n" + _memory_context_json(memory_df),
        },
        {"role": "user", "content": user_text},
    ]

    llm = LLMFactory("openai")
    response = llm.create_completion(response_model=ChatAnswer, messages=messages)
    return response.answer


def main() -> None:
    args = parse_args()
    vec = VectorStore()
    vec.create_tables()

    print(f"Conversation ID: {args.conversation_id}")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_text = input("You: ").strip()
        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit"}:
            print("Bye.")
            break

        _store_turn(vec, args.conversation_id, "user", user_text)
        answer = _generate_reply(vec, args.conversation_id, user_text, args.memory_limit)
        _store_turn(vec, args.conversation_id, "assistant", answer)

        print(f"Assistant: {answer}\n")


if __name__ == "__main__":
    main()