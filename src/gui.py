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
#< ------------------------ >#

#< not pre-installed imports >#
try:
    from PyQt6.QtCore import (
        pyqtSignal,
        QSize,
        Qt,
        QThread
    )
except Exception as error:
    print_import_error("[gui]<-[PyQt6.QtCore]", error, 
        "https://pypi.org/project/PyQt6", "PyQt6")

try:
    from PyQt6.QtGui import (
        QFontDatabase
    )
except Exception as error:
    print_import_error("[gui]<-[PyQt6.Gui]", error, 
        "https://pypi.org/project/PyQt6", "PyQt6")

try:
    from PyQt6.QtWidgets import (
        QApplication,
        QComboBox,
        QDialog,
        QFormLayout,
        QGridLayout,
        QGroupBox,
        QLabel, 
        QLineEdit,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QStackedWidget,
        QTabWidget,
        QWidget
    )
except Exception as error:
    print_import_error("[gui]<-[PyQt6.QtWidgets]", error, 
        "https://pypi.org/project/PyQt6", "PyQt6")
#< ------------------------ >#

#< photon provided imports >#
try:
    from ..modules.common import (
        _UNIVERSALS, 
        log
    )
except Exception as error:
    print_import_error("[gui]<-[..modules.common]", error, 
    import_type="Photon", hypertext=False)
#< ------------------------ >#

#< project provided imports >#
try:
    from . import (
        logic
    )
except Exception as error:
    print_import_error("[gui]<-[.logic]", error, 
    import_type="Project", hypertext=False)
#< ----------------------- >#



#< ------------------------ >#
class workerThread(QThread):
    finished=pyqtSignal()

    def __init__(
            self, 
            run_function, 
            args=None, 
            parent=None
        ):

        super().__init__(parent)

        self.run_function=run_function
        self.args=args

    def run(
            self
        ):

        log.debug(f"worker {self} started")
        if self.args is None:
            self.run_function()
        else:
            self.run_function(self.args)
        log.debug(f"worker {self} finished")
        self.finished.emit()
#< ------------------------ >#



#< ------------------------ >#
class notifyDialog(QDialog):
    def __init__(
            self, 
            title:str, 
            message:str, 
            min_size:tuple[int, int]=(220, 40), 
            max_size:tuple[int, int]=(320, 120), 
            parent=None, 
            modal:bool=False
        ):

        super().__init__(parent)
        log.debug(f"init {self}")

        layout=QGridLayout()

        self.setWindowTitle(title)
        self.setModal(modal)

        self.message_label=QLabel(message)
        self.message_label.setMinimumSize(min_size[0], min_size[1])
        self.message_label.setMaximumSize(max_size[0], max_size[1])
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 0, 0, 1, 2)

        self.close_button=QPushButton("Close")
        self.close_button.clicked.connect(lambda: [self.close()])
        layout.addWidget(self.close_button, 1, 1, 1, 1)

        self.setLayout(layout)
#< ------------------------ >#



#< ----------------------- >#
class MPM(QApplication):
    def __init__(
            self, 
            argv:list[str]
        ):

        super().__init__(argv)
        log.debug(f"init {self}")

        #< create window >#
        window=self.window_setup()

        #< add any fonts provided by mpm or photon >#
        local_font_directory=os.path.join(
            _UNIVERSALS.package_root(logic.manifest.name()), 
            "resources", "fonts")
        self.add_font(local_font_directory)

        photon_font_directory=os.path.join(
            _UNIVERSALS.root(), "resources", "fonts")
        self.add_font(photon_font_directory)

        #< apply sheet >#
        if os.path.exists(logic.local_settings.style_sheet()):
            self.setStyleSheet(logic.local_settings.style_sheet_contents())
        else:
            log.warning("no style sheet found")

        #< setup complete, show window >#
        window.show()


    def window_setup(self):
        #< window size >#
        window_width=640 
        window_height=360

        #< window icon >#
        self.setWindowIcon(logic.get_QIcon(
            logic.images_vault.images_dict()["general"]["icon"]))

        #< window title >#
        display_name=logic.manifest.display_name()
        version=logic.manifest.version()
        log.debug(f"display_name: {display_name}, version: {version}")

        window=Container(self, window_width, window_height)
        window.setWindowTitle(f"{display_name} {version}")

        #< try find screen size and assume 1920x1080 if unable to >#
        screen_size=self.primaryScreen()
        if screen_size is not None:
            screen_size=screen_size.size()
        else:
            screen_size=QSize(1920, 1080)
        log.debug(screen_size)
        screen_width=screen_size.width()
        screen_height=screen_size.height()

        #< move to center screen >#
        center_x=int(screen_width/2 - window_width/2)
        center_y=int(screen_height/2 - window_height/2)

        #< apply geometry and show >#
        window.setGeometry(center_x, center_y, window_width, window_height)
        window.setFixedSize(window_width, window_height)
        return window


    def add_font(self, directory_path):
        if not os.path.exists(directory_path):
            return

        log.debug(f"loading fonts from {directory_path}")
        for font_directory in os.listdir(directory_path):
            font_directory_path=os.path.join(directory_path, font_directory)
            for font in os.listdir(font_directory_path):
                log.debug(f"loading font {font}")
                font_filepath=os.path.join(font_directory_path, font)
                try:
                    QFontDatabase.addApplicationFont(font_filepath)
                except:
                    log.warning(f"failed to load font {font}")
