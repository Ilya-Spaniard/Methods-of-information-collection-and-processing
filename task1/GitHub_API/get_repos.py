import requests
import json

def get_repos(owner: str):
    url = f"https://api.github.com/users/{owner}/repos"
    return requests.get(url)

def write_json(data: dict, file_name: str):
    with open(file_name, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    owner = ''
    output_json = 'repos.json'

    repos = get_repos(owner)
    print(repos.json())
    write_json(repos.json(), output_json)
 
if __name__ == "__main__":
	main()