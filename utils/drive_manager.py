import os
import platform
import shutil
import subprocess


class DriveManager:
    def __init__(self):
        self.system = platform.system()
        self.drives = []

    def get_available_drives(self):
        """Detects available drives on the system."""
        self.drives = []
        if self.system == "Windows":
            # Use wmic or simple drive letter check
            for letter in "EFGHIJKLMNOPQRSTUVWXYZ":
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        # Try to get volume label
                        cmd = f"vol {letter}:"
                        # shell=True is required for Windows internal command 'vol'
                        output = subprocess.check_output(cmd, shell=True)  # nosec
                        label = output.decode().split()[-1]
                    except Exception:
                        label = "Unknown"

                    self.drives.append(
                        {"letter": f"{letter}:", "path": drive, "label": label}
                    )
        return self.drives

    def backup_project(self, target_drive_letter, source_dir="D:\\GenX_FX"):
        """Backs up the project to a specific drive."""
        target_path = os.path.join(f"{target_drive_letter}\\", "GenX_FX_Backup")
        if not os.path.exists(source_dir):
            print(f"Error: Source directory {source_dir} not found.")
            return False

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(f"Backing up {source_dir} to {target_path}...")

        # Define what to backup
        subdirs = ["credentials", "configs", "expert-advisors", "logs"]
        for subdir in subdirs:
            src = os.path.join(source_dir, subdir)
            dst = os.path.join(target_path, subdir)
            if os.path.exists(src):
                print(f"Copying {subdir}...")
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

        # Copy root files
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(target_path, "project", item)
            valid_ext = (
                item.endswith(".py")
                or item.endswith(".bat")
                or item == "requirements.txt"
            )
            if os.path.isfile(s) and valid_ext:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)

        print("Backup completed successfully.")
        return True


def main():
    manager = DriveManager()
    print("GenX FX Drive Manager")
    print("----------------------")

    drives = manager.get_available_drives()
    if not drives:
        print("No USB drives detected.")
        return

    print("Available Drives:")
    for i, drive in enumerate(drives):
        print(f"{i+1}. {drive['letter']} ({drive['label']})")

    choice = input("\nSelect a drive for backup (or 'all'): ")
    if choice.lower() == "all":
        for drive in drives:
            manager.backup_project(drive["letter"])
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(drives):
                manager.backup_project(drives[idx]["letter"])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


if __name__ == "__main__":
    main()
