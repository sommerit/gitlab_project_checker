import requests
import json
import yaml
import os
import logging
from termcolor import colored

GITLAB_API_URL = "https://gitlab.com/api/graphql"
GITLAB_ACCESS_TOKEN = os.getenv("GITLAB_ACCESS_TOKEN")
CONFIG_FILE = "settings_to_check.yaml"

logging.basicConfig(level=logging.INFO)

def build_query(settings_to_check, after_cursor=None):
    fields = {}
    general_settings = settings_to_check.get("general", {})
    topics = general_settings.get("topics", "")
    query_topics = f', topics: "{topics}"' if topics else ""

    query_settings = settings_to_check.get("query", {})
    for setting in query_settings.keys():
        keys = setting.split(".")
        current = fields
        for key in keys:
            if key not in current:
                current[key] = {}
            current = current[key]

    def build_fields_query(fields_dict, indent=6):
        query_parts = []
        for key, subfields in fields_dict.items():
            if subfields:
                subfields_query = build_fields_query(subfields, indent + 2)
                query_parts.append(f"{key} {{\n{' ' * indent}{subfields_query}\n{' ' * (indent - 2)}}}")
            else:
                query_parts.append(key)
        return "\n".join(query_parts)

    fields_query = build_fields_query(fields)
    pagination = f', after: "{after_cursor}"' if after_cursor else ""

    query = f"""
    query {{
      projects(first: 100{query_topics}{pagination}) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        nodes {{
          id
          name
          fullPath
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

    if __name__ == "__main__" and '--debug' in os.sys.argv:
        logging.info(f"Executing query: {query}")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")

def check_project_settings():
    settings_to_check = load_settings(CONFIG_FILE)
    general_settings = settings_to_check.get("general", {})
    excluded_paths = general_settings.get("exclude", [])
    if excluded_paths:
        logging.info(f"Excluding projects under paths: {', '.join(excluded_paths)}")

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

    query_settings = settings_to_check.get("query", {})
    correct_projects = []
    incorrect_projects = []
    skipped_projects = []

    for project in all_projects:
        project_name = project["name"]
        project_path = project.get("fullPath", "")

        if any(project_path.startswith(excluded_path) for excluded_path in excluded_paths):
            skipped_projects.append((project_name, project_path))
            continue

        errors = []

        for setting, expected_value in query_settings.items():
            keys = setting.split(".")
            value = project
            for key in keys:
                if isinstance(value, list):
                    if isinstance(expected_value, list) and isinstance(expected_value[0], dict):
                        match_found = False
                        for item in value:
                            match = all(item.get(sub_key) == sub_value for sub_key, sub_value in expected_value[0].items())
                            if match:
                                match_found = True
                                break
                        value = match_found
                    else:
                        value = [v.get(key, None) for v in value if isinstance(v, dict)]
                        value = [v for v in value if v is not None]
                        if len(value) == 1:
                            value = value[0]
                elif isinstance(value, dict):
                    value = value.get(key, None)
                else:
                    value = None
                if value is None:
                    break
            if value != expected_value:
                errors.append(f"Setting '{setting}' is '{colored(value, 'cyan')}', expected '{colored(expected_value, 'yellow')}'")

        if errors:
            incorrect_projects.append((project_name, errors))
        else:
            correct_projects.append(project_name)

    if skipped_projects:
        print(colored("\n=== Projects Skipped ===", 'yellow'))
        for project_name, project_path in skipped_projects:
            print(colored(f"- {project_name} ({project_path})", 'yellow'))
    print("-" * 50)

    print(colored("\n=== Summary ===", 'magenta'))
    print(colored(f"Total Projects Checked: {len(all_projects)}", 'cyan'))
    print(colored(f"Projects with Correct Settings: {len(correct_projects)}", 'green'))
    print(colored(f"Projects with Incorrect Settings: {len(incorrect_projects)}", 'red'))
    print(colored(f"Projects Skipped: {len(skipped_projects)}", 'yellow'))
    print("-" * 50)

    if correct_projects:
        print(colored("\n=== Projects with Correct Settings ===", 'green'))
        for project_name in correct_projects:
            print(colored(f"- {project_name}", 'green'))
    print("-" * 50)

    if incorrect_projects:
        print(colored("\n=== Projects with Incorrect Settings ===", 'red'))
        for project_name, errors in incorrect_projects:
            print(colored(f"- {project_name}", 'red'))
            for error in errors:
                print(f"  {error}")
    print("-" * 50)

if __name__ == "__main__":
    if not GITLAB_ACCESS_TOKEN:
        raise EnvironmentError("Please set the GITLAB_ACCESS_TOKEN environment variable.")
    check_project_settings()

