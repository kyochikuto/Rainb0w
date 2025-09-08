#!/usr/bin/env python3


import os
import re
import shutil
from time import sleep
from typing import List

from pick import pick
from rich import print

from base.config import (
    RAINB0W_BACKUP_DIR,
    RAINB0W_CONFIG_FILE,
    RAINB0W_USERS_FILE,
    SINGBOX_CONFIG_FILE,
)
from proxy.singbox import (
    disable_porn_dns_blocking,
    enable_porn_dns_blocking,
    revert_to_local_dns,
)
from user.user_manager import (
    add_user_to_proxies,
    create_new_user,
    get_users,
    print_client_info,
    remove_user,
)
from utils.helper import clear_screen, prompt_clear_screen
from utils.os_utils import is_network_stack_tweaked, is_service_running, run_system_cmd

NEED_SERVICE_RESTART = False


def performance_menu():
    title = "Select any option to optimize performance:"
    options = [
        "Revert Network Stack Optimizations"
        if is_network_stack_tweaked()
        else "Optimize Network Stack (BBR)",
        "Disable Zram Swap" if is_service_running("zramswap") else "Enable Zram Swap",
        "Back to Main Menu",
    ]
    option, _ = pick(options, title)
    if option == "Optimize Network Stack (BBR)":
        run_system_cmd([f"{os.getcwd()}/src/shell/performance/tune_kernel_net.sh"])
        prompt_clear_screen()
        performance_menu()
    elif option == "Revert Network Stack Optimizations":
        run_system_cmd([f"{os.getcwd()}/src/shell/performance/revert_kernel_net.sh"])
        prompt_clear_screen()
        performance_menu()
    elif option == "Enable Zram Swap":
        run_system_cmd([f"{os.getcwd()}/src/shell/performance/enable_zram.sh"])
        prompt_clear_screen()
        performance_menu()
    elif option == "Disable Zram Swap":
        run_system_cmd([f"{os.getcwd()}/src/shell/performance/disable_zram.sh"])
        prompt_clear_screen()
        performance_menu()
    dashboard()


def dns_controls_menu():
    global NEED_SERVICE_RESTART

    title = "Select any option:"
    options = [
        "Set DNS to AdGuard DNS Ad Filtering",
        "Set DNS to AdGuard DNS Family Protection",
        "Set DNS to local server",
        "Back to Main Menu",
    ]
    option, _ = pick(options, title)
    if option == "Set DNS to AdGuard DNS Family Protection":
        NEED_SERVICE_RESTART = True
        enable_porn_dns_blocking(SINGBOX_CONFIG_FILE)
        sleep(1)
        clear_screen()
        dns_controls_menu()
    elif option == "Set DNS to AdGuard DNS Ad Filtering":
        NEED_SERVICE_RESTART = True
        disable_porn_dns_blocking(SINGBOX_CONFIG_FILE)
        sleep(1)
        clear_screen()
        dns_controls_menu()
    elif option == "Set DNS to local server":
        NEED_SERVICE_RESTART = True
        revert_to_local_dns(SINGBOX_CONFIG_FILE)
        sleep(1)
        clear_screen()
        dns_controls_menu()
    dashboard()


def user_info_menu(user: str):
    global NEED_SERVICE_RESTART

    title = f"Select any option for {user}:"
    options = [
        "View Share URLs",
        "Remove User",
        "Back to Users Management Menu",
    ]
    option, _ = pick(options, title)
    if option == "View Share URLs":
        print_client_info(user, RAINB0W_USERS_FILE)
        prompt_clear_screen()
    elif option == "Remove User":
        title = f"Confirm removing '{user}'?"
        options = ["Yes", "No"]
        option, _ = pick(options, title)
        if option == "Yes":
            NEED_SERVICE_RESTART = True
            remove_user(
                user,
                RAINB0W_USERS_FILE,
                SINGBOX_CONFIG_FILE
            )
            clear_screen()
        else:
            user_info_menu(user)


