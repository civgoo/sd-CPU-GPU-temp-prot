import wmi
import subprocess as sp

result=[]
#path = "C:\\Users\\locti\\OneDrive\\Documents\\OpenHardwareMonitor.exe"
#prog = sp.Popen(['runas', '/profile', '/user:locti', path],stdin=sp.PIPE)

w = wmi.WMI(namespace="root\OpenHardwareMonitor")

temperature_infos = w.Sensor()
print(temperature_infos)
for sensor in temperature_infos:
    if sensor.SensorType=='Temperature':
        temperature=(sensor.Name, sensor.Value)

        if temperature[0].startswith("CPU"):
            result.append(temperature)
        elif temperature[0].startswith("GPU"):
            result.append(temperature)

print(result)
