from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import scripts, shared
import gradio as gr
import subprocess
import time

import pythoncom
import wmi

shared.options_templates.update(shared.options_section(('CPU_GPU_temperature_protection', "CPU-GPU Temperature"), {
    "gpu_temps_sleep_enable": shared.OptionInfo(True, "Enable GPU temperature protection"),
    "gpu_temps_sleep_print": shared.OptionInfo(True, "Print GPU Core temperature while sleeping in terminal"),
    "gpu_temps_sleep_minimum_interval": shared.OptionInfo(5.0, "GPU temperature monitor minimum interval", gr.Number).info("won't check the temperature again until this amount of seconds have passed"),
    "gpu_temps_sleep_sleep_time": shared.OptionInfo(1.0, "Sleep Time", gr.Number).info("seconds to pause before checking temperature again"),
    "gpu_temps_sleep_max_sleep_time": shared.OptionInfo(10.0, "Max sleep Time", gr.Number).info("max number of seconds that it's allowed to pause, 0=unlimited"),
    "gpu_temps_sleep_sleep_temp": shared.OptionInfo(75.0, "GPU sleep temperature", gr.Slider, {"minimum": 0, "maximum": 125}).info("generation will pause if GPU core temperature exceeds this temperature"),
    "gpu_temps_sleep_wake_temp": shared.OptionInfo(75.0, "GPU wake temperature", gr.Slider, {"minimum": 0, "maximum": 125}).info("generation will pause until GPU core temperature drops below this temperature"),
    "gpu_temps_sleep_gpu_index": shared.OptionInfo(0, "GPU device index", gr.Number, {"precision": 0}).info("selecting the correct temperature reading for multi GPU systems, for systems with 3 gpus the value should be an integer between 0~2, default 0"),
    
    "cpu_temps_sleep_enable": shared.OptionInfo(True, "Enable CPU temperature protection"),
    "cpu_temps_sleep_print": shared.OptionInfo(True, "Print CPU Core temperature while sleeping in terminal"),
    "cpu_temps_sleep_sleep_temp": shared.OptionInfo(75.0, "CPU sleep temperature", gr.Slider, {"minimum": 0, "maximum": 125}).info("generation will pause if CPU core temperature exceeds this temperature"),
    "cpu_temps_sleep_wake_temp": shared.OptionInfo(75.0, "CPU wake temperature", gr.Slider, {"minimum": 0, "maximum": 125}).info("generation will pause until CPU core temperature drops below this temperature"),
}))


class GPUTemperatureProtection(scripts.Script):
    def title(self):
        return "GPU temperature protection"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def process(self, p, *args):
        
        if shared.opts.gpu_temps_sleep_enable:
            setattr(KDiffusionSampler, "callback_state", GPUTemperatureProtection.gpu_temperature_protection_decorator(KDiffusionSampler.callback_state))

    @staticmethod
    def get_gpu_temperature():
        try:
            return int(subprocess.check_output(
                ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader']).decode().strip().splitlines()[shared.opts.gpu_temps_sleep_gpu_index])
        except subprocess.CalledProcessError as e:
            print(f"[Error GPU temperature protection]: {e.output.decode('utf-8').strip()}")
        except Exception as e:
            print(f'[Error GPU temperature protection]: {e}')
        return 0
    
    @staticmethod
    def get_cpu_temperature():
        
        pythoncom.CoInitialize()
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        temperature_infos = w.Sensor()
        if temperature_infos == []:
            print("OpenHardwareMonitor.exe is not running. CPU protection is DISABLED")
            return 0
        cputemp = 0
        for sensor in temperature_infos:
            if sensor.SensorType=='Temperature':
                #temperature=(sensor.Name, sensor.Value)
                if sensor.Name.startswith("CPU"):
                    cputemp = sensor.Value
        return cputemp

    @staticmethod
    def gpu_temperature_protection():
        if shared.opts.gpu_temps_sleep_enable:
            call_time = time.time()
            if call_time - GPUTemperatureProtection.last_call_time > shared.opts.gpu_temps_sleep_minimum_interval:
                gpu_core_temp = GPUTemperatureProtection.get_gpu_temperature()
                cpu_temp = GPUTemperatureProtection.get_cpu_temperature()
                if gpu_core_temp > shared.opts.gpu_temps_sleep_sleep_temp or cpu_temp > shared.opts.cpu_temps_sleep_sleep_temp:
                    
                    if shared.opts.gpu_temps_sleep_print or shared.opts.cpu_temps_sleep_print:
                        print(f'\n\nPausing Generation for Device Protection')

                    time.sleep(shared.opts.gpu_temps_sleep_sleep_time)

                    pausegen = True
                    while pausegen:
                        if shared.opts.gpu_temps_sleep_print:
                            print(f'GPU Temperature: {gpu_core_temp}')
                        if shared.opts.cpu_temps_sleep_print:
                            print(f'CPU Temperature: {cpu_temp}')

                        time.sleep(shared.opts.gpu_temps_sleep_sleep_time)

                        gpu_core_temp = GPUTemperatureProtection.get_gpu_temperature()
                        cpu_temp = GPUTemperatureProtection.get_cpu_temperature()

                        pausegen_gpu = gpu_core_temp > shared.opts.gpu_temps_sleep_wake_temp and (not shared.opts.gpu_temps_sleep_max_sleep_time or shared.opts.gpu_temps_sleep_max_sleep_time > time.time() - call_time) and shared.opts.gpu_temps_sleep_enable
                        pausegen_cpu = cpu_temp > shared.opts.cpu_temps_sleep_wake_temp and (not shared.opts.gpu_temps_sleep_max_sleep_time or shared.opts.gpu_temps_sleep_max_sleep_time > time.time() - call_time) and shared.opts.cpu_temps_sleep_enable
                        pausegen = pausegen_gpu or pausegen_cpu
                        
                    GPUTemperatureProtection.last_call_time = time.time()
                else:
                    GPUTemperatureProtection.last_call_time = call_time

    @staticmethod
    def gpu_temperature_protection_decorator(fun):
        def wrapper(*args, **kwargs):
            result = fun(*args, **kwargs)
            GPUTemperatureProtection.gpu_temperature_protection()
            return result
        return wrapper

    last_call_time = time.time()
