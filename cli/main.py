import sys

from dataclasses import dataclass


# < ----------------------------------------------------------------------- > #


@dataclass
class Settings:
    GUI: bool = False


# < ----------------------------------------------------------------------- > #


def main() -> int:
    unkown_arguments = False

    for arg in sys.argv[1:]:
        match arg:
            case "--gui":
                Settings.GUI = True

            case _:
                print(f"unknown argument: {arg}")
                unkown_arguments = True

    if unkown_arguments:
        return 1

    if Settings.GUI:
        from minecraft_pack_manager.gui.main import main as gui_main

        return gui_main()

    return 0


# < ----------------------------------------------------------------------- > #
