[![GitHub top language](https://img.shields.io/github/languages/top/chigwell/penelopa)](https://github.com/chigwell/penelopa)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Downloads](https://static.pepy.tech/badge/penelopa)](https://pepy.tech/project/penelopa)
[![PyPI - Version](https://img.shields.io/pypi/v/penelopa?color=blue)](https://pypi.org/project/penelopa/)

# Penelopa: AI-driven Codebase Modifier

Penelopa is an innovative tool designed to leverage OpenAI's GPT models for intelligent and automated codebase modifications. It comprehends and executes code changes based on natural language task descriptions, bringing a new level of efficiency to code maintenance.

![Penelopa](https://penelopa.uk/penelopa.gif)

## Installation

Install Penelopa easily using pip:

```bash
pip install penelopa
```

## Usage

Run Penelopa from the command line with various options:

```bash
penelopa --task=<task description> 
         --gpt_key=<OpenAI GPT key>
         --config_path=<path to config> 
         --logging=<True/False> 
         --project=<project name> 
         --path=<project path> 
         --model=<GPT model> 
         --temperature=<float> 
         --top_p=<float> 
         --max_tokens=<int> 
         --gitignore=<True/False> 
         --listing=<path to listing file> 
         --updated_listing=<True/False> 
         --assistant_id=<assistant id>
```

### Arguments

- `--config_path`: Path to the YAML configuration file.
- `--logging`: Enable verbose logging (True/False).
- `--project`: Name of the project for contextual understanding.
- `--path`: Path to the project directory.
- `--task`: Description of the task for the AI to understand and perform.
- `--gpt_key`: API key for OpenAI services.
- `--model`: OpenAI GPT model to use.
- `--temperature`: Level of creativity for AI responses.
- `--top_p`: Diversity of AI responses.
- `--max_tokens`: Maximum word count for AI responses.
- `--gitignore`: Consider .gitignore rules (True/False).
- `--listing`: Path to project file listing for context.
- `--updated_listing`: Flag to update the listing file (True/False).
- `--assistant_id`: Identifier for the AI assistant instance.

## Contributing

Your contributions are welcome! Feel free to create [issue requests](https://github.com/chigwell/penelopa/issues) to enhance Penelopa's functionalities.

## License

This project is licensed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0).
