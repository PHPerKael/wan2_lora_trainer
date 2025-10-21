# File: musubi-tuner/dataset/config_utils.py
# Version: RECONSTRUCTED_AND_CORRECTED

import argparse
from dataclasses import asdict, dataclass
import functools
import random
from textwrap import dedent, indent
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union # Ensure all are here

import toml
import voluptuous
# Import specific voluptuous components needed
from voluptuous import Any, ExactSequence, MultipleInvalid, Object, Schema, Optional as VolOptional, Required, Coerce, In

# Corrected relative import for image_video_dataset
# This assumes image_video_dataset.py is in the SAME directory as this config_utils.py
# and dataset/ has an __init__.py
from image_video_dataset import DatasetGroup, ImageDataset, VideoDataset, ARCHITECTURE_WAN, ARCHITECTURE_HUNYUAN_VIDEO

import logging
logger = logging.getLogger(__name__)
# Configure logging once, preferably at a higher level (e.g., in your package's __init__.py or when app starts)
# For now, ensure it's configured if this module is run or imported.
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s %(name)s] %(message)s')

# --- Funciones de Validación a Nivel de Módulo (FUERA DE LA CLASE) ---
# These are used by ConfigSanitizer's class-level schema definitions, so they must be defined before ConfigSanitizer
def _static_validate_and_convert_twodim(klass, value: Sequence) -> Tuple:
    Schema(ExactSequence([klass, klass]))(value)
    return tuple(value)

def _static_validate_and_convert_scalar_or_twodim(klass, value: Union[float, Sequence]) -> Tuple:
    Schema(Any(klass, ExactSequence([klass, klass])))(value)
    try:
        Schema(klass)(value) # Try to validate as a single instance of klass
        return (value, value) # If it's a scalar, duplicate it
    except voluptuous.Invalid: # If scalar validation fails, it must be a sequence
        return _static_validate_and_convert_twodim(klass, value)

# --- Dataclasses (Definidas ANTES de ser usadas en Type Hints de otras clases/funciones) ---
@dataclass
class BaseDatasetParams:
    resolution: Tuple[int, int] = (960, 544)
    enable_bucket: bool = False
    bucket_no_upscale: bool = False
    caption_extension: Optional[str] = ".txt" # Original had None, but .txt is common
    batch_size: int = 1
    num_repeats: int = 1
    cache_directory: Optional[str] = None
    debug_dataset: bool = False
    architecture: str = "no_default"

@dataclass
class ImageDatasetParams(BaseDatasetParams):
    image_directory: Optional[str] = None
    image_jsonl_file: Optional[str] = None

@dataclass
class VideoDatasetParams(BaseDatasetParams):
    video_directory: Optional[str] = None
    video_jsonl_file: Optional[str] = None
    control_directory: Optional[str] = None
    target_frames: Sequence[int] = (1,)
    frame_extraction: Optional[str] = "head"
    frame_stride: Optional[int] = 1
    frame_sample: Optional[int] = 1
    max_frames: Optional[int] = 129
    source_fps: Optional[float] = None

@dataclass
class DatasetBlueprint:
    is_image_dataset: bool
    params: Union[ImageDatasetParams, VideoDatasetParams]

@dataclass
class DatasetGroupBlueprint:
    datasets: Sequence[DatasetBlueprint]

@dataclass
class Blueprint:
    dataset_group: DatasetGroupBlueprint

