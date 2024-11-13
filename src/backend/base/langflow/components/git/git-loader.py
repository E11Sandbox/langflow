from langchain.document_loaders import GithubFileLoader
from langflow.field_typing import Data
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data
import requests


class GitHubFileLoaderComponent(Component):
    display_name = "GitHub File Loader"
    description = "Load specific files from a GitHub repository."
    documentation: str = "http://docs.langflow.org/components/custom"
    icon = "custom_components"

    inputs = [
        MessageTextInput(
            name="repo",
            display_name="Repository Name",
            value="seu-usuario/seu-repositorio",
        ),
        MessageTextInput(name="access_token", display_name="Access Token", value=""),
        MessageTextInput(
            name="github_api_url",
            display_name="GitHub API URL",
            value="https://api.github.com",
        ),
        MessageTextInput(name="branch", display_name="Branch", value="main"),
        MessageTextInput(
            name="file_filter",
            display_name="File Filter",
            value="lambda file_path: file_path.endswith('.md')",
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def build_output(self) -> list[Data]:
        repo = self.repo
        access_token = self.access_token
        github_api_url = self.github_api_url
        branch = self.branch
        file_filter = eval(self.file_filter)

        try:
            # Test the repository URL to ensure it exists
            response = requests.get(
                f"{github_api_url}/repos/{repo}",
                headers={"Authorization": f"token {access_token}"},
            )
            response.raise_for_status()

            loader = GithubFileLoader(
                repo=repo,
                access_token=access_token,
                github_api_url=github_api_url,
                branch=branch,
                file_filter=file_filter,
            )
            documents = loader.load()

            # Concatenando o conteúdo dos documentos em uma string
            # content = "\n".join([doc.page_content for doc in documents])
            data = [Data.from_document(doc) for doc in documents]
            self.status = data
            return data
        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP error occurred: {e}"
            print(error_message)
            data = [Data(value=error_message)]
            self.status = data
            return data
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            data = [Data(value=error_message)]
            self.status = data
            return data
