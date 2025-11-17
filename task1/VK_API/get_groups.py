import requests
import json

def get_groups(user_id: str, token: str):
    url = f"https://api.vk.com/method/groups.get?user_id={user_id}&extended=1&access_token={token}&v=5.199"
    return requests.get(url)

def write_json(data: dict, file_name: str):
    with open(file_name, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    user_id = ''
    token = ''
    output_json = 'groups.json'

    groups = get_groups(user_id, token)
    write_json(groups.json(), output_json)
 
if __name__ == "__main__":
	main()