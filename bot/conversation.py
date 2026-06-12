from collections import defaultdict

# хранилище историй: user_id -> list of dicts
histories = defaultdict(list)

def add_to_history(user_id: int, role: str, content: str, max_history: int):
    histories[user_id].append({"role": role, "content": content})
    if len(histories[user_id]) > max_history:
        histories[user_id] = histories[user_id][-max_history:]

def get_history(user_id: int) -> list:
    return histories.get(user_id, [])

def reset_history(user_id: int):
    histories[user_id] = []