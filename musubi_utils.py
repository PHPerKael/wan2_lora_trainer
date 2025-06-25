import os
import folder_paths

def get_model_files(folder_name, extensions):
    try:
        folders = folder_paths.get_folder_paths(folder_name)
        all_files = []
        for folder in folders:
            if os.path.isdir(folder):
                for item_name in os.listdir(folder):
                    if os.path.isfile(os.path.join(folder, item_name)) and any(item_name.lower().endswith(ext) for ext in extensions):
                        all_files.append(item_name)
        return sorted(list(set(all_files)))
    except Exception as e:
        print(f"[MusubiTuner Utils] ERROR escaneando '{folder_name}': {e}")
        return []

MODEL_EXTENSIONS = ['.pth', '.safetensors']

models_combo = [""] + get_model_files("diffusion_models", MODEL_EXTENSIONS)
vaes_combo = [""] + get_model_files("vae", MODEL_EXTENSIONS)
encoders_combo = [""] + get_model_files("text_encoders", MODEL_EXTENSIONS)
try:
    clip_vision_files = ["None"] + folder_paths.get_filename_list("clip_vision")
except:
    clip_vision_files = ["None"]