import requests
import json
import yaml

GITLAB_API_URL = "https://gitlab.com/api/graphql"
GITLAB_ACCESS_TOKEN = "<YOUR_ACCESS_TOKEN>"
CONFIG_FILE = "settings_to_check.yaml"

def build_query(settings_to_check, after_cursor=None):
    fields = set()
    for setting in settings_to_check.keys():
        if setting != "topic":
            fields.add(setting.split(".")[0])
    fields_query = "\n      ".join(fields)

    pagination = f', after: "{after_cursor}"' if after_cursor else ""
    topic = settings_to_check.get("topic", "")
    topic_filter = f', topic: "{topic}"' if topic else ""

    query = f"""
    query {{
      projects(first: 100{topic_filter}{pagination}) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        nodes {{
          id
          name
          {fields_query}
        }}
      }}
    }}
    """
    return query

def load_settings(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def get_projects(query):
    headers = {
        "Authorization": f"Bearer {GITLAB_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(GITLAB_API_URL, headers=headers, json={"query": query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")

def check_project_settings():
    settings_to_check = load_settings(CONFIG_FILE)
    after_cursor = None
    all_projects = []

    while True:
        query = build_query(settings_to_check, after_cursor)
        data = get_projects(query)
        projects_data = data.get("data", {}).get("projects", {})
        projects = projects_data.get("nodes", [])
        all_projects.extend(projects)

        page_info = projects_data.get("pageInfo", {})
        if not page_info.get("hasNextPage", False):
            break
        after_cursor = page_info.get("endCursor")

    for project in all_projects:
        project_name = project["name"]
        errors = []

        for setting, expected_value in settings_to_check.items():
            if setting == "topic":
                continue
            keys = setting.split(".")
            value = project
            for key in keys:
                value = value.get(key, None)
                if value is None:
                    break
            if value != expected_value:
                errors.append(f"Setting '{setting}' is '{value}', expected '{expected_value}'")

        if errors:
            print(f"Project '{project_name}' has incorrect settings:\n" + "\n".join(errors))
        else:
            print(f"Project '{project_name}' has all correct settings.")

if __name__ == "__main__":
    check_project_settings()
