# Importar los mapeos de nodos del archivo wan_trainer_nodes.py
# Usamos alias para evitar conflictos de nombres si ambos archivos tuvieran las mismas variables
from wan_trainer_nodes import NODE_CLASS_MAPPINGS as TRAINER_NODE_CLASS_MAPPINGS, \
                               NODE_DISPLAY_NAME_MAPPINGS as TRAINER_NODE_DISPLAY_NAME_MAPPINGS

# Importar los mapeos de nodos del nuevo archivo wan_complements.py
from wan_complements import NODE_CLASS_MAPPINGS as COMPLEMENTS_NODE_CLASS_MAPPINGS, \
                               NODE_DISPLAY_NAME_MAPPINGS as COMPLEMENTS_NODE_DISPLAY_NAME_MAPPINGS

# Combinar los diccionarios de mapeo de clases de nodos
NODE_CLASS_MAPPINGS = {**TRAINER_NODE_CLASS_MAPPINGS, **COMPLEMENTS_NODE_CLASS_MAPPINGS}

# Combinar los diccionarios de mapeo de nombres de visualizaci�n de nodos
NODE_DISPLAY_NAME_MAPPINGS = {**TRAINER_NODE_DISPLAY_NAME_MAPPINGS, **COMPLEMENTS_NODE_DISPLAY_NAME_MAPPINGS}

# Exportar las variables combinadas para que ComfyUI las descubra
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
MAGENTA = "\033[35m"
RESET = "\033[0m"
print(f"{MAGENTA}\033[4mMusubiTuner] WAN 2.1 LORA TRAINER.{RESET}") # Magenta y subrayado
