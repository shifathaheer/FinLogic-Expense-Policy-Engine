import json
from pathlib import Path


def load_policy(file_path="data/policy.json"):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Policy file not found!")

    with open(path, "r") as file:
        policy = json.load(file)

    return policy