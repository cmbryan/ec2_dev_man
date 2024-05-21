build:
	pyinstaller app.py --name ec2_dev_man --onefile

clean:
	rm -rf build dist
