from app.core.app_state import state


class MemoryService:

    def build_history(self):

        history = ""

        for chat in state.conversation_history[-5:]:

            history += f"""
User:
{chat['question']}

Assistant:
{chat['answer']}
"""

        return history

    def save_conversation(
        self,
        question,
        answer,
    ):

        state.conversation_history.append(
            {
                "question": question,
                "answer": answer,
            }
        )

        state.conversation_history = (
            state.conversation_history[-10:]
        )


memory_service = MemoryService()