# --- ConfigSanitizer Class ---
class ConfigSanitizer:
    # Schemas defined as CLASS attributes
    DATASET_ASCENDABLE_SCHEMA = {
        VolOptional("caption_extension", default=".txt"): str,
        VolOptional("batch_size", default=1): Coerce(int),
        VolOptional("num_repeats", default=1): Coerce(int),
        VolOptional("resolution", default=(512, 512)): functools.partial(_static_validate_and_convert_scalar_or_twodim, int),
        VolOptional("enable_bucket", default=True): bool,
        VolOptional("bucket_no_upscale", default=False): bool,
    }
    IMAGE_DATASET_DISTINCT_SCHEMA = {
        VolOptional("image_directory"): VolOptional(str),
        VolOptional("image_jsonl_file"): VolOptional(str),
        Required("cache_directory"): str, # Made required as it's crucial for caching nodes
    }
    VIDEO_DATASET_DISTINCT_SCHEMA = {
        VolOptional("video_directory"): VolOptional(str),
        VolOptional("video_jsonl_file"): VolOptional(str),
        VolOptional("control_directory"): VolOptional(str),
        VolOptional("target_frames", default=[1]): [Coerce(int)],
        VolOptional("frame_extraction", default="head"): In(["head", "middle", "tail", "all", "uniform", "uniform_scaled"]),
        VolOptional("frame_stride", default=1): Coerce(int),
        VolOptional("frame_sample", default=1): Coerce(int),
        VolOptional("max_frames", default=129): Coerce(int),
        Required("cache_directory"): str, # Made required
        VolOptional("source_fps"): VolOptional(Coerce(float)),
    }
    ARGPARSE_SPECIFIC_SCHEMA = {
        Required("debug_dataset", default=False): bool,
        VolOptional("dataset_config"): VolOptional(str), 
        VolOptional("vae"): VolOptional(str), VolOptional("vae_dtype"): VolOptional(str),
        VolOptional("device"): VolOptional(str), 
        VolOptional("batch_size", description="CLI batch_size for encoding/processing, not dataset definition"): VolOptional(Coerce(int)),
        VolOptional("num_workers", description="CLI num_workers for encoding/processing"): VolOptional(Coerce(int)), 
        VolOptional("skip_existing", default=False): bool,
        VolOptional("keep_cache", default=False): bool, 
        VolOptional("debug_mode"): VolOptional(str),
        VolOptional("console_width", default=80): Coerce(int), 
        VolOptional("console_back"): VolOptional(str),
        VolOptional("console_num_images"): VolOptional(Coerce(int)), 
        VolOptional("vae_cache_cpu", default=False): bool, # From wan_cache_latents
        VolOptional("clip"): VolOptional(str),            # From wan_cache_latents
        VolOptional("t5"): VolOptional(str),              # From wan_cache_text_encoder
        VolOptional("fp8_t5", default=False): bool,       # From wan_cache_text_encoder
        VolOptional("architecture", default=ARCHITECTURE_WAN): In([ARCHITECTURE_WAN, ARCHITECTURE_HUNYUAN_VIDEO, "no_default", None]),
        VolOptional("output_name", default="default_run_name"): str, # Often useful
        # Add ANY other argparse argument your scripts define that might be used by BlueprintGenerator fallbacks
    }

    @staticmethod
    def _merge_dict(*dict_list: dict) -> dict: # Renamed to avoid name mangling if called externally
        merged = {}
        for schema_part in dict_list:
            merged.update(schema_part)
        return merged

    def __init__(self) -> None:
        # Instance schemas are built from class schemas
        self.image_dataset_schema_inst = ConfigSanitizer._merge_dict( # Use ClassName._merge_dict
            ConfigSanitizer.DATASET_ASCENDABLE_SCHEMA,
            ConfigSanitizer.IMAGE_DATASET_DISTINCT_SCHEMA,
        )
        self.video_dataset_schema_inst = ConfigSanitizer._merge_dict(
            ConfigSanitizer.DATASET_ASCENDABLE_SCHEMA,
            ConfigSanitizer.VIDEO_DATASET_DISTINCT_SCHEMA,
        )
    
        def validate_flex_dataset(dataset_config: dict):
            if dataset_config.get("video_directory") or dataset_config.get("video_jsonl_file"):
                return Schema(self.video_dataset_schema_inst)(dataset_config)
            else:
                return Schema(self.image_dataset_schema_inst)(dataset_config)
    
        self.dataset_schema_func = validate_flex_dataset # This is a callable
    
        self.general_schema_inst = ConfigSanitizer._merge_dict(ConfigSanitizer.DATASET_ASCENDABLE_SCHEMA)
        
        self.user_config_validator = Schema({
                VolOptional("general", default={}): self.general_schema_inst, 
                Required("datasets"): [self.dataset_schema_func], # Use the callable here
            }
        )
        
        # Validator for the argparse namespace, using the class-level schema
        self.argparse_config_validator = Schema(ConfigSanitizer.ARGPARSE_SPECIFIC_SCHEMA, extra=voluptuous.ALLOW_EXTRA)
        logger.debug(f"[ConfigSanitizer __init__] Initialized.")

    def sanitize_user_config(self, user_config: dict) -> dict:
        try:
            return self.user_config_validator(user_config)
        except MultipleInvalid as e:
            logger.error(f"Invalid user config (sanitize_user_config): {e}")
            # You might want to print e.path and e.msg for more details
            raise

    def sanitize_argparse_namespace(self, argparse_namespace: Union[argparse.Namespace, object]) -> argparse.Namespace:
        try:
            # Ensure we have a dict to validate
            data_to_validate = vars(argparse_namespace) if hasattr(argparse_namespace, '__dict__') else dict(argparse_namespace)
            # logger.debug(f"[ConfigSanitizer] Validating argparse data: {data_to_validate} against schema {ConfigSanitizer.ARGPARSE_SPECIFIC_SCHEMA}")
            validated_data_dict = self.argparse_config_validator(data_to_validate)
            # logger.debug(f"[ConfigSanitizer] Argparse data validated: {validated_data_dict}")
            # Reconstruct a Namespace or a simple object that behaves like one
            # Using argparse.Namespace ensures it has the expected behaviors (e.g., getattr default to None)
            return argparse.Namespace(**validated_data_dict)
        except MultipleInvalid as e:
            logger.error(f"Invalid argparse namespace (sanitize_argparse_namespace). Error: {e}")
            # logger.error(f"Data that failed validation: {vars(argparse_namespace) if hasattr(argparse_namespace, '__dict__') else dict(argparse_namespace)}")
            raise
        except Exception as e_other: # Catch any other unexpected errors
            logger.error(f"Unexpected error in sanitize_argparse_namespace: {type(e_other).__name__}: {e_other}")
            raise

