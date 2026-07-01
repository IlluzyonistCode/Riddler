# Riddler

> *Puzzles No Machine Can Solve For You*

![Python](https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white)

## Overview

Riddler is a Python terminal application for interactive riddle sessions. A plugin-based engine dynamically discovers and loads riddle types at runtime, validates answers through salted hashing, scores attempts by entropy and timing, and manages the full session lifecycle from prompt to resolution.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

---

## Features

|      | Component         | Details                                                                                                                                                                                                                                  |
| :--- | :---------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Standalone Python application (no containerization detected)</li><li>No microservices or distributed architecture evident</li></ul> |
| 🔩  | **Code Quality**  | <ul><li>Written in **Python** — dynamically typed, interpreted language</li><li>No linter configs detected (e.g., no `.flake8`, `pylint`, `ruff` config)</li><li>No formatter config found (e.g., no `black` or `isort` setup)</li></ul>  |
| 📄  | **Documentation** | <ul><li>No dedicated docs directory or framework detected (e.g., no `Sphinx`, `MkDocs`)</li><li>No `README.md` or `CHANGELOG` identified in metadata</li><li>**License file present** — project has defined usage terms</li></ul>         |
| 🔌  | **Integrations**  | <ul><li>No external API integrations detected from available metadata</li><li>No webhook, SDK, or third-party service configs found</li><li>CI/CD references `.py` and `py` — possible scripted pipeline steps</li></ul>                  |
| 🧩  | **Modularity**    | <ul><li>No package manager config found (e.g., no `pyproject.toml`, `setup.py`, `requirements.txt`)</li><li>Unclear module/package boundaries without source file access</li><li>Likely single-repo, flat structure</li></ul>             |

---

## Project Structure

```
└── Riddler/
    ├── core.py
    ├── LICENSE
    ├── README.md
    ├── riddles
    │   ├── __init__.py
    └── session.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+ / Node.js 18+ *(depending on the stack above)*

### Installation

```sh
git clone "https://github.com/IlluzyonistCode/Riddler
cd Riddler"
pip install -r requirements.txt
```

### Usage

```sh
python main.py
```

---

## Contributing

- [Report Issues](https://github.com/IlluzyonistCode/Riddler/issues)
- [Submit Pull Requests](https://github.com/IlluzyonistCode/Riddler/pulls)
- [Discussions](https://github.com/IlluzyonistCode/Riddler/discussions)

---

## License

Distributed under the [AGPL-3.0](LICENSE) license.
