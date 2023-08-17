# CPU/GPU temperature protection
### Pause image generation when CPU or GPU temperature exceeds threshold
this extension uses nvidia-smi to monitor CPU/GPU temperature at the end of each step, if temperature exceeds threshold pause image generation until criteria are met.

## Requirements
Nvidia GPU

Open Hardware Monitor
https://openhardwaremonitor.org/downloads/ 

This extension was only tested and developed for windows OS. It will likely not work on other OS due to the use of wmi package.

## Installation
- method 1: Install using extensions tab `Available` extensions
- method 2: Install using extensions tab `Install from URL` by manually copying the repository URL
```
https://github.com/asd417/stable-diffusion-webui-GPU-temperature-protection
```

## Setting
Settings can be found at `Setting` > `CPU-GPU Temperature`

- `GPU temperature monitor minimum interval`
    - checking temperature too often will reduce image generation performance
    - set to `0` well effectively disable this extension
    - to completely disable extension disable the file extension tab
- `GPU sleep temperature`
    - generation will pause if GPU core temperature exceeds this temperature
- `GPU wake temperature`
    - generation will continue to pause until temperature has drops below this temperature 
    - setting a higher value than `GPU sleep temperature`will effectively disable this
- `Sleep Time`
    - seconds to sleep before checking temperature again
- `Max sleep Time` 
    - max number of seconds that it's allowed to pause
    - generation will continue disregarding `GPU wake temperature` after the allotted time has passed
    - set to `0` disable this limit allowing it to pause indefinitely
- `Print GPU Core temperature while sleeping in terminal`
    - print the GPU core temperature reading from nvidia-smi to console when generation is paused
    - providing information
- `GPU device index`
    - selecting the correct temperature reading for multi GPU systems
    - in most cases and for single GPU system this value should be `0`
 
- Same settings for CPU as well.
- If you have the original extension installed, the gpu settings will only appear on the original extension's setting page

## Notes
- Temperature unit Celsius, Time unit seconds
- To be honest I don't recommend anyone using this extension, if your GPU is having temperature issues and don't have the means to improve the cooling, then recommend using software like MSI afterburner to undervolt or further power limit or thermal limit the GPU.