# --- BlueprintGenerator Class ---
class BlueprintGenerator:
    BLUEPRINT_PARAM_NAME_TO_CONFIG_OPTNAME = {} # You might populate this if needed

    def __init__(self, sanitizer: ConfigSanitizer):
        self.sanitizer = sanitizer

    def generate(self, user_config: dict, argparse_namespace: argparse.Namespace, **runtime_params) -> 'Blueprint': # Forward ref
        sanitized_user_config = self.sanitizer.sanitize_user_config(user_config)
        # The argparse_namespace here IS the one from ComfyUI node, already an ArgsNamespace object
        sanitized_argparse_namespace = self.sanitizer.sanitize_argparse_namespace(argparse_namespace)
        
        # argparse_config should contain all fields from sanitized_argparse_namespace that are not None
        # or are boolean (even if False)
        argparse_config = {
            k: v for k, v in vars(sanitized_argparse_namespace).items() 
            if v is not None or isinstance(v, bool) # Keep booleans even if False
        }
        
        general_config = sanitized_user_config.get("general", {})
        # Ensure 'architecture' is available for generate_params_by_fallbacks
        # It will search in dataset_config_entry, general_config, argparse_config, runtime_params
        if 'architecture' not in argparse_config and 'architecture' in runtime_params:
            argparse_config['architecture'] = runtime_params['architecture']
        # If still not found, it will default to BaseDatasetParams.architecture ("no_default")

        dataset_blueprints = []
        for dataset_config_entry in sanitized_user_config.get("datasets", []):
            is_image_dataset = dataset_config_entry.get("image_directory") or dataset_config_entry.get("image_jsonl_file")
            dataset_params_klass = ImageDatasetParams if is_image_dataset else VideoDatasetParams
            
            # The fallbacks list is crucial: specific dataset entry, then general, then argparse, then runtime
            params = self.generate_params_by_fallbacks(
                dataset_params_klass, [dataset_config_entry, general_config, argparse_config, runtime_params]
            )
            dataset_blueprints.append(DatasetBlueprint(is_image_dataset, params))
        
        dataset_group_blueprint = DatasetGroupBlueprint(dataset_blueprints)
        return Blueprint(dataset_group_blueprint)

    @staticmethod
    def generate_params_by_fallbacks(param_klass, fallbacks: Sequence[dict]):
        name_map = BlueprintGenerator.BLUEPRINT_PARAM_NAME_TO_CONFIG_OPTNAME
        search_value = BlueprintGenerator.search_value
        # Get default values from the dataclass itself
        default_params_instance = param_klass()
        default_params_dict = asdict(default_params_instance)
        param_names = default_params_dict.keys()

        params = {}
        for name in param_names:
            config_opt_name = name_map.get(name, name) # Use mapped name if exists, else original
            default_for_this_param = default_params_dict.get(name)
            params[name] = search_value(config_opt_name, fallbacks, default_for_this_param)
        
        return param_klass(**params)

    @staticmethod
    def search_value(key: str, fallbacks: Sequence[dict], default_value=None):
        for cand_dict in fallbacks:
            if key in cand_dict: # Check if key exists in the current fallback dictionary
                value = cand_dict[key]
                if value is not None:
                    return value
                if isinstance(value, bool): # Explicitly allow False to be a valid override
                    return value
        return default_value # If not found in any fallback, use the original default

