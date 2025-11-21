import os
import sys
import json
import requests


def get_groups(user_id: str, token: str):
    url = f'https://api.vk.com/method/groups.get?user_id={user_id}&extended=1&access_token={token}&v=5.199'
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Error executing request to {url}: {response.status_code}')
        sys.exit(1)

    return response.json()


def write_json(data: dict):
    output_dir = 'result'
    output_file = 'result.json'
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, output_file)
    with open(file_path, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    user_id = ''
    token = ''
    groups = get_groups(user_id, token)
    write_json(groups)


if __name__ == '__main__':
    main()