#< ----------------------- >#



#< ----------------------- >#
class Container(QWidget):
    def __init__(
            self, 
            parent:MPM, 
            width:int, 
            height:int,
        ):

        super().__init__()
        log.debug(f"init {self}")

        #< layouts >#
        layout=QGridLayout()
        self.pages=QStackedWidget()

        #< to attach the title bar to the top of the window >#
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        #< the background image and scale background image to window >#
        self.background_label=QLabel()
        self.background_label.setObjectName("background")
        self.background_label.setPixmap(logic.get_QPixmap(
            logic.images_vault.images_dict()["general"]["background"], 
            size=(width, height)))
        self.background_label.setMinimumSize(1, 1)
        layout.addWidget(self.background_label, 0, 0, 
            Qt.AlignmentFlag.AlignCenter)

        #< pages >#
        self.pages.setContentsMargins(0, 0, 0, 0)
        self.pages.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.pages.setFixedSize(width, height)

        for page in [
                HomePage, 
                UploadPage, 
                DownloadPage, 
                SettingsPage, 
                HelpPage, 
                PlayPage
            ]:
            self.pages.addWidget(page(self))
        layout.addWidget(self.pages, 0, 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


    def change_page(self, index):
        self.pages.setCurrentIndex(index)
#< ----------------------- >#



#< ----------------------- >#
class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()
        layout.setContentsMargins(25, 0, 25, 25)

        #< page title >#
        self.title_label=QLabel("Home")
        self.title_label.setObjectName("page_title")
        self.title_label.setFixedSize(384, 48)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 4, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        #< home page buttons >#
        buttons={}
        row=1
        column=0
        for button in [
                " Upload", 
                " Download", 
                " Settings", 
                " Help", 
                " Play", 
                " Quit"
            ]:
            self.button=QPushButton(button)
            self.button.setFixedSize(256, 72)
            self.button.setObjectName("home_buttons")

            icon_name=f"{button.strip().lower()}_button"
            self.button.setIcon(logic.get_QIcon(
                logic.images_vault.images_dict()["home_page"][icon_name]))
            self.button.setIconSize(QSize(56, 56))

            buttons[button.strip().lower()]=self.button
            layout.addWidget(self.button, row, column, 1, 2, 
                Qt.AlignmentFlag.AlignCenter)

            if column == 0:
                column=column+2
            else:
                row=row+1
                column=column-2

        #< .clicked.connect gets overridden inside the for loop >#
        buttons["upload"].clicked.connect(lambda: [parent.change_page(1)])
        buttons["download"].clicked.connect(lambda: [parent.change_page(2)])
        buttons["settings"].clicked.connect(lambda: [parent.change_page(3)])
        buttons["help"].clicked.connect(lambda: [parent.change_page(4)])
        buttons["play"].clicked.connect(lambda: [parent.change_page(5)])
        buttons["quit"].clicked.connect(lambda: [MPM.quit()])

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class UploadPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()
        layout.setContentsMargins(25, 0, 25, 25)

        #< page title >#
        self.title_label=QLabel("Upload")
        self.title_label.setObjectName("page_title")
        self.title_label.setFixedSize(384, 48)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 4, 
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        #< home button >#
        self.home_button=QPushButton("Back")
        self.home_button.setFixedHeight(40)
        self.home_button.setMinimumWidth(128)
        self.home_button.clicked.connect(lambda: [parent.change_page(0)])
        layout.addWidget(self.home_button, 1, 3, 1, 1)

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class DownloadPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()
        layout.setContentsMargins(25, 0, 25, 25)

        #< page title >#
        self.title_label=QLabel("Download")
        self.title_label.setObjectName("page_title")
        self.title_label.setFixedSize(384, 48)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 4, 
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        #< home button >#
        self.home_button=QPushButton("Back")
        self.home_button.setFixedHeight(40)
        self.home_button.setMinimumWidth(128)
        self.home_button.clicked.connect(lambda: [parent.change_page(0)])
        layout.addWidget(self.home_button, 1, 3, 1, 1)

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class SettingsPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()
        layout.setContentsMargins(25, 0, 25, 25)
        self.setting_widgets={}
        self.icons={}

        #< page title >#
        self.title_label=QLabel("Settings")
        self.title_label.setObjectName("page_title")
        self.title_label.setFixedSize(384, 48)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 4, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        #< launcher path >#
        #< label >#
        self.launcher_path_label=QLabel("Launcher Path: ")
        self.launcher_path_label.setFixedSize(180, 40)
        layout.addWidget(self.launcher_path_label, 1, 0)

        #< input >#
        self.launcher_path_input=QLineEdit()
        self.launcher_path_input.setFixedSize(356, 40)
        layout.addWidget(self.launcher_path_input, 1, 1)
        self.setting_widgets["launcher_path_input"]=self.launcher_path_input

        #< validate >#
        self.launcher_path_validate=QPushButton()
        self.launcher_path_validate.setObjectName("settings_icon")
        self.launcher_path_validate.setIcon(logic.get_QIcon(
            logic.images_vault.images_dict()["settings_page"]["valid"]))
        self.launcher_path_validate.setIconSize(QSize(24, 24))
        self.launcher_path_validate.setFixedSize(40, 40)

        self.launcher_path_validate.clicked.connect(lambda: [
            self.settings_popup("launcher_path is valid")])
        layout.addWidget(self.launcher_path_validate, 1, 3, 1, 1, 
            Qt.AlignmentFlag.AlignRight)
        self.icons["launcher_path_validate"]=self.launcher_path_validate

        #< instances path >#
        #< label >#
        self.instances_path_label=QLabel("Instances Path: ")
        self.instances_path_label.setFixedSize(180, 40)

        layout.addWidget(self.instances_path_label, 2, 0)

        #< input >#
        self.instances_path_input=QLineEdit()
        self.instances_path_input.setFixedSize(356, 40)

        layout.addWidget(self.instances_path_input, 2, 1)
        self.setting_widgets["instances_path_input"]=self.instances_path_input

        #< validate >#
        self.instances_path_validate=QPushButton()
        self.instances_path_validate.setFixedSize(40, 40)
        self.instances_path_validate.setObjectName("settings_icon")
        self.instances_path_validate.setIcon(logic.get_QIcon(
            logic.images_vault.images_dict()["settings_page"]["valid"]))
        self.instances_path_validate.setIconSize(QSize(24, 24))

        self.instances_path_validate.clicked.connect(lambda: [
            self.settings_popup("instances_path is valid")])
        layout.addWidget(self.instances_path_validate, 2, 3, 1, 1, 
            Qt.AlignmentFlag.AlignRight)
        self.icons["instances_path_validate"]=self.instances_path_validate

        #< verify settings >#
        self.verify_settings_button=QPushButton("Verify Settings")
        self.verify_settings_button.setFixedSize(180, 40)

        self.verify_settings_button.clicked.connect(lambda: [
            logic.validate_settings(
                self, self.setting_widgets, self.icons, write=True)])
        layout.addWidget(self.verify_settings_button, 4, 0)

        #< home button >#
        self.home_button=QPushButton("Back")
        self.home_button.setFixedHeight(40)
        self.home_button.setMinimumWidth(128)

        self.home_button.clicked.connect(lambda: [parent.change_page(0)])
        layout.addWidget(self.home_button, 4, 3, 1, 1)


        self.setLayout(layout)
        logic.write_settings_to_gui(self.setting_widgets)
        logic.validate_settings(self, self.setting_widgets, self.icons)


    def settings_popup(
            self, 
            label_text: str="label", 
            second_button: bool=False, 
            second_button_text: str="Create", 
            path: str=None
        ):
        popup=settingsPopup(self, label_text, 
            second_button, second_button_text)
        if popup.exec() and second_button:
            if path.endswith(os.sep):
                path=path[-1]
            split_path=path.split(os.sep)

            if len(split_path) < 3:
                log.warning("Failed to make file path: too short")

            else:
                try:
                    os.makedirs(path)
                except Exception as error:
                    log.error(error)
                logic.validate_settings(self, self.setting_widgets, self.icons)
#< ----------------------- >#



#< ----------------------- >#
class settingsPopup(QDialog):
    def __init__(
            self, 
            parent=None, 
            label_text: str="label", 
            second_button: bool=False, 
            second_button_text: str="Create"
        ):
        super().__init__(parent)

        #< apply sheet >#
        if os.path.exists(logic.local_settings.style_sheet()):
            self.setStyleSheet(logic.local_settings.style_sheet_contents())
        else:
            log.warning("no style sheet found")

        self.setFixedSize(360, 120)
        self.setWindowTitle(" ")

        layout=QGridLayout()

        popup_label=QLabel(label_text)
        layout.addWidget(popup_label, 0, 0, 1, 2)

        popup_exit_button=QPushButton("Close")
        popup_exit_button.clicked.connect(lambda: [self.close()])
        layout.addWidget(popup_exit_button, 1, 1, 1, 1)

        if second_button:
            popup_create_button=QPushButton(second_button_text)
            popup_create_button.clicked.connect(lambda: [self.accept()])
            layout.addWidget(popup_create_button, 1, 0, 1, 1)

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class HelpPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()
        layout.setContentsMargins(25, 0, 25, 25)

        #< page title >#
        self.title_label=QLabel("Help")
        self.title_label.setObjectName("page_title")
        self.title_label.setFixedSize(384, 48)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 4, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        #< home button >#
        self.home_button=QPushButton("Back")
        self.home_button.setFixedHeight(40)
        self.home_button.setMinimumWidth(128)
        self.home_button.clicked.connect(lambda: [parent.change_page(0)])
        layout.addWidget(self.home_button, 1, 3, 1, 1)

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class PlayPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()
        layout.setContentsMargins(25, 0, 25, 25)

        #< page title >#
        self.title_label=QLabel("Play")
        self.title_label.setObjectName("page_title")
        self.title_label.setFixedSize(384, 48)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 4, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        #< tabs container >#
        self.tabs=QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.tabs.setFixedSize(600, 240)
        layout.addWidget(self.tabs, 1, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)

        #< tabs >#
        self.players_tab=PlayPagePlayersTab(self)
        self.tabs.addTab(self.players_tab, "Players")

        self.history_tab=PlayPageHistoryTab(self)
        self.tabs.addTab(self.history_tab, "History")

        #< launcher button >#
        self.open_launcher_button=QPushButton("Open Launcher")
        self.open_launcher_button.setFixedSize(200, 40)
        self.open_launcher_button.clicked.connect(lambda: [
            logic.open_launcher()])
        layout.addWidget(self.open_launcher_button, 2, 0, 
            Qt.AlignmentFlag.AlignCenter)

        #< user refresh button >#
        self.refresh_user_list_button=QPushButton("Update List")
        self.refresh_user_list_button.setFixedSize(200, 40)
        self.refresh_user_list_button.clicked.connect(lambda: [
            self.update_list()])
        layout.addWidget(self.refresh_user_list_button, 2, 1, 
            Qt.AlignmentFlag.AlignCenter)

        #< user add button >#
        self.add_user_button=QPushButton()
        self.add_user_button.setFixedSize(80, 40)
        self.add_user_button.setIcon(logic.get_QIcon(
            logic.images_vault.images_dict()["play_page"]["plus_slash_minus"], 
            size=(60, 60)))
        self.add_user_button.setIconSize(QSize(60, 60))
        self.add_user_button.clicked.connect(lambda: [self.change_users()])
        layout.addWidget(self.add_user_button, 2, 2, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)

        #< home button >#
        self.home_button=QPushButton("Back")
        self.home_button.setFixedSize(80, 40)
        self.home_button.clicked.connect(lambda: [parent.change_page(0)])
        layout.addWidget(self.home_button, 2, 3, 1, 1, 
            Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


    def update_list(self):
        self.worker1=workerThread(logic.get_player_skin)
        self.worker2=workerThread(logic.reload_player_labels, self.players_tab)

        popup=notifyDialog("Updating User List", "Updating...", 
            parent=self, modal=True)
        popup.close_button.hide()

        self.worker1.finished.connect(self.worker2.start)
        self.worker2.finished.connect(self.worker1.quit)
        self.worker2.finished.connect(self.worker2.quit)
        self.worker2.finished.connect(popup.close)

        popup.show()
        self.worker1.start()


    def change_users(self):
        popup=editUsersPopup(self)
        if popup.exec():
            logic.edit_users(popup)
            logic.reload_player_labels(self.players_tab)
#< ----------------------- >#



#< ----------------------- >#
class PlayPagePlayersTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        #< layout >#
        layout=QGridLayout()
        group_box=QGroupBox()
        scroll_layout=QScrollArea()
        self.user_list=QFormLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        group_box.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.user_list.setVerticalSpacing(15)
        self.user_list.setHorizontalSpacing(0)
        self.user_list.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_list.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_list.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user_labels={}
        self.user_active_icons={}

        group_box.setLayout(self.user_list)
        scroll_layout.setWidget(group_box)
        scroll_layout.setWidgetResizable(True)
        layout.addWidget(scroll_layout)

        logic.reload_player_labels(self)
        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class PlayPageHistoryTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout=QGridLayout()

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class addUserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout=QGridLayout()

        self.username_label=QLabel("Username:")
        self.username_label.setFixedHeight(40)
        layout.addWidget(self.username_label, 0, 0)

        self.username_input=QLineEdit()
        self.username_input.setFixedHeight(40)
        self.username_input.setObjectName("edit_users")
        layout.addWidget(self.username_input, 0, 1, 1, 2)

        self.auth_type_label=QLabel("Auth Type:")
        self.auth_type_label.setFixedHeight(40)
        layout.addWidget(self.auth_type_label, 1, 0)

        self.auth_type_input=QComboBox()
        self.auth_type_input.setFixedHeight(40)
        self.auth_type_input.addItems(["Official", "Ely"])
        layout.addWidget(self.auth_type_input, 1, 1, 1, 2)

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class removeUserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout=QGridLayout()

        self.username_label=QLabel("Username:")
        self.username_label.setFixedHeight(40)
        layout.addWidget(self.username_label, 0, 0)

        self.username_input=QComboBox()
        self.username_input.setFixedHeight(40)
        self.username_input.addItems(logic.user_list())
        layout.addWidget(self.username_input, 0 ,1, 1, 2)

        self.setLayout(layout)
#< ----------------------- >#



#< ----------------------- >#
class editUsersPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        #< apply sheet >#
        if os.path.exists(logic.local_settings.style_sheet()):
            self.setStyleSheet(logic.local_settings.style_sheet_contents())
        else:
            log.warning("no style sheet found")

        self.setFixedSize(480, 220)
        self.setWindowTitle("Edit Users")

        layout=QGridLayout()

        self.tabs=QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)
        layout.addWidget(self.tabs, 0, 0, 1, 2)

        self.add_user_tab=addUserTab(self)
        self.tabs.addTab(self.add_user_tab, "Add")

        self.remove_user_tab=removeUserTab(self)
        self.tabs.addTab(self.remove_user_tab, "Remove")

        popup_exit_button=QPushButton("Close")
        popup_exit_button.clicked.connect(lambda: [self.close()])
        layout.addWidget(popup_exit_button, 1, 1, 1, 1)

        popup_accept_button=QPushButton("Ok")
        popup_accept_button.clicked.connect(lambda: [self.accept()])
        layout.addWidget(popup_accept_button, 1, 0, 1, 1)

        self.setLayout(layout)
#< ----------------------- >#


