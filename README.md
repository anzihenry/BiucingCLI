# BiucingCLI

BiucingCLI is a Typer-based command-line companion that curates full-stack development toolchains. It helps frontend, mobile, desktop, backend, testing, and DevOps engineers bootstrap projects, discover recommended tools, and automate routine setup tasks.

## Features

- 🌐 **Frontend**: Recommend bundlers, frameworks, linting, and testing tools for web stacks (including TypeScript).
- 📱 **Mobile**: Surface native and cross-platform options, SDK helpers, and CI tips (including React Native, Swift iOS, and Kotlin Android).
- 🖥️ **Desktop**: Highlight Electron, Tauri, Qt, and packaging workflows (including C++ cross-platform development).
- 🔧 **Backend**: Suggest frameworks, ORMs, observability, and API tooling (including Go frameworks like Gin and Echo).
- 🧪 **Testing**: Organize unit, integration, E2E, and performance testing stacks.
- 🚀 **DevOps**: Provide CI/CD, infrastructure-as-code, container, and monitoring practices (including Python DevOps automation tools).
- 🔧 **Configuration-driven**: Customize recommendations through YAML-driven profiles.
- ✨ **Rich output**: Uses Rich for colorful, structured terminal UX.

## Quick Start

### Prerequisites

- Python 3.14+
- `pipx`, `pip`, or `uv`

### Installation

```bash
pipx install .
# or
pip install .
```

### Usage

```bash
biucing --help
biucing frontend list
biucing backend list                    # Lists Go frameworks like Gin and Echo
biucing mobile list                     # Lists Swift iOS and Kotlin Android options
biucing devops list                     # Lists Python DevOps tools
biucing desktop list                    # Lists C++ cross-platform options
biucing devops suggest --stack cloud-native
biucing configure show --config config/biucingcli.yaml
```

### Configuration

Copy the template configuration to customize recommendations:

```bash
cp config/biucingcli.yaml ~/.config/biucingcli/config.yaml
```

Edit the YAML file to select preferred stacks, tools, and automation tasks.

## Development

Use `uv` to provision the project environment with development tooling:

```bash
uv sync --extra dev
```

Prefer a manual virtual environment instead?

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Makefile Helpers

```bash
make install
make lint
make format
make test
```

### Running Tests

```bash
uv run pytest --cov=biucingcli --cov-report=term-missing
```

## Contributing

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for workflow guidelines.

## License

This project is licensed under the MIT License – see [`LICENSE`](LICENSE) for details.
