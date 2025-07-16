#< ------------------------ >#
def print_import_error(
        import_tree:str, 
        error:Exception, 
        link:str=None, # type: ignore
        text:str=None, # type: ignore
        import_type:str="Installed",
        hypertext:bool=True
    ):
    print(f"{import_type} Import Error: {import_tree}",
          f"  {error.args[0].split("(")[0]}", sep=os.linesep)
    if hypertext:
        hyperlink=f"\x1b]8;{""};{link}\x1b\\{text}\x1b]8;;\x1b\\"
        print(f"  Is {hyperlink} installed?")
    sys.exit(1)
#< ------------------------ >#

#< pre-installed imports >#
import os
import sys
#< ----------------------- >#

#< photon provided imports >#
try:
    from .modules.common import (
        log
    )
except Exception as error:
    print_import_error("[main]<-[.modules.common]", error, 
        import_type="Photon", hypertext=False)
#< ----------------------- >#

#< project provided imports >#
try:
    from .src.gui import MPM
except Exception as error:
    print_import_error("[main]<-[.src.gui]", error, 
        import_type="Project", hypertext=False)
#< ----------------------- >#



#< ----------------------- >#
def main(argv):
    app=MPM(argv)
    app.exec()
#< ----------------------- >#



#< ----------------------- >#
if __name__ == "packages.minecraft_pack_manager.main":
    main(sys.argv)

elif __name__ == "__main__":
    log.error("run using photon")
#< ----------------------- >#


