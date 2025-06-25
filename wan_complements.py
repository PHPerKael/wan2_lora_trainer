# File: ComfyUI/custom_nodes/musubi-tuner/wan_complements.py
# Version: 1.0 (Initial Musubi Compile Settings node)

import os
import comfy.utils
import folder_paths
import time
import shutil
from .musubi_utils import models_combo, vaes_combo, encoders_combo, clip_vision_files

# Nota: Para este nodo específico, no necesitamos importar argparse, toml, etc.,
# ya que solo estamos recolectando los argumentos en un diccionario.
# Estos serán pasados al WanLoRATrainer.

class MusubiCompileSettings:
    NODE_NAME = "MusubiCompileSettings"
    IS_OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(s):
        # Identificamos los argumentos relacionados con la compilación y optimización
        # de la lista de argumentos de `run_wan_training.py` proporcionada.
        return {
            "required": {
                "fp8_base": ("BOOLEAN", {"default": False, "tooltip": "Enable FP8 base training. Requires compatible hardware."}),
                "fp8_scaled": ("BOOLEAN", {"default": False, "tooltip": "Enable FP8 scaled training (e.g., for UNet/DiT). Requires compatible hardware."}),
                "dynamo_backend": (["NO", "EAGER", "AOT_EAGER", "INDUCTOR", "AOT_TS_NVFUSER", "NVPRIMS_NVFUSER", "CUDAGRAPHS", "OFI", "FX2TRT", "ONNXRT", "TENSORRT", "AOT_TORCHXLA_TRACE_ONCE", "TORCHXLA_TRACE_ONCE", "IPEX", "TVM", "HPU_BACKEND"], {"default": "NO", "tooltip": "TorchDynamo backend to use for compilation."}),
                "dynamo_mode": (["default", "reduce-overhead", "max-autotune"], {"default": "default", "tooltip": "TorchDynamo mode for performance tuning."}),
                "dynamo_fullgraph": ("BOOLEAN", {"default": False, "tooltip": "Forces TorchDynamo to capture the entire graph (disables graph breaks)."}),
                "dynamo_dynamic": ("BOOLEAN", {"default": False, "tooltip": "Enables dynamic shapes for TorchDynamo."}),
            },
            # Podemos añadir inputs opcionales si surge la necesidad, pero por ahora todos son "required"
            # y se gestionan sus valores por defecto.
        }

    RETURN_TYPES = ("DICT",) # Devolverá un diccionario con los ajustes de compilación
    RETURN_NAMES = ("compile_settings",)
    FUNCTION = "get_compile_settings"
    CATEGORY = "musubi-tuner/wan/settings" # Nueva categoría para agrupar ajustes

    def get_compile_settings(self, fp8_base, fp8_scaled, dynamo_backend, dynamo_mode, dynamo_fullgraph, dynamo_dynamic):
        node_name_print = f"[MusubiTuner {self.NODE_NAME}]"
        print(f"{node_name_print} Generating compile settings.")

        settings = {
            "fp8_base": fp8_base,
            "fp8_scaled": fp8_scaled,
            "dynamo_fullgraph": dynamo_fullgraph,
            "dynamo_dynamic": dynamo_dynamic,
        }

        # Manejar los combos que pueden significar "desactivado" o "por defecto"
        if dynamo_backend != "NO":
            settings["dynamo_backend"] = dynamo_backend
        # else: Si es "NO", no lo añadimos al diccionario para que el parser lo ignore.

        if dynamo_mode != "default":
            settings["dynamo_mode"] = dynamo_mode
        # else: Si es "default", no lo añadimos al diccionario.

        # Filtra los booleanos False para que no se pasen explícitamente si el script espera ausencia de flag.
        # Por ejemplo, si `--fp8_base` es un flag `store_true`, pasar `--fp8_base False` es un error.
        # Es mejor omitir el flag por completo si el valor es False.
        final_settings = {k: v for k, v in settings.items() if not (isinstance(v, bool) and v is False)}
        
        print(f"{node_name_print} Generated settings: {final_settings}")
        return (final_settings,)

