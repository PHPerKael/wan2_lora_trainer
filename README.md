* ComfyUi lora trainer.
* Adaptation of the musubi-tunner library from https://github.com/kohya-ss/musubi-tuner.
* Added train into subprocess.
* Code mods for full compatibility with the last version of ComfyUi.
* Added 6 nodes for training.
* Added Example Workflow in the custom node folder.
* Made for ComfyUi windows portable package.

* ![image](https://github.com/user-attachments/assets/cce68c8f-9ae7-4de2-b5a0-be6f0d11b2cd)



Instructions:
1. Clone this repository into your custom node folder.
2. install requirements.txt from custom_nodes\ComfyUI_Wan2_1_lora_trainer : ..\..\..\python -m pip install -r requirements.txt
3. run comfyUi
4. Enjoy training.


Optional :
![image](https://github.com/user-attachments/assets/bc07a0f6-1fc3-4f4e-b511-71d8ad8d5b7e)

If you have the last version of torch 2.7.0 cuda and visual studio tools, you can modify your Bat file Comfy runner with this:

```
@echo off
REM Load Visual Studio Build Tools for the Wan subprocess environment (Optional to use max pow with the musubi compile settings and memory nodes)
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64
REM Start ComfyUI
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --fast fp16_accumulation
pause
```

if you don't have any of this modules you can disconnect the musubi compile settings node.

![image](https://github.com/user-attachments/assets/fc7f34fe-6c47-49d2-a15b-c44232c1db56)

