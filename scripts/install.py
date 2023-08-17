import launch

if not launch.is_installed("wmi"):
    print("WMI is not installed. Installing...")
    launch.run_pip("install wmi")