# --- Helper Functions for Datasets ---
def generate_dataset_group_by_blueprint(dataset_group_blueprint: 'DatasetGroupBlueprint', training: bool = False) -> 'DatasetGroup':
    datasets: List[Union[ImageDataset, VideoDataset]] = []
    # seed = random.randint(0, 2**31) # Moved seed setting inside the loop for per-dataset seed if BaseDataset handles it.
                                     # Or keep it here if all datasets in the group must share the exact same random sequence start.
                                     # Your original code had it outside, implying shared seed for initial shuffling/bucketing.

    for i_ds, dataset_blueprint_entry in enumerate(dataset_group_blueprint.datasets):
        dataset_klass = ImageDataset if dataset_blueprint_entry.is_image_dataset else VideoDataset
        
        params_dict = asdict(dataset_blueprint_entry.params)
        # logger.debug(f"Instantiating dataset {i_ds} of type {dataset_klass.__name__} with params: {params_dict}")
        try:
            dataset = dataset_klass(**params_dict)
        except TypeError as te:
            logger.error(f"TypeError creating dataset {dataset_klass.__name__} with params {params_dict}: {te}")
            raise
        datasets.append(dataset)

    # Assertion for unique cache_directories (only if cache_directory is not None)
    # cache_directories = [ds.cache_directory for ds in datasets if ds.cache_directory is not None]
    # if len(cache_directories) != len(set(cache_directories)):
    #     logger.warning("Multiple datasets share the same cache_directory. This might be intentional or an error.")
        # raise ValueError("cache directory should be unique for each dataset if specified")

    # Log dataset info
    info = ""
    for i, dataset in enumerate(datasets): # Iterate over the created dataset instances
        is_image_dataset = isinstance(dataset, ImageDataset)
        info += dedent(f"""\
[Dataset {i}] ({type(dataset).__name__})
  is_image_dataset: {is_image_dataset}
  resolution: {dataset.resolution} | batch_size: {dataset.batch_size} | num_repeats: {dataset.num_repeats}
  caption_extension: "{dataset.caption_extension}"
  enable_bucket: {dataset.enable_bucket} | bucket_no_upscale: {dataset.bucket_no_upscale}
  cache_directory: "{dataset.cache_directory}"
  debug_dataset: {dataset.debug_dataset}
  architecture: {dataset.architecture}""")
        if is_image_dataset:
            info += indent(dedent(f"""\
  image_directory: "{dataset.image_directory}"
  image_jsonl_file: "{dataset.image_jsonl_file}"\n"""), "  ")
        else: # VideoDataset
            info += indent(dedent(f"""\
  video_directory: "{dataset.video_directory}"
  video_jsonl_file: "{dataset.video_jsonl_file}"
  control_directory: "{dataset.control_directory}"
  target_frames: {dataset.target_frames} | frame_extraction: "{dataset.frame_extraction}"
  frame_stride: {dataset.frame_stride} | frame_sample: {dataset.frame_sample}
  max_frames: {dataset.max_frames} | source_fps: {dataset.source_fps}\n"""), "  ")
    if info: logger.info(f"Generated Dataset Group Info:\n{info}")

    # Set seed and prepare for training after all datasets are instantiated
    # This ensures that if bucketing depends on other datasets in the group, it's done with final objects
    # However, your original code set seed *before* prepare_for_training.
    group_seed = random.randint(0, 2**31) 
    for dataset in datasets:
        dataset.set_seed(group_seed) # Pass the same group_seed to each
        if training:
            dataset.prepare_for_training()

    return DatasetGroup(datasets)

def load_user_config(file: str) -> dict:
    file_path: Path = Path(file)
    if not file_path.is_file():
        raise ValueError(f"Config file not found: {file_path}")
    
    # logger.debug(f"Loading user config from: {file_path}")
    if file_path.name.lower().endswith(".json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e_json:
            logger.error(f"Error parsing JSON config file {file_path}: {e_json}")
            raise
        except Exception as e: # Catch other potential errors like file IO
            logger.error(f"Unexpected error loading JSON config file {file_path}: {e}")
            raise
    elif file_path.name.lower().endswith(".toml"):
        try:
            config = toml.load(file_path)
        except toml.TomlDecodeError as e_toml:
            logger.error(f"Error parsing TOML config file {file_path}: {e_toml}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading TOML config file {file_path}: {e}")
            raise
    else:
        raise ValueError(f"Unsupported config file format: {file_path}. Must be .json or .toml.")
    return config

# Remove or comment out the if __name__ == "__main__": block for module usage
# if __name__ == "__main__":
#     # ... (your test code) ...
#     pass