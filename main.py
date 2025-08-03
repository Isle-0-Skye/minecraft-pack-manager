def print_import_error(
    import_tree: str,
    error: ImportError,
    hypertext: bool = True,
    import_type: str = "installed",
    link: str | None = None,
    text: str | None = None,
):
    print(
        f"{import_type} import error: {import_tree}",
        f"  {error.args[0].split('(')[0]}",
        sep=os.linesep,
    )
    if hypertext:
        hyperlink = f"\x1b]8;{''};{link}\x1b\\{text}\x1b]8;;\x1b\\"
        print(f"  is {hyperlink} installed?")
    sys.exit(1)


# < pre-installed imports --------------------------------------------------------------------- > #
import os
import sys


# < photon provided imports ------------------------------------------------------------------- > #
try:
    from .modules.common import pLOG
except ImportError as error:
    print_import_error(
        import_tree="[main]<-[.modules.common]",
        error=error,
        import_type="Photon",
        hypertext=False,
    )

# < project provided imports ------------------------------------------------------------------ > #
try:
    from .src.gui import MPM
except ImportError as error:
    print_import_error(
        import_tree="[main]<-[.src.gui]",
        error=error,
        import_type="Project",
        hypertext=False,
    )


# < ------------------------------------------------------------------------------------------- > #
def main(argv):
    app = MPM(argv)
    app.exec()


# < ------------------------------------------------------------------------------------------- > #
if __name__ == "packages.minecraft_pack_manager.main":
    main(sys.argv)

elif __name__ == "__main__":
    pLOG.error("run using photon")
