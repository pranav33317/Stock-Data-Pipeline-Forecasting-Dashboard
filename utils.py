"""Utility helpers for the pipeline."""
import pandas as pd, os, yaml
def load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(cfg_path) as f:
        return yaml.safe_load(f)