def users_management_menu():
    global NEED_SERVICE_RESTART

    title = "Select any option:"
    options = [
        "Add a New User",
        "Back to Main Menu",
    ]
    # If we have existing users, display a numbered list of them in the menu
    usernames: List[str] = []
    users = get_users(RAINB0W_USERS_FILE)
    if users:
        for idx, user in enumerate(users):
            usernames.append(f"{idx}. {user['name']}")
        options[:0] = usernames
        title = "Add or remove a user:"
    option, _ = pick(options, title)
    if option == "Add a New User":
        username_input = input("Enter a name for the new user: ")
        if username_input:
            if any(user["name"] == username_input for user in users):
                print(f"A user with the given name '{username_input}' already exists!")
                prompt_clear_screen()
            else:
                NEED_SERVICE_RESTART = True
                user_info = create_new_user(username_input)
                add_user_to_proxies(
                    user_info,
                    RAINB0W_CONFIG_FILE,
                    RAINB0W_USERS_FILE,
                    SINGBOX_CONFIG_FILE
                )
                print(
                    "Changes only take effect after selecting 'Apply Changes' in the dashboard!"
                )
                prompt_clear_screen()
        users_management_menu()
    elif option in usernames:
        user = re.sub(r"^.*?\.\s*", "", str(option))
        user_info_menu(user)
        users_management_menu()
    elif option == "Back to Main Menu":
        dashboard()
    dashboard()


def backup():
    print(
        f"Backing up users and config files to [bold blue]'{RAINB0W_BACKUP_DIR}'[/bold blue]"
    )
    if not os.path.exists(RAINB0W_BACKUP_DIR):
        os.makedirs(RAINB0W_BACKUP_DIR)
    shutil.copyfile(
        RAINB0W_CONFIG_FILE,
        f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_CONFIG_FILE)}",
    )
    shutil.copyfile(
        RAINB0W_USERS_FILE,
        f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_USERS_FILE)}",
    )
    print("[bold green]Backup finished successfully.")
    prompt_clear_screen()
    dashboard()


def uninstall():
    title = """
Proceeding will stop and remove all Docker containers, volumes, networks and
revert all changes made to the system such as firewall settings and kernel tweaks!
Make sure you have made a backup of your configuration and users
if you'd like to restore them later on.

Do you confirm?
"""
    options = ["CANCEL", "OKAY"]
    option, _ = pick(options, title)
    if option == "OKAY":
        run_system_cmd([f"{os.getcwd()}/src/shell/uninstall.sh"])
        prompt_clear_screen()
        exit(0)
    else:
        dashboard()


def update():
    title = """
IMPORTANT: Proceeding will pull the latest Docker images of proxies and
update them on your system, BUT doing so without upgrading your CLIENT apps first
may cause connectivity issues, and you won't be able to connect until you upgrade your clients!
Please update your client apps first and then proceed here.

Do you want to continue?
"""
    options = ["CANCEL", "OKAY"]
    option, _ = pick(options, title)
    if option == "OKAY":
        run_system_cmd([f"{os.getcwd()}/src/shell/update.sh"])
    else:
        dashboard()


def dashboard():
    global NEED_SERVICE_RESTART
    title = """Choose any options to proceed:"""
    options = [
        "Performance Settings",
        "DNS Controls",
        "Manage Users",
        "Backup",
        "Uninstall",
        "Update",
        "Apply Changes" if NEED_SERVICE_RESTART else "Exit",
    ]
    option, _ = pick(options, title)
    if option == "Performance Settings":
        performance_menu()
    elif option == "DNS Controls":
        dns_controls_menu()
    elif option == "Manage Users":
        users_management_menu()
    elif option == "Backup":
        backup()
    elif option == "Uninstall":
        uninstall()
    elif option == "Update":
        update()
    elif option == "Apply Changes":
        clear_screen()
        print("Applying Changes!")
        # We let the parent bash process handle the rest
        exit(1)
    elif option == "Exit":
        print("Exiting!")
        exit(0)


if __name__ == "__main__":
    dashboard()
