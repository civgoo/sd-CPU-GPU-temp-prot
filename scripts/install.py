import launch

if not launch.is_installed("wmi"):
    launch.run_pip("install wmi")