from pathlib import Path

import tomli


def main():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        data = tomli.load(f)

    print(data["project"]["version"])


if __name__ == "__main__":
    main()
