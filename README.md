![ComfyUI_00026_](https://github.com/user-attachments/assets/57fdbf91-51d5-43ad-9ec7-3873003dca1b)

<div align="center"><h1>ComfyUI MUSUBI-TUNNER WAN LORA TRAINER</h1></div>


✅ MODEL STRENGTH FIXED!.

**Update version 1.01**:
* Fixed as default the learning parameters (A good starting point to see quickly results just loading the nodes).
* Added number of cpu per process argument.
* Added max_train_epochs argument to avoid the internal step limit of 2048.
* Fixed scale weight norms.
* Updated example workflow.
* Updated pictures.
* Delete your custom folder and clone again.

**Features**:
* ComfyUi lora trainer.
* Adaptation of the musubi-tunner library by kohya-ss. From https://github.com/kohya-ss/musubi-tuner.
* Added train into subprocess.
* Code mods for full compatibility with the last version of ComfyUi.
* Added 6 nodes for training.
* Added Example Workflow in the custom node folder.
* Made for ComfyUi windows portable package.
* Automated process for the creation of the TOM file, cache latents, cache texts & trainning run (Nodes triggered by this order to do the complete process in one shot).
* You can skip latents and text caches if you need to restart the training (taking into account data has not changed vae, clipvision, text models).


**Instructions**:
1. Clone this repository into your custom node folder.
2. install requirements.txt from custom_nodes\ComfyUI_Wan2_1_lora_trainer :
```

..\..\..\python -m pip install -r requirements.txt

```
3. run comfyUi
4. Enjoy training.


Regular run: If you use regular bat you must to bypass compiler an memory settings, enough for 1.3B models. (attention mode in spda, default parameters already configured for inmediate results)
![image](https://github.com/user-attachments/assets/9bd03153-622e-45e9-8bc6-b8697620e8cf)

**Torch settings run** : 
Run 14B are a heavy process so, highly recomended an instalation of torch >=2.7.0 cuda128 and visual studio tools. After this you must create your custom Bat file adding the visual Studio environment.
Example, if you want a bat that use sage attention and also train with musubi compile settings then create it as this:
```
@echo off
REM Load Visual Studio Build Tools for the Wan subprocess environment (Optional to use max pow with the musubi compile settings and memory nodes)
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64
REM Start ComfyUI
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --use-sage-attention --fast fp16_accumulation
pause
```
**NOTE** : The reason of adding this windows call is because the Trainer runs in a new sub process inheriting the ComfyUI environment, but needs its own Visual Studio environment to work.

Then conect the compiler and memory nodes (choose your desired attention mode):
![image](https://github.com/user-attachments/assets/63f8862e-544d-4718-89f1-1c34067e5ee1)

if you don't have any of this modules you can disconnect the musubi compile settings node.

* Image data input are not exclusive to videos! you can train just with images as the following example (path to your images and text captions):
![Captura de pantalla 2025-05-23 161441](https://github.com/user-attachments/assets/465448fe-f347-431f-b3e7-e13436d5c039)

* Path into an empty folder for the cache (use different folders for each lora to not mix you cache data (cleaner and probably faster).

Performances test with 312 images with default settings (spda) :
![image](https://github.com/user-attachments/assets/15222364-f1db-42fa-abf3-0ccc08a953b5)

And the results :
https://github.com/user-attachments/assets/41b439ee-6e90-49ac-83dd-d1ba21fd1d63

For any concern no doubt to contact me.