class MusubiMemorySettings: # Nuevo nodo
    NODE_NAME = "MusubiMemorySettings"
    IS_OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(s):
        # blocks_to_swap: suele ser un número de bloques (INT), 0 o -1 para deshabilitar
        # img_in_txt_in_offloading: un flag booleano
        return {
            "required": {
                "blocks_to_swap": ("INT", {"default": 0, "min": 0, "max": 100, "tooltip": "Number of model blocks to offload to CPU/disk to save VRAM (0 to disable). Larger values save more VRAM but increase training time. 1.3B models max use is 30, 14B max use is 40"}),
                "img_in_txt_in_offloading": ("BOOLEAN", {"default": False, "tooltip": "Enable offloading of image/text embeding it to RAM memory to save GPU memory."}),
            }
        }

    RETURN_TYPES = ("DICT",) # Devolverá un diccionario con los ajustes de memoria
    RETURN_NAMES = ("memory_settings",)
    FUNCTION = "get_memory_settings"
    CATEGORY = "musubi-tuner/wan/settings" # Misma categoría que Compile Settings

    def get_memory_settings(self, blocks_to_swap, img_in_txt_in_offloading):
        node_name_print = f"[MusubiTuner {self.NODE_NAME}]"
        print(f"{node_name_print} Generating memory settings.")

        settings = {
            "blocks_to_swap": blocks_to_swap,
            "img_in_txt_in_offloading": img_in_txt_in_offloading,
        }

        # Similar a compile settings, filtramos los booleanos False y valores que significan "desactivado"
        final_settings = {}
        for k, v in settings.items():
            if isinstance(v, bool):
                if v: # Solo añadir si es True (para flags store_true)
                    final_settings[k] = v
            elif k == "blocks_to_swap":
                if v > 0: # Solo añadir blocks_to_swap si es mayor que 0 (significa que hay algo que swappear)
                    final_settings[k] = v
            else: # Otros tipos de argumentos se añaden directamente
                final_settings[k] = v
        
        print(f"{node_name_print} Generated settings: {final_settings}")
        return (final_settings,)

