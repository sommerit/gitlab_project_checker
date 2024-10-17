# GitLab GraphQL Project Settings Checker

This script checks GitLab projects with a specific topic for certain settings using the GitLab GraphQL API. You can configure the settings to be checked in a YAML file.

## Requirements

- Python 3
- Required Python packages: `requests`, `pyyaml`
- A GitLab Personal Access Token with access to the projects you want to check

## Installation

1. Clone the repository or copy the script to your local machine.
2. Install the required Python packages:
   ```sh
   pip install requests pyyaml

## Possible GraphQL Settings

| Setting                                                  | Description                                         | Example Value                    |
| -------------------------------------------------------- | --------------------------------------------------- | -------------------------------- |
| `topic`                                                  | The topic to filter projects by                     | "Devopsapp"                     |
| `mergeRequestsSettings.mergeMethod`                      | The merge method to be used                         | "merge_commit", "fast_forward" |
| `mergeRequestsSettings.onlyAllowMergeIfPipelineSucceeds` | Require all pipelines to succeed before merging     | true                             |
| `mergeRequestsSettings.allowCollaboration`               | Allow collaboration on merge requests               | true                             |
| `mergeRequestsSettings.rebaseBeforeMerge`                | Rebase the source branch before merging             | true                             |
| `mergeRequestsSettings.squash`                           | Allow squash merging                                | true                             |
| `mergeRequestsSettings.squashOnMerge`                    | Automatically squash commits when merging           | true                             |
| `mergeRequestsSettings.defaultMergeCommitMessage`       | Default commit message for merges                   | "Merge branch into main"        |
| `mergeRequestsSettings.defaultSquashCommitMessage`      | Default commit message for squashes                 | "Squash commit"                 |
| `mergeRequestsSettings.commitMessageTemplate`           | Template for commit messages                        | "[JIRA-123] - <message>"        |
| `mergeRequestsSettings.requireCodeOwnerApprovals`       | Require code owner approvals before merging         | true                             |
| `onlyAllowMergeIfAllDiscussionsAreResolved`              | Allow merge only if all discussions are resolved    | true                             |
| `approvalsBeforeMerge`                                   | Number of approvals required before merging         | 2                                |
| `visibility`                                             | Project visibility level                            | "private", "public", "internal"  |
| `issuesEnabled`                                          | Enable issues for the project                       | true                             |
| `mergeRequestsEnabled`                                   | Enable merge requests for the project               | true                             |
| `jobsEnabled`                                            | Enable CI/CD jobs for the project                   | true                             |
| `wikiEnabled`                                            | Enable wiki for the project                         | true                             |
| `snippetsEnabled`                                        | Enable snippets for the project                     | true                             |
| `containerRegistryEnabled`                               | Enable container registry for the project           | true                             |
| `lfsEnabled`                                             | Enable Git Large File Storage (LFS) for the project | true                             |
| `protectedBranches.name`                                 | Name of the protected branch                        | "main"                          |
| `protectedBranches.pushAccessLevel`                      | Access level required to push to the branch         | "maintainer"                    |
| `protectedBranches.mergeAccessLevel`                     | Access level required to merge into the branch      | "developer"                     |
| `protectedBranches.unprotectAccessLevel`                 | Access level required to unprotect the branch       | "maintainer"                    |
