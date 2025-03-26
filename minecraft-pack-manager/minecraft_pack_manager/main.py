import os
import sys
import subprocess
import json
import threading

import customtkinter

from tkinter import PhotoImage


def center_window(window_width, window_height, window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

def invalid_path_popup(platform_os, photon_root):
    pop=customtkinter.CTkToplevel()
    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme('green')
    pop.title('Photon')
    # image = PhotoImage(file=os.path.join(photon_root, 'assets', 'warning.png'))
    # pop.wm_iconphoto(True, image)
    # center_window(400, 100, pop)
    pop.geometry('400x100')
    customtkinter.CTkLabel(pop, text='Invalid file path', font=('Consolas', 32)).pack(fill='both', expand=True)
    pop.lift()
    pop.mainloop()
    pop.lift()


def path_seperators(platform_os):
    seperators=[]
    for seperator in os.path.sep, os.path.altsep:
        if seperator:
            seperators.append(seperator)
            if platform_os == 'Windows':
                break
    return seperators


def file_path_check(platform_os, photon_root, widget, instances_folder=None):
    if instances_folder == None:
        instances_folder=widget.get()
    if (instances_folder in ['', None]) or (' ' in instances_folder):
        invalid_path_popup(platform_os, photon_root)
        return(instances_folder, False)

    for seperator in path_seperators(platform_os):
        setting_value=instances_folder.removesuffix(seperator)
        instances_folder_split=instances_folder.split(seperator)
        if len(instances_folder_split) < 3:
            invalid_path_popup(platform_os, photon_root)
            return(instances_folder, False)

    setting_value='\\'.join(instances_folder_split)
    if not os.path.exists(instances_folder):
        setting_value='/'.join(instances_folder_split)
        if not os.path.exists(instances_folder):
            invalid_path_popup(platform_os, photon_root)
            return(instances_folder, False)

    return(instances_folder, True)


def settings_update(platform_os, photon_root, AppCommandName, setting, setting_value=None, widget=None):
    # default_settings='{"DarkTheme":true, "DesktopShortcut":true}'
    # os.makedirs(os.path.join(photon_root, 'settings', AppCommandName), exist_ok=True)
    # with open(os.path.join(photon_root, 'settings', AppCommandName, 'user_settings.json'), 'r') as user_settings_file:
    #     try:
    #         user_settings_json=json.load(user_settings_file)
    #     except Exception as error:
    #         print(error)
    #         user_settings_json=json.loads(default_settings)

    file_path_check(platform_os, photon_root, widget)

    # user_settings_json[setting]=setting_value

    # with open(os.path.join(photon_root, 'settings', AppCommandName, 'user_settings.json'), 'w+') as user_settings_file:
        # json.dump(user_settings_json, user_settings_file)


def refresh_available_upload(platform_os,  photon_root, rclone_exe, widget, dropdown):
    print('refresh upload')
    (instances_folder, bool)=file_path_check(platform_os,  photon_root, widget)
    if bool:
        local_instances=[]
        for name in os.listdir(instances_folder):
            if os.path.isdir(os.path.join(instances_folder, name)):
                local_instances.append(name)
        try:
            local_instances.remove('_LAUNCHER_TEMP')
        except ValueError as error:
            print (error)

        dropdown.configure(values=local_instances)

    else:
        return


def refresh_available_download(platform_os,  photon_root, rclone_exe, widget, dropdown, rclone_config):
    print('refresh download')
    (instances_folder, bool)=file_path_check(platform_os,  photon_root, widget)
    if bool:
        def update_thread():
            remote_instances=[]
            rc_cmd=subprocess.run([rclone_exe, 'lsjson', 'GDR:', '--max-depth=3', '--dirs-only', '--no-modtime', '--no-mimetype', f'--config={rclone_config}'], capture_output=True, text=True)
            rcjson=json.loads(rc_cmd.stdout)

            for obj in rcjson:
                if obj['Path'].endswith('/Modpacks') or obj['Path'].endswith('/mods') or obj['Path'] in ['AC1', 'AC2', 'AC3']:
                    pass
                else:
                    remote_instances.append(obj['Path'])

            dropdown.configure(values=remote_instances)

        threading.Thread(target=update_thread, daemon=True).run()

    else:
        return


def upload_instance(platform_os, photon_root, widget, dropdown, rclone_exe, rclone_config):
    instance=dropdown.get().strip()
    if instance in ['', None]:
        return
    (instances_folder, bool)=file_path_check(platform_os, photon_root, widget)
    print('uploading %s' % instance)

    if instance == 'TechPack':
        ACN='AC1'
    elif instance == 'Cobblemon Modpack [Fabric]':
        ACN='AC2'
    else:
        ACN='AC3'

    rclone_cmd=[f'{rclone_exe}', 'sync', 
        f'{os.path.join(instances_folder, instance)}', 
        f'GDR:{os.path.join(ACN, 'Modpacks', instance)}', 
        '--transfers=20', '--checkers=50', '--fast-list', '--max-backlog=-1', '-P', 
        '--exclude="{logs/**, backups/**, options.txt}"', 
        f'--config={rclone_config}'
    ]
    print(rclone_cmd)
    transfer=subprocess.run(rclone_cmd, capture_output=True, text=True)
    print('-----')
    print(transfer.stdout)
    print(transfer.stdout)


def download_instance(platform_os, photon_root, widget, dropdown, rclone_exe, rclone_config):
    instance=dropdown.get().strip()
    if instance in ['', None]:
        return
    (instances_folder, bool)=file_path_check(platform_os, photon_root, widget)
    print('downloading %s' % instance)
    instance_path=instance
    instance_split=instance.split('/')
    instance=instance_split[2]

    rclone_cmd=[f'{rclone_exe}', 'sync',
        f'GDR:{instance_path}' ,
        f'{os.path.join(instances_folder, instance)}',
        '--transfers=20', '--checkers=50', '--fast-list', '--max-backlog=-1', '-P', 
        '--exclude="{logs/**, backups/**, options.txt}"', 
        f'--config={rclone_config}'
    ]
    print(rclone_cmd)
    transfer=subprocess.run(rclone_cmd, capture_output=True, text=True)
    print('-----')
    print(transfer.stdout)
    print(transfer.stdout)


def update(platform_os, venv_internal, venv_bin, photon_root, AppFolderName, AppDisplayName, AppCommandName):
    for cmd in ['python', 'python3', 'py']:
        try:
            subprocess.Popen([cmd, os.path.join(photon_root, 'update.py'), platform_os, venv_internal, venv_bin, photon_root, AppFolderName, AppDisplayName, AppCommandName])
        except:
            pass
        else:
            break
    sys.exit()


def main(platform_os, venv_internal, venv_bin, photon_root, AppFolderName, AppDisplayName, AppCommandName):
    rclone_config=os.path.join(photon_root, 'settings', 'rclone.conf')

    root=customtkinter.CTk()

    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme('green')

    root.title(AppDisplayName)
    if platform_os == 'Linux':
        rclone_exe=os.path.join(photon_root, 'tools', 'rclone')
    elif platform_os == 'Windows':
        rclone_exe=os.path.join(photon_root, 'tools', 'rclone.exe')
    image = PhotoImage(file=os.path.join(photon_root, 'assets', 'minecraft.png'))
    root.wm_iconphoto(True, image)
    try:
        root.wm_iconbitmap(default='minecraft.ico')
    except:
        pass
    center_window(600, 280, root)

    tabs=customtkinter.CTkTabview(root, fg_color='transparent')
    for tab_name in ['Upload', 'Download', 'Settings']:
        tabs.add(tab_name)
        # if tab_name != 'Settings':
        for i in range(3):
            tabs.tab(tab_name).rowconfigure(i, weight=1)
        tabs.tab(tab_name).columnconfigure(0, weight=1)
        tabs.tab(tab_name).columnconfigure(1, weight=10)
        tabs.tab(tab_name).columnconfigure(2, weight=1)

    title=customtkinter.CTkLabel(root, text=AppDisplayName, font=('Consolas', 32))

    title.pack(side='top', fill='both', expand=True)
    tabs.pack(side='top', fill='both', expand=True)

    ##########  UPLOAD  ##########

    upload_page_description_label=customtkinter.CTkLabel(tabs.tab('Upload'),
        height=25,
        width=120,
        text='Upload and overwrite cloud files',
        font=('Consolas', 20),
    )
    upload_page_selection_dropdown=customtkinter.CTkComboBox(tabs.tab('Upload'),
        height=25,
        width=120,
        font=('Consolas', 20),
        values=[],
    )
    upload_page_refresh_button=customtkinter.CTkButton(tabs.tab('Upload'),
        height=25,
        width=120,
        text='Refresh',
        font=('Consolas', 20),
        command=lambda:[
            refresh_available_upload(platform_os,  photon_root, rclone_exe, settings_page_entry, upload_page_selection_dropdown)
        ],
    )
    upload_page_upload_button=customtkinter.CTkButton(tabs.tab('Upload'),
        height=25,
        width=120,
        text='Upload',
        font=('Consolas', 20),
        command=lambda:[
            upload_instance(platform_os, photon_root, settings_page_entry, upload_page_selection_dropdown, rclone_exe, rclone_config)
        ],
    )
    upload_page_exit_button=customtkinter.CTkButton(tabs.tab('Upload'),
        height=25,
        width=120,
        text='Exit',
        font=('Consolas', 20),
        command=lambda:[
            print(sys.exit(0))
        ],
    )

    upload_page_description_label.grid(  row=0, column=0, padx=15, pady=15, sticky='ew', columnspan=3)
    upload_page_selection_dropdown.grid( row=1, column=0, padx=15, pady=15, sticky='ew', columnspan=2)
    upload_page_refresh_button.grid(     row=1, column=2, padx=15, pady=15, sticky='ew')
    upload_page_upload_button.grid(      row=2, column=0, padx=15, pady=15, sticky='ew')
    upload_page_exit_button.grid(        row=2, column=2, padx=15, pady=15, sticky='ew')

    upload_page_selection_dropdown.set('')

    ##########  DOWNLOAD    ##########

    download_page_description_label=customtkinter.CTkLabel(tabs.tab('Download'),
        height=25,
        width=120,
        text='Download and overwrite local files',
        font=('Consolas', 20),
    )
    download_page_selection_dropdown=customtkinter.CTkComboBox(tabs.tab('Download'),
        height=25,
        width=120,
        font=('Consolas', 20),
        values=[],
    )
    download_page_refresh_button=customtkinter.CTkButton(tabs.tab('Download'),
        height=25,
        width=120,
        text='Refresh',
        font=('Consolas', 20),
        command=lambda:[
            refresh_available_download(platform_os,  photon_root, rclone_exe, settings_page_entry, download_page_selection_dropdown, rclone_config)
        ],
    )
    download_page_download_button=customtkinter.CTkButton(tabs.tab('Download'),
        height=25,
        width=120,
        text='Download',
        font=('Consolas', 20),
        command=lambda:[
            download_instance(platform_os, photon_root, settings_page_entry, download_page_selection_dropdown, rclone_exe, rclone_config)
        ],
    )
    download_page_exit_button=customtkinter.CTkButton(tabs.tab('Download'),
        height=25,
        width=120,
        text='Exit',
        font=('Consolas', 20),
        command=lambda:[
            print(sys.exit(0))
        ],
    )

    download_page_description_label.grid(  row=0, column=0, padx=15, pady=15, sticky='ew', columnspan=3)
    download_page_selection_dropdown.grid( row=1, column=0, padx=15, pady=15, sticky='ew', columnspan=2)
    download_page_refresh_button.grid(     row=1, column=2, padx=15, pady=15, sticky='ew')
    download_page_download_button.grid(    row=2, column=0, padx=15, pady=15, sticky='ew')
    download_page_exit_button.grid(        row=2, column=2, padx=15, pady=15, sticky='ew')

    download_page_selection_dropdown.set('')

    ##########  SETTINGS    ##########

    settings_page_description_label=customtkinter.CTkLabel(tabs.tab('Settings'),
        height=20,
        width=120,
        text='The folder to upload from or download to',
        font=('Consolas', 20),
    )
    settings_page_entry=customtkinter.CTkEntry(tabs.tab('Settings'),
        height=20,
        width=120,
        placeholder_text='path/to/instances/folder',
        font=('Consolas', 20),
    )
    settings_page_apply_button=customtkinter.CTkButton(tabs.tab('Settings'),
        height=20,
        width=120,
        text='Apply',
        font=('Consolas', 20),
        command=lambda:[
            settings_update(
                platform_os, 
                photon_root,
                AppCommandName,
                'InstancePath',
                widget=settings_page_entry
        )],
    )    
    settings_page_update_button=customtkinter.CTkButton(tabs.tab('Settings'), 
        height=20,
        width=120,
        text='Update', 
        font=('Consolas', 20),
        command=lambda:[update(
            platform_os,
            venv_internal,
            venv_bin, 
            photon_root, 
            AppFolderName, 
            AppDisplayName, 
            AppCommandName
        )]
    )
    settings_page_exit_button=customtkinter.CTkButton(tabs.tab('Settings'), 
        height=20,
        width=120,
        text='Exit',
        font=('Consolas', 20),
        command=lambda:[
            print(sys.exit(0))
        ],
    )

    settings_page_description_label.grid( row=0, column=0, padx=15, pady=15, sticky='ew', columnspan=3)
    settings_page_entry.grid(             row=1, column=0, padx=15, pady=15, sticky='ew', columnspan=2)
    settings_page_apply_button.grid(      row=1, column=2, padx=15, pady=15, sticky='ew')
    settings_page_update_button.grid(     row=2, column=0, padx=15, pady=15, sticky='ew')
    settings_page_exit_button.grid(       row=2, column=2, padx=15, pady=15, sticky='ew')


    root.mainloop()


if __name__ == '__main__':
    required_args=['platform_os', 'venv_internal', 'venv_bin', 'photon_root', 'AppFolderName', 'AppDisplayName', 'AppCommandName']
    i=0
    for arg in required_args:
        x=i
        i=i+1
        try:
            required_args[x]=sys.argv[i]
        except:
            sys.exit('this file should not be ran directly, use photon')

    try:
        main(required_args[0], required_args[1], required_args[2], required_args[3], required_args[4], required_args[5], required_args[6])
    except TypeError as error:
        print(error)
        sys.exit('this file should not be ran directly, use photon')

