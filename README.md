![ComfyUI_00026_](https://github.com/user-attachments/assets/57fdbf91-51d5-43ad-9ec7-3873003dca1b)

<div align="center"><h1>ComfyUI MUSUBI-TUNNER WAN LORA TRAINER</h1></div>


Important note: The sprites used for the training tests are property of real artirsts (under copyright), so this is not only a copy of the world, it can be a tool for artists too.

✅ LORA STRENGTH FIXED!.

Tested and working with this package:
* ComfyUI 0.3.39
* Python 3.12.10
* Torch 2.7.0 cuda 128

**Strongly recomended to use the Regular run to ensure your Lora using SPDA attention (Without Compiler and memory nodes). Why? see the next point below** :
* Using SPDA Is the only one making a valid Lora for the moment...Testing sage just make the Lora generate noise, so i need to make more testing to see if there is an issue or is just an incompatibility with Sage or number of processes. I will update with any news.
* Regular run: If you use regular bat you must to bypass compiler an memory settings, enough for 1.3B models. (attention mode in spda, default parameters already configured for inmediate results)
![image](https://github.com/user-attachments/assets/9bd03153-622e-45e9-8bc6-b8697620e8cf)


**Update version 1.02**:
* Setted up max_train_epochs to 512.

**Update version 1.01**:
* Fixed as default the learning parameters (A good starting point to see quickly results just loading the nodes/workflow).
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
* For more info about setting up correctly parameters you can check the Wan Doc on https://github.com/kohya-ss/musubi-tuner/blob/main/docs/wan.md


* avr_loss in last update looking great (128 epochs, 30 images + 5000 steps, network dropout 0.2, other settings as home):
* ![image](https://github.com/user-attachments/assets/17211bb0-ae8d-42b6-a4c1-3610500a62f2)
* Deconstructed character in pieces:
* ![image](https://github.com/user-attachments/assets/25a5b432-3c5a-4f25-9d5a-6e1a824c7570)
* Result (text to video generation):
![image](https://github.com/user-attachments/assets/dc8d425e-09d7-4e67-985f-cf0bcf782872)

Also playing with image sequences :
![image](https://github.com/user-attachments/assets/13480d51-e221-48b5-9eed-f2133b92eabc)


Result with 0.5 of strenght:

![image](https://github.com/user-attachments/assets/65a94dfe-dcce-4b1d-acea-faac8191109c)






**About max_train_epochs**: The max train epochs is an equations that takes into account several arguments as gradients, number of images etc. This must be set up between 16/512 depending of the number of images you want to train. To ensure a little package of 30 images, set up it as 128 to train more than 5000 steps. Take into account network dropout to not overfitting, also dim and alpha. All is relative but for sure you will find you custom setting depending of your purpose. For the moment max train epochs have a limit to 512, but if is needed to add a bigger max value i can update it.


**Instructions**:
1. Clone this repository into your custom node folder.
2. install requirements.txt from custom_nodes\ComfyUI_Wan2_1_lora_trainer :
```

..\..\..\python -m pip install -r requirements.txt

```
3. run comfyUi
4. Enjoy training.


**In case ComfyUI does not detect CL from visual studio or use Torch** : 
If you want to use torch (not tested and not sure if this kind of compiling can work for training) or your instalation does not detect the CL tools from visual studio. You can create a custom bat adding a call pointing to your build tool
Example:
```
@echo off
REM Load Visual Studio Build Tools for the Wan subprocess environment (Optional to use max pow with the musubi compile settings and memory nodes)
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64
REM Start ComfyUI
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build 
pause
```
**NOTE** : The reason of adding this windows call is because the Trainer runs in a new sub process inheriting the ComfyUI environment, but needs its own Visual Studio environment to work.

**CLIP VISION** : Clip vision is just setted up for I2V models, for training T2V Models, set clip to None. 

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
