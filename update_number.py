#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    with open("number.txt", "r") as f:
        return int(f.read().strip())


def write_number(num):
    with open("number.txt", "w") as f:
        f.write(str(num))


def read_last_commit_date():
    with open("last_commit_date.txt", "r") as f:
        return datetime.strptime(f.read().strip(), "%Y-%m-%d")


def write_last_commit_date(date):
    with open("last_commit_date.txt", "w") as f:
        f.write(date.strftime("%Y-%m-%d"))


def generate_random_commit_message():
    from transformers import pipeline

    generator = pipeline(
        "text-generation",
        model="openai-community/gpt2",
    )
    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject. Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message:
    """
    generated = generator(
        prompt,
        max_new_tokens=50,
        num_return_sequences=1,
        temperature=0.9,  # Slightly higher for creativity
        top_k=50,  # Limits sampling to top 50 logits
        top_p=0.9,  # Nucleus sampling for diversity
        truncation=True,
    )
    text = generated[0]["generated_text"]

    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        raise ValueError(f"Unexpected generated text {text}")


def git_commit(date):
    commit_message = f"Update number: {date.strftime('%Y-%m-%d')}"
    subprocess.run(["git", "add", "number.txt"])
    subprocess.run(["git", "commit", "-m", commit_message])


def git_push():
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def get_commits_for_missing_days():
    last_commit_date = read_last_commit_date()
    today = datetime.now()
    delta = today - last_commit_date
    commit_dates = []

    for i in range(delta.days):
        commit_dates.append(today - timedelta(days=i))

    return commit_dates


def main():
    try:
        commit_dates = get_commits_for_missing_days()  # Получаем список пропущенных дней
        for date in commit_dates:
            current_number = read_number()
            new_number = current_number + 1
            write_number(new_number)
            git_commit(date)  # Коммитим с нужной датой
            write_last_commit_date(date)  # Обновляем дату последнего коммита

        git_push()  # После всех коммитов пушим на GitHub
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
