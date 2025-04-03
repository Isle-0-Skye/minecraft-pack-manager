import os
import sys
import platform
import subprocess
import logging
import threading
import json
import importlib.util
import customtkinter
import mcworldlib as mc
import shutil

from logging import config
from tkinter import PhotoImage


def main(PhotonVars, AppManifest):
    def logging_setup():
        # if logs does not exists logging throws an error
        os.makedirs(os.path.join(PhotonVars['photon_root_dir'], 'logs'), exist_ok=True)

        spec = importlib.util.spec_from_file_location('photon_logger.py', os.path.join(PhotonVars['photon_root_dir'], 'photon_logger.py'))
        photon_logger=importlib.util.module_from_spec(spec)   
        spec.loader.exec_module(photon_logger)

        # add and configure custom_handler
        photon_logger.setup(os.path.join(PhotonVars['photon_root_dir'], 'logs'), 'DEBUG', 'minecraftpackmanager.log')
        log=logging.getLogger('__name__')
        log.setLevel(logging.DEBUG)
        custom_handler=logging.StreamHandler()
        custom_handler.setLevel('DEBUG')
        custom_handler.setFormatter(photon_logger.custom_formatter())
        log.addHandler(custom_handler)

        # seperate each run instance to make reading logs easier
        log.debug(f'{"NEW INSTANCE":{"-"}^100}')

        return log

    log=logging_setup()


    def center_window(window_width, window_height, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        log.debug(f'setting window {window} to {window_width}x{window_height}+{center_x}+{center_y}')
        window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')


    def show_frame(self, page):
        for frame in self.frames.values():
            frame.pack_forget()

        log.debug(f'showing frame / page {page}')
        self.frames[page].pack(side='top', fill='both', expand=True)


    def path_verify(path_entry, upload_button, download_button):
        path=path_entry.get().strip().removesuffix(PhotonVars['platform_seperator'])
        log.debug(f'user input path is {path}')
        path_split=path.split(PhotonVars['platform_seperator'])

        if (not os.path.exists(path)) or (len(path_split) < 3):
            log.info('invalid path')
            popup=customtkinter.CTkToplevel()
            popup.geometry('400x100')
            popup_warning=customtkinter.CTkLabel(popup,
                text='Invalid path',
                font=('Consolas', 32)
            ).pack(side='top', fill='both', expand=True)

            upload_button.configure(state='disabled')
            download_button.configure(state='disabled')

            return path, False
        
        else:
            upload_button.configure(state='normal')
            download_button.configure(state='normal')
        
        return path, True


    def path_scan(local, dropdown, path_entry, upload_button, download_button):
        if local:
            log.debug('scan local')
            (instances_folder, bool)=path_verify(path_entry, upload_button, download_button)
            if bool:
                local_instances=[]
                for name in os.listdir(instances_folder):
                    if os.path.isdir(os.path.join(instances_folder, name)):
                        local_instances.append(name)
                try:
                    local_instances.remove('_LAUNCHER_TEMP')
                except ValueError as error:
                    log.warning(error)

                dropdown.configure(values=local_instances)

        else:
            log.debug('scan remote')
            (instances_folder, bool)=path_verify(path_entry, upload_button, download_button)
            if bool:
                def update_thread():
                    remote_instances=[]
                    rclone_cmd=[os.path.join(PhotonVars['photon_root_dir'], 'tools', PhotonVars['rclone_exe']), 'lsjson', 'GDR:', '--max-depth=3', '--dirs-only', '--no-modtime', '--no-mimetype', f'--config={PhotonVars['rclone_config_file']}']
                    rclone_proc=subprocess.run(rclone_cmd, capture_output=True, text=True)
                    rclonejson=json.loads(rclone_proc.stdout)
                    log.debug(json.dumps(rclonejson, indent=4))

                    for obj in rclonejson:
                        if obj['Path'].endswith('/Modpacks') or obj['Path'].endswith('/mods') or obj['Path'] in ['AC1', 'AC2', 'AC3']:
                            pass
                        else:
                            remote_instances.append(obj['Path'])

                    dropdown.configure(values=remote_instances)

                threading.Thread(target=update_thread, daemon=True).run()

        log.debug(dropdown.get())


    def transfer(local, dropdown, path_entry, upload_button, download_button):
        instance=dropdown.get().strip().removesuffix(PhotonVars['platform_seperator'])
        log.debug(instance)
        if instance not in dropdown.cget('values'):
            log.info('invalid instance')
            return

        (instances_folder, bool)=path_verify(path_entry, upload_button, download_button)
        if bool:
            if local:
                for save in os.listdir(os.path.join(instances_folder, instance, '.minecraft', 'saves')):

                    world=mc.load(os.path.join(instances_folder, instance, '.minecraft', 'saves', save))
                    try:
                        del world.level['Data']['Player']
                    except KeyError as error:
                        log.warning(f'keyerror {error}')
                    world.save(os.path.join(PhotonVars['photon_root_dir'], '.cache', save))

                    shutil.move(
                        os.path.join(PhotonVars['photon_root_dir'], '.cache', save, 'level.dat'),
                        os.path.join(instances_folder, instance, '.minecraft', 'saves', save, 'level.dat')
                    )

                if instance == 'TechPack':
                    ACN='AC1'
                elif instance == 'Cobblemon Modpack [Fabric]':
                    ACN='AC2'
                else:
                    ACN='AC3'
                log.info(f'uploading {instance}')
                gdrive_pth=f'GDR:{ACN}/Modpacks/'
                rclone_cmd_src=os.path.join(instances_folder, instance)
                rclone_cmd_dst=os.path.join(gdrive_pth, instance)

            else:
                log.info(f'downloading {instance}')
                gdrive_pth='GDR:'
                instance_split=instance.split('/')
                rclone_cmd_src=f'{gdrive_pth}{instance}'
                instance=instance_split.pop()
                rclone_cmd_dst=os.path.join(instances_folder, instance)

            rclone_cmd=[
                os.path.join(PhotonVars['photon_root_dir'], 'tools', PhotonVars['rclone_exe']),
                'sync', 
                rclone_cmd_src,
                rclone_cmd_dst,
                '--transfers=20', '--checkers=50', '--fast-list', '--max-backlog=-1', '-P',
                '--exclude="{logs/**, backups/**, options.txt}"',
                f'--config={PhotonVars['rclone_config_file']}'
            ]
            log.debug(rclone_cmd)
            subprocess.run(rclone_cmd)


    def self_update():
        log.info('updating')
        cmd=[PhotonVars['python'], os.path.join(PhotonVars['photon_root_dir'], 'photon.py'), 'update', 'minecraft-pack-manager']
        log.debug(cmd)

        if PhotonVars['platform_os'] == 'Linux':
            run_proc=subprocess.Popen(cmd, start_new_session=True)
        elif PhotonVars['platform_os'] == 'Windows':
            run_proc=subprocess.Popen(cmd, start_new_session=True, creationflags=subprocess.DETACHED_PROCESS)

        try:
            run_proc.detach()
        except:
            pass

        sys.exit(0)

    class minecraftpackmanager(customtkinter.CTk):
        def __init__(self, fg_color = None, **kwargs):
            super().__init__(fg_color, **kwargs)

            customtkinter.set_appearance_mode('dark')
            customtkinter.set_default_color_theme('green')

            self.title(f'{AppManifest['DisplayName']} - {AppManifest['Version']}')
            self.wm_iconphoto(True, PhotoImage(file=os.path.join(PhotonVars['photon_root_dir'], 'assets', f'{AppManifest['Icon']}.png')))
            try:
                self.wm_iconbitmap(default=os.path.join(PhotonVars['photon_root_dir'], 'assets', 'minecraft.ico'))
            except:
                pass
            center_window(600, 250, self)

            ContainerFrame=customtkinter.CTkFrame(self)
            ContainerFrame.pack(side='top', fill='both', expand=True)

            self.frames={}
            self.pages=[
                home_page
            ]

            for page in self.pages:
                self.frames[page]=page(ContainerFrame, self)

            show_frame(self, home_page)


    class home_page(customtkinter.CTkFrame):
        def __init__(self, master, controller, bg_color='transparent', fg_color='transparent', **kwargs):
            super().__init__(master, bg_color='transparent', fg_color='transparent', **kwargs)

            home_page_tabview=customtkinter.CTkTabview(self, bg_color='transparent')

            exit_button=customtkinter.CTkButton(self,
                height=30,
                width=150,
                text='Quit',
                font=('Consolas', 20),
                command=lambda:[sys.exit(0)],
            )

            self.rowconfigure(0, weight=10)
            self.rowconfigure(1, weight=1)

            self.columnconfigure(0, weight=1)

            home_page_tabview.grid( row=0, column=0, padx=15, pady=5)
            exit_button.grid(       row=1, column=0, padx=15, pady=5, sticky='e')

            # # # # # # # # # # # 
            #    UPLOAD PAGE    # 
            # # # # # # # # # # # 

            home_page_tabview.add('Upload')
            upload_label=customtkinter.CTkLabel(home_page_tabview.tab('Upload'),
                height=30,
                width=600,
                text='Upload local files and overwrite cloud files',
                font=('Consolas', 16),
                wraplength=600
            )
            upload_button=customtkinter.CTkButton(home_page_tabview.tab('Upload'),
                height=30,
                width=250,
                text='Upload',
                font=('Consolas', 20),
                command=lambda:[transfer(True, upload_dropdown, misc_path_entry, upload_button, download_button)],
            )
            upload_dropdown=customtkinter.CTkComboBox(home_page_tabview.tab('Upload'),
                height=30,
                width=600,
                font=('Consolas', 20),
                values=[],
            )
            upload_refresh_button=customtkinter.CTkButton(home_page_tabview.tab('Upload'),
                height=30,
                width=250,
                text='Refresh',
                font=('Consolas', 20),
                command=lambda:[path_scan(True, upload_dropdown,misc_path_entry, upload_button, download_button)],
            )

            for i in range(0,2):
                home_page_tabview.tab('Upload').rowconfigure(i, weight=1)
                home_page_tabview.tab('Upload').columnconfigure(i, weight=1)

            upload_label.grid(          row=0, column=0, padx=15, pady=5, columnspan=3)
            upload_dropdown.grid(       row=1, column=0, padx=15, pady=5, columnspan=3)
            upload_refresh_button.grid( row=2, column=0, padx=15, pady=5)
            upload_button.grid(         row=2, column=2, padx=15, pady=5)
            
            upload_dropdown.set('')

            # # # # # # # # # # # # 
            #    DOWNLOAD PAGE    # 
            # # # # # # # # # # # # 

            home_page_tabview.add('Download')
            download_label=customtkinter.CTkLabel(home_page_tabview.tab('Download'),
                height=30,
                width=600,
                text='Download cloud files and overwrite local files',
                font=('Consolas', 16),
                wraplength=600
            )
            download_button=customtkinter.CTkButton(home_page_tabview.tab('Download'),
                height=30,
                width=250,
                text='Download',
                font=('Consolas', 20),
                command=lambda:[transfer(False, download_dropdown, misc_path_entry, upload_button, download_button)],
            )
            download_dropdown=customtkinter.CTkComboBox(home_page_tabview.tab('Download'),
                height=30,
                width=600,
                font=('Consolas', 20),
                values=[],
            )
            download_refresh_button=customtkinter.CTkButton(home_page_tabview.tab('Download'),
                height=30,
                width=250,
                text='Refresh',
                font=('Consolas', 20),
                command=lambda:[path_scan(False, download_dropdown,misc_path_entry, upload_button, download_button)],
            )

            for i in range(0,2):
                home_page_tabview.tab('Download').rowconfigure(i, weight=1)
                home_page_tabview.tab('Download').columnconfigure(i, weight=1)

            download_label.grid(          row=0, column=0, padx=15, pady=5, columnspan=3)
            download_dropdown.grid(       row=1, column=0, padx=15, pady=5, columnspan=3)
            download_refresh_button.grid( row=2, column=0, padx=15, pady=5)
            download_button.grid(         row=2, column=2, padx=15, pady=5)

            download_dropdown.set('')

            # # # # # # # # # # 
            #    MISC PAGE    # 
            # # # # # # # # # # 

            home_page_tabview.add('Misc')
            misc_path_label=customtkinter.CTkLabel(home_page_tabview.tab('Misc'),
                height=30,
                width=600,
                text='The folder that contains instances:',
                font=('Consolas', 16),
                wraplength=600
            )
            misc_path_entry=customtkinter.CTkEntry(home_page_tabview.tab('Misc'),
                height=30,
                width=600,
                placeholder_text='path/to/instances/folder',
                font=('Consolas', 20),
            )
            misc_path_button=customtkinter.CTkButton(home_page_tabview.tab('Misc'),
                height=30,
                width=250,
                text='Verify',
                font=('Consolas', 20),
                command=lambda:[path_verify(misc_path_entry, upload_button, download_button)],
            )
            misc_update_button=customtkinter.CTkButton(home_page_tabview.tab('Misc'),
                height=30,
                width=250,
                text='Update',
                font=('Consolas', 20),
                command=lambda:[self_update()],
            )

            for i in range(0,2):
                home_page_tabview.tab('Misc').rowconfigure(i, weight=1)
                home_page_tabview.tab('Misc').columnconfigure(i, weight=1)

            misc_path_label.grid(    row=0, column=0, padx=15, pady=5, columnspan=3)
            misc_path_entry.grid(    row=1, column=0, padx=15, pady=5, columnspan=3)
            misc_path_button.grid(   row=2, column=0, padx=15, pady=5)
            misc_update_button.grid( row=2, column=2, padx=15, pady=5)

            for tab_button in home_page_tabview._segmented_button._buttons_dict.values():
                tab_button.configure(height=30, width=120, font=('Consolas', 18))


    app=minecraftpackmanager()
    app.mainloop()


if __name__ == '__main__':
    platform_os=platform.system()
    if platform_os == 'Linux':
        platform_seperator='/'
    
    elif platform_os == 'Windows':
        platform_seperator='\\'

    main_file_path=os.path.realpath(__file__)

    root_venv_connector=f'apps{platform_seperator}minecraft-pack-manager'
    main_file_path_split=main_file_path.split(root_venv_connector)

    photon_root=main_file_path_split[0]
    internal_venv_path=main_file_path_split[1]

    if os.path.exists(os.path.join(photon_root, '.cache', 'PhotonVars.json')):
        with open(os.path.join(photon_root, '.cache', 'PhotonVars.json')) as PhotonVars_file:
            PhotonVars=json.load(PhotonVars_file)

    else:
        sys.exit('ERROR: missing variable file')


    if os.path.exists(os.path.join(photon_root, 'manifests', 'installed', 'minecraft-pack-manager.json')):
        with open(os.path.join(photon_root, 'manifests', 'installed', 'minecraft-pack-manager.json')) as Manifest_file:
            AppManifest=json.load(Manifest_file)

    else:
        sys.exit('ERROR: missing manifest file')


    main(PhotonVars, AppManifest)

