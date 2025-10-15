from pathlib import Path


# < ----------------------------------------------------------------------- > #


def main() -> int:
    path: Path = Path(__file__).parent.joinpath("cli")

    if path.exists():
        from minecraft_pack_manager.cli.main import main as cli_main

        return cli_main()

    else:
        return 1


# < ----------------------------------------------------------------------- > #
