
![ComfyUI_00026_](https://github.com/user-attachments/assets/57fdbf91-51d5-43ad-9ec7-3873003dca1b)

<div align="center"><h1>ComfyUI MUSUBI-TUNNER WAN LORA TRAINER</h1></div>

* ComfyUi lora trainer.
* Adaptation of the musubi-tunner library by kohya-ss. From https://github.com/kohya-ss/musubi-tuner.
* Added train into subprocess.
* Code mods for full compatibility with the last version of ComfyUi.
* Added 6 nodes for training.
* Added Example Workflow in the custom node folder.
* Made for ComfyUi windows portable package.
* Automated process for the creation of the TOM file, cache latents, cache texts & trainning run (Nodes triggered by this order to do the complete process in one shot).
* You can skip latents and text caches if you need to restart the training (taking into account data has not changed vae, clipvision, text models).

Instructions:
1. Clone this repository into your custom node folder.
2. install requirements.txt from custom_nodes\ComfyUI_Wan2_1_lora_trainer :
```

..\..\..\python -m pip install -r requirements.txt

```
3. run comfyUi
4. Enjoy training.


Regular run: If you use regular bat you must to bypass compiler an memory settings (attention mode in spda). (Look at the picture)
![image](https://github.com/user-attachments/assets/03bebfca-79c2-4079-aea4-0f0b7dfc5645)



Torch settings run : 
If you have the last version of torch 2.7.0 cuda and visual studio tools, you can create/modify a Bat file using the visual Studio environment:

```
@echo off
REM Load Visual Studio Build Tools for the Wan subprocess environment (Optional to use max pow with the musubi compile settings and memory nodes)
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64
REM Start ComfyUI
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --use-sage-attention --fast fp16_accumulation
pause
```
Note : Activating torch wihtout calling the Sage argument will cause an invalid Lora.

Then activate the compiler nodes (choose sage attention o wich one you want based on your configs):
![image](https://github.com/user-attachments/assets/8982f665-a7bd-47a1-a8eb-ad6bce87b7f2)


if you don't have any of this modules you can disconnect the musubi compile settings node.


Performances test with 312 images [torch 2.7.0 cuda128 + sage attention] :


![Captura de pantalla 2025-05-21 044524](https://github.com/user-attachments/assets/b9ec9f8a-daee-4e0b-a72c-91ff29950a7f)

* Image data input are not exclusive to videos! you can train just with images as the following example (path to your images and text captions):

![Captura de pantalla 2025-05-23 161441](https://github.com/user-attachments/assets/465448fe-f347-431f-b3e7-e13436d5c039)

* Path into an empty folder for the cache (use different folders for each lora to not mix you cache data (cleaner and probably faster).
  
And the results :

https://github.com/user-attachments/assets/41b439ee-6e90-49ac-83dd-d1ba21fd1d63



Important note : settings shown in pictures does not represent the proper one for X purpose, it was just screenshots in different tests. To get the Default setting go to https://github.com/jaimitoes/ComfyUI_Wan2_1_lora_trainer/blob/main/docs/wan.md



