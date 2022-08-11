import json
import redis


def update_user_last_question(database: redis, question: str, user_id: str):
    get_users_with_questions = database.get("users").decode()
    authorized_users = json.loads(get_users_with_questions)
    if authorized_users.get(user_id):
        authorized_users[user_id]["last_asked_question"] = question
    else:
        new_user = {
            user_id: {
                "last_asked_question": question,
                "count": 0,
            }
        }
        authorized_users.update(new_user)
    user_json = json.dumps(authorized_users, ensure_ascii=True)

    database.set("users", user_json)
