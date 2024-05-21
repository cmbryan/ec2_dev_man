from configparser import ConfigParser, NoOptionError, NoSectionError
import os
import boto3
from pathlib import Path
from tkinter import Frame, Tk, Label, Entry, Button


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


def get_instance_state(instance_id):
    """
    Retrieves the current state of the EC2 instance.
    """
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        return response["Reservations"][0]["Instances"][0]["State"]["Name"]
    except Exception as e:
        print(f"Error getting instance state: {e}")


status_color_dict = {
    "stopped": "red",
    "running": "green",
}


def update_instance_status(instance_id_text_field: Label, status_button: Button):
    """
    Updates the status based on the current state.
    """
    status = get_instance_state(instance_id_text_field.get())
    if status:
        status_button.config(text=status, background=status_color_dict.get(status, "grey"))
    else:
        status_button.config(text="Error retrieving status")


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

button_frame = Frame(root)
button_frame.pack()

# Action buttons
start_button = Button(button_frame, text="Start", command=lambda: perform_action(instance_id, "start"))
start_button.pack(side="left")

stop_button = Button(button_frame, text="Stop", command=lambda: perform_action(instance_id, "stop"))
stop_button.pack(side="left")

reboot_button = Button(button_frame, text="Reboot", command=lambda: perform_action(instance_id, "reboot"))
reboot_button.pack(side="left")

save_id_button = Button(button_frame, text="Save ID", command=lambda: perform_action(instance_id, "save_id"))
save_id_button.pack(side="left")

# Status
status_button = Button(root)
status_button.pack()


# Poll status
def poll_instance_status():
  update_instance_status(instance_id, status_button)
  root.after(3000, poll_instance_status)  # Call again after 3 seconds
poll_instance_status()

# Run the main event loop
root.mainloop()
