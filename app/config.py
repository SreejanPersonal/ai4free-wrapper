import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# --- Neon Defaults ---
NEON_POSTGRES_URI = os.getenv("NEON_POSTGRES_URI")

parsed_uri = urlparse(NEON_POSTGRES_URI)
neon_host = parsed_uri.hostname
neon_port = parsed_uri.port or 5432
neon_user = parsed_uri.username
neon_password = parsed_uri.password
neon_db = parsed_uri.path.lstrip("/")

# --- Local Overrides ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", neon_host)
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", neon_port))
POSTGRES_USER = os.getenv("POSTGRES_USER", neon_user)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", neon_password)
POSTGRES_DB = os.getenv("POSTGRES_DB", neon_db)

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

class Config:
    """
    Configuration class for the Flask application.
    """
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'a-very-secret-key')
    DEBUG = bool(os.environ.get('FLASK_DEBUG', False))

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_URL = (
        f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
        if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    )

    REQUEST_LIMIT = 10
    RATE_LIMIT_WINDOW = 60

    API_KEY_PREFIX = 'ddc-'
    API_KEY_LENGTH = 50

    SYSTEM_SECRET = os.environ.get('SYSTEM_SECRET')

    # Default tokens are still here, but the model‐specific configuration for Provider4 is keyed by alias.
    MAX_INPUT_TOKENS = 4000
    MAX_OUTPUT_TOKENS = 4000

    MODEL_SPECIFIC_CONFIG = {
        "Provider-1/DeepSeek-R1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-2/gpt-4o": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-3/DeepSeek-R1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-3/o3-mini": {"max_input_tokens": 16384, "max_output_tokens": 4096},
        "Provider-4/DeepSeek-R1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-4/DeepSeek-R1-Distill-Llama-70B": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-4/DeepSeekV3": {"max_input_tokens": 32768, "max_output_tokens": 8192},
    }

    @classmethod
    def get_model_config(cls, model_id):
        return cls.MODEL_SPECIFIC_CONFIG.get(model_id, {
            "max_input_tokens": cls.MAX_INPUT_TOKENS,
            "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
        })

    MODEL_LIST_PATH = 'data/models.json'
    TOKEN_ENCODING = 'cl100k_base'
    ALLOWED_MODELS = []

    @classmethod
    def load_models(cls):
        try:
            with open(cls.MODEL_LIST_PATH, 'r') as f:
                models_data = json.load(f)
                if 'data' in models_data and isinstance(models_data['data'], list):
                    cls.ALLOWED_MODELS = models_data['data']
                else:
                    print("Warning: 'data' key not found or not a list in models.json")
                    cls.ALLOWED_MODELS = []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading models from {cls.MODEL_LIST_PATH}: {e}")
            cls.ALLOWED_MODELS = []

    DISABLE_AUTO_DB_INIT = False

Config.load_models()