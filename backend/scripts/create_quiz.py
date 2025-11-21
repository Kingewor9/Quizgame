#!/usr/bin/env python3
"""
Admin CLI to create quizzes by POSTing a JSON payload to the backend.

Usage:
  - Provide a JSON file: python create_quiz.py --file path/to/quiz.json
  - Or run without args to create interactively: python create_quiz.py

The script expects the backend to be available at http://localhost:8000 by default.
"""
import argparse
import json
import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

SAMPLE_PROMPT = "Enter value (leave blank to accept default)"


def post_quiz(payload, api_base=API_BASE):
    url = f"{api_base}/api/quizzes"
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        print("Quiz created:")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def load_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def interactive():
    print("Interactive quiz creation — you can also provide a JSON file with --file")
    title = input("Quiz title: ").strip()
    if not title:
        title = "Untitled Quiz"

    duration = input(f"Duration seconds [{90}]: ").strip() or "90"
    try:
        duration = int(duration)
    except:
        duration = 90

    # default start now, end in 7 days
    start_default = datetime.utcnow().isoformat()
    end_default = (datetime.utcnow() + timedelta(days=7)).isoformat()
    start = input(f"Start ISO datetime [{start_default}]: ").strip() or start_default
    end = input(f"End ISO datetime [{end_default}]: ").strip() or end_default

    questions = []
    qcount = input("Number of questions [3]: ").strip() or "3"
    try:
        qcount = int(qcount)
    except:
        qcount = 3

    for i in range(1, qcount + 1):
        print(f"\nQuestion {i}")
        text = input("Text: ").strip() or f"Question {i}"
        opts_raw = input("Options (separate by |) e.g. Option1|Option2|Option3: ").strip()
        if not opts_raw:
            options = ["A", "B", "C", "D"]
        else:
            options = [s.strip() for s in opts_raw.split('|') if s.strip()]
        for idx, o in enumerate(options):
            print(f"  {idx}: {o}")
        ans = input(f"Correct option index [0]: ").strip() or "0"
        try:
            ans = int(ans)
        except:
            ans = 0
        qid = f"q{i}"
        questions.append({
            'id': qid,
            'text': text,
            'options': options,
            'answerIndex': ans
        })

    payload = {
        'title': title,
        'questions': questions,
        'durationSeconds': duration,
        'startDate': start,
        'endDate': end
    }
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='Path to quiz JSON file')
    parser.add_argument('--api', help='API base URL', default=API_BASE)
    args = parser.parse_args()

    if args.file:
        payload = load_from_file(args.file)
        print(f"Loaded quiz from {args.file}")
    else:
        payload = interactive()

    print('\nQuiz payload:')
    print(json.dumps(payload, indent=2))
    confirm = input('Send to server? (y/N): ').strip().lower()
    if confirm == 'y':
        post_quiz(payload, api_base=args.api)
    else:
        print('Aborted')


if __name__ == '__main__':
    main()
