from dataclasses import asdict, dataclass
import os
import subprocess
import threading
from tkinter.constants import DISABLED, NORMAL
import boto3
from botocore.exceptions import UnauthorizedSSOTokenError
from enum import StrEnum, auto
from pathlib import Path
from tkinter import Frame, Tk, Label, Entry, Button
import tomli
import tomli_w


# boto3.set_stream_logger('')  # debug

CONFIG_PATH = Path.home()/".ec2_dev_man"

@dataclass
class UserData:
    instance_id: str = ""
    profile: str = ""
    region: str = ""


class Status(StrEnum):
    RUNNING = auto()
    STOPPED = auto()
    PENDING = auto()
    UNKNOWN = auto()


user_data = UserData()
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "rb") as fh:
        user_data = UserData(**(tomli.load(fh)))


__client = None
def get_client():
    """
    Create and return an EC2 client
    """
    global __client
    if not __client:
        session = boto3.Session(
            profile_name=profile.get(),
            region_name=region.get()
        )
        __client = session.client("ec2")
    return __client


def clear_client(event):
    """
    Handler to refresh cached client
    """
    global __client
    __client = None


def _login(profile):
    """
    Call the AWS SSO login
    """
    try:
        subprocess.run(f"aws sso login --profile {profile}".split(" "), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error logging in: {e}")


def login():
    """
    Call the AWS SSO login in a background thread
    """
    threading.Thread(target=_login, args=[profile.get()]).start()


def start_instance():
    """
    Starts an EC2 instance with the provided ID.
    """
    response = get_client().start_instances(InstanceIds=[instance_id.get()])
    print(f"Instance {instance_id.get()} started successfully.")


def stop_instance():
    """
    Stops an EC2 instance with the provided ID.
    """
    response = get_client().stop_instances(InstanceIds=[instance_id.get()])
    print(f"Instance {instance_id.get()} stopped successfully.")


def reboot_instance():
    """
    Reboots an EC2 instance with the provided ID.
    """
    response = get_client().reboot_instances(InstanceIds=[instance_id.get()])
    print(f"Instance {instance_id.get()} is rebooting.")


def save_user_data():
    """
    Persist user settings
    """
    with open(CONFIG_PATH, "wb") as fh:
        tomli_w.dump(asdict(UserData(instance_id.get(), profile.get(), region.get())), fh)


def get_instance_state():
    """
    Retrieves the current state of the EC2 instance.
    """
    try:
        response = get_client().describe_instances(InstanceIds=[instance_id.get()])
        status_str = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        return Status(status_str)
    except UnauthorizedSSOTokenError as e:
        print(str(e))
        return Status.UNKNOWN


status_color_dict = {
    Status.STOPPED: "red",
    Status.RUNNING: "green",
    Status.UNKNOWN: "grey"
}


def update_instance_status(status_button: Button):
    """
    Updates the display based on the current state.
    """
    status = get_instance_state()
    status_button.config(text=str(status), background=status_color_dict.get(status))
    if status == Status.STOPPED:
        login_button.config(state=DISABLED)
        start_button.config(state=NORMAL)
        stop_button.config(state=DISABLED)
        reboot_button.config(state=DISABLED)
    if status == Status.RUNNING:
        login_button.config(state=DISABLED)
        start_button.config(state=DISABLED)
        stop_button.config(state=NORMAL)
        reboot_button.config(state=NORMAL)
    if status == Status.UNKNOWN:
        login_button.config(state=NORMAL)
        start_button.config(state=DISABLED)
        stop_button.config(state=DISABLED)
        reboot_button.config(state=DISABLED)



def perform_action(action):
    if action == "start":
        start_instance()
    elif action == "stop":
        stop_instance()
    elif action == "reboot":
        reboot_instance()
    elif action == "save":
        save_user_data()
    elif action == "login":
        login()
    else:
        print("Invalid action")  # Handle errors in the main GUI loop


# Create the main window
root = Tk()
root.title("EC2 Instance Manager")
root.resizable(False, False)

label_frame = Frame(root)
label_frame.grid(row=0, column=0)

Label(label_frame, text="Instance ID:").pack()
Label(label_frame, text="Profile:").pack()
Label(label_frame, text="Region:").pack()

entry_frame = Frame(root)
entry_frame.grid(row=0, column=1)

instance_id = Entry(entry_frame)
instance_id.insert(0, user_data.instance_id)
instance_id.pack()

profile = Entry(entry_frame)
profile.insert(0, user_data.profile)
profile.bind("<KeyRelease>", clear_client)
profile.pack()

region = Entry(entry_frame)
region.insert(0, user_data.region)
region.bind("<KeyRelease>", clear_client)
region.pack()

save_frame = Frame(root)
save_frame.grid(row=0, column=2)

save_id_button = Button(save_frame, text="Save", command=lambda: perform_action("save"))
save_id_button.pack(side="top", expand=True, fill="both")

action_frame = Frame(root)
action_frame.grid(row=2, columnspan=3)

login_button = Button(action_frame, text="Login", command=lambda: perform_action("login"))
start_button = Button(action_frame, text="Start", command=lambda: perform_action("start"))
stop_button = Button(action_frame, text="Stop", command=lambda: perform_action("stop"))
reboot_button = Button(action_frame, text="Reboot", command=lambda: perform_action("reboot"))
for button in [login_button, start_button, stop_button, reboot_button]:
    button.pack(side="left")

status_frame = Frame(root)
status_frame.grid(row=3, columnspan=3)

status_button = Button(status_frame)
status_button.pack(side="bottom")


# Poll status
def poll_instance_status():
  update_instance_status(status_button)
  root.after(3000, poll_instance_status)  # Call again after 3 seconds


if __name__ == '__main__':
    poll_instance_status()
    root.mainloop()