class MusubiSamplingSettings:
    NODE_NAME = "MusubiSamplingSettings"
    IS_OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(s):
        # Reutilizamos las listas de modelos que ya se cargan al inicio del script principal
        # Si este archivo no las tiene, tendrás que copiar el código que escanea las carpetas
        # pero por lo que veo en tu script, 'vaes_combo', 'encoders_combo' son globales.
        # Si no lo fueran, tendrías que pasar 'self' en el método o recargarlos aquí.
        # Asumimos que están disponibles.
        clip_vision_files = ["None"] + folder_paths.get_filename_list("clip_vision")

        return {
            "required": {
                # Parámetros para controlar la frecuencia del sampleo
                "sample_every_n_steps": ("INT", {"default": 0, "min": 0, "step": 50, "tooltip": "Generate a sample every n steps."}),
                "sample_every_n_epochs": ("INT", {"default": 0, "min": 0, "step": 1, "tooltip": "Generate a sample every n epoch."}),
                "sample_at_first": ("BOOLEAN", {"default": True, "tooltip": "Genera a sample at the starting training."}),
                
                # Modelos necesarios para el sampleo. El usuario debe seleccionarlos aquí.
                "vae_name": (vaes_combo, {"tooltip": "The same vae used to caching"}),
                "t5_name": (encoders_combo, {"tooltip": "The same T5 used to caching"}),
                "clip_name": (clip_vision_files, {"default": "None", "tooltip": "If I2V, the same clip vision used for caching"}),

                # El "truco" que pediste: un bloque de texto en lugar de un archivo.
                "prompts_text": ("STRING", {
                    "multiline": True,
                    "default": 'a beautiful sunset over mountains',
                    "tooltip": "Write a prompt. You can specify width and height by using --w --h. Example : a cat making surf --w 832 --h 480"
                }),
            }
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("sampling_settings",)
    FUNCTION = "get_sampling_settings"
    CATEGORY = "musubi-tuner/wan/settings"

    def get_sampling_settings(self, sample_every_n_steps, sample_every_n_epochs, sample_at_first, vae_name, t5_name, clip_name, prompts_text):
        node_name_print = f"[MusubiTuner {self.NODE_NAME}]"
        print(f"{node_name_print} Generating sampling settings.")

        settings = {}

        # 1. Comprobar si el usuario realmente quiere generar muestras.
        # Si el texto de los prompts está vacío, no hacemos nada.
        if not prompts_text or not prompts_text.strip():
            print(f"{node_name_print} No prompts provided. Skipping sample generation setup.")
            return ({},) # Devolvemos un diccionario vacío.

        # 2. Crear el archivo de prompts temporal a partir del texto del nodo.
        try:
            # Usamos la carpeta 'temp' de ComfyUI, que es un buen lugar para archivos temporales.
            temp_dir = folder_paths.get_temp_directory()
            # Creamos una subcarpeta para mantenerlo organizado.
            prompts_dir = os.path.join(temp_dir, "musubi_tuner_prompts")
            os.makedirs(prompts_dir, exist_ok=True)

            # Creamos un nombre de archivo único usando la fecha y hora.
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            prompt_filename = f"prompts_{timestamp}.txt"
            prompt_filepath = os.path.join(prompts_dir, prompt_filename)

            # Escribimos el contenido del input de texto al archivo.
            with open(prompt_filepath, "w", encoding="utf-8") as f:
                f.write(prompts_text)
            
            print(f"{node_name_print} Successfully created temporary prompt file at: {prompt_filepath}")
            
            # Añadimos la ruta del archivo a los ajustes que pasaremos al trainer.
            settings["sample_prompts"] = prompt_filepath

        except Exception as e:
            print(f"{node_name_print} ERROR creating temporary prompt file: {e}")
            traceback.print_exc()
            return ({},) # Devolvemos un diccionario vacío en caso de error.

        # 3. Añadir el resto de parámetros al diccionario de ajustes.
        settings["sample_every_n_steps"] = sample_every_n_steps
        settings["sample_every_n_epochs"] = sample_every_n_epochs
        settings["sample_at_first"] = sample_at_first
        

        # 4. Obtener las rutas completas de los modelos y añadirlas.
        # El script de entrenamiento necesita las rutas absolutas, no solo los nombres.
        if vae_name:
            settings["vae"] = folder_paths.get_full_path("vae", vae_name)
        if t5_name:
            settings["t5"] = folder_paths.get_full_path("text_encoders", t5_name)
        
        # Manejar el CLIP model, que es opcional.
        if clip_name and clip_name != "None":
            settings["clip"] = folder_paths.get_full_path("clip_vision", clip_name)
        
        print(f"{node_name_print} Generated sampling settings: {settings}")
        return (settings,)

# Mapeos para ComfyUI - ¡ASEGÚRATE DE QUE ESTA SECCIÓN ESTÉ AL FINAL DEL ARCHIVO!
# Combina los mapeos de ambas clases
NODE_CLASS_MAPPINGS = {
    "MusubiCompileSettings": MusubiCompileSettings,
    "MusubiMemorySettings": MusubiMemorySettings, 
    "MusubiSamplingSettings": MusubiSamplingSettings,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "MusubiCompileSettings": "Musubi Compile Settings (Wan)",
    "MusubiMemorySettings": "Musubi Memory Settings (Wan)", # Nuevo mapeo
    "MusubiSamplingSettings": "Musubi Sampling Settings (Wan)",
}
#print("[MusubiTuner Nodes] wan_complements.py loaded. Mappings defined.")