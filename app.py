from configparser import ConfigParser, NoOptionError, NoSectionError
import os
import boto3
from pathlib import Path
from tkinter import Tk, Label, Entry, Button


# boto3.set_stream_logger('')  # debug


def get_instance_id():
    """
    Retrieve saved instance ID.
    """
    config_path = Path.home()/".aws_instance_id"
    if os.path.exists(config_path):
        with open(config_path, "r") as fh:
            return fh.read().strip()
    return ""


def save_instance_id(instance_id):
    """
    Save instance ID for next time.
    """
    config_path = Path.home()/".aws_instance_id"
    with open(config_path, "w") as fh:
        fh.write(instance_id)


# Create an EC2 client object
session = boto3.Session(profile_name="sus-acc", region_name="eu-west-2")
ec2_client = session.client("ec2")


def start_instance(instance_id):
    """
    Starts an EC2 instance with the provided ID.
    """
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} started successfully.")
    except Exception as e:
        print(f"Error starting instance {instance_id}: {e}")


def stop_instance(instance_id):
    """
    Stops an EC2 instance with the provided ID.
    """
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} stopped successfully.")
    except Exception as e:
        print(f"Error stopping instance {instance_id}: {e}")


def reboot_instance(instance_id):
    """
    Reboots an EC2 instance with the provided ID.
    """
    try:
        response = ec2_client.reboot_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} is rebooting.")
    except Exception as e:
        print(f"Error rebooting instance {instance_id}: {e}")


def perform_action(instance_id, action):
    if action == "start":
        start_instance(instance_id.get())
    elif action == "stop":
        stop_instance(instance_id.get())
    elif action == "reboot":
        reboot_instance(instance_id.get())
    elif action == "save_id":
        save_instance_id(instance_id.get())
    else:
        print("Invalid action")  # Handle errors in the main GUI loop


# Create the main window
root = Tk()
root.title("EC2 Instance Manager")

# Instance ID label and entry
instance_id_label = Label(root, text="Instance ID:")
instance_id_label.pack()

instance_id = Entry(root)
instance_id.insert(0, get_instance_id())
instance_id.pack()

# Action buttons
start_button = Button(root, text="Start", command=lambda: perform_action(instance_id, "start"))
start_button.pack(side="left")

stop_button = Button(root, text="Stop", command=lambda: perform_action(instance_id, "stop"))
stop_button.pack(side="left")

reboot_button = Button(root, text="Reboot", command=lambda: perform_action(instance_id, "reboot"))
reboot_button.pack(side="left")

save_id_button = Button(root, text="Save ID", command=lambda: perform_action(instance_id, "save_id"))
save_id_button.pack(side="left")

# Run the main event loop
root.mainloop()
