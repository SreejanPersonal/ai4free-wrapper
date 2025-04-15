import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# --- Firebase and Supabase Configuration ---
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

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

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 60,
        'pool_recycle': 3600
    }

    # Get Redis configuration
    REDIS_URL = os.getenv('REDIS_URL')
    
    # If REDIS_URL not provided, construct it from components
    if not REDIS_URL:
        REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
        REDIS_USERNAME = os.getenv('REDIS_USERNAME', '')
        
        # For Upstash, ensure proper URL format
        if 'upstash.io' in REDIS_HOST or '1Panel' in REDIS_HOST or '1panel' in REDIS_HOST:
            REDIS_URL = f"rediss://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
        else:
            # Local Redis URL format
            REDIS_URL = (
                f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
                if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
            )

    REQUEST_LIMIT = 10
    RATE_LIMIT_WINDOW = 60

    IMAGE_REQUEST_LIMIT = 50
    IMAGE_RATE_LIMIT_WINDOW = 60

    API_KEY_PREFIX = 'ddc-beta-'
    API_KEY_LENGTH = 54
    
    # API key generation configuration
    API_KEY_PREFIX_LENGTH = 10
    RANDOM_VALUE_LENGTH = API_KEY_LENGTH - API_KEY_PREFIX_LENGTH - len(API_KEY_PREFIX)
    
    # Firebase and Supabase configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = FIREBASE_SERVICE_ACCOUNT_PATH
    SUPABASE_URL = SUPABASE_URL
    SUPABASE_KEY = SUPABASE_KEY

    SYSTEM_SECRET = os.environ.get('SYSTEM_SECRET')

    MAX_INPUT_TOKENS = 4000
    MAX_OUTPUT_TOKENS = 4000

    MODEL_SPECIFIC_CONFIG = {
        "Provider-1/DeepSeek-R1": {"max_input_tokens": 32768, "max_output_tokens": 8192},

        "Provider-2/gpt-4o": {"max_input_tokens": 8192, "max_output_tokens": 4096},

        "Provider-3/DeepSeek-R1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-3/o3-mini": {"max_input_tokens": 16384, "max_output_tokens": 4096},
        "Provider-3/gpt-4.1-mini": {"max_input_tokens": 32768, "max_output_tokens": 8192},

        "Provider-4/DeepSeek-R1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-4/DeepSeek-R1-Distill-Llama-70B": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-4/DeepSeekV3": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        
        "Provider-5/gpt-4o-mini": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/gpt-4o": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/o1-mini": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/qwen-2.5-coder-32b": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/llama-3.3-70b": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/deepseek-v3": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-5/claude-3.7-sonnet": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/deepseek-r1-distill-qwen-32b": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-5/deepseek-r1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-5/deepseek-r1-llama-70b": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-5/gemini-2.0-flash": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/gemini-2.0-flash-thinking": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-5/gpt-4o-audio-preview": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        
        "Provider-6/flux-schnell": {"max_input_tokens": 1000, "max_output_tokens": 1000},
        "Provider-6/flux-dev": {"max_input_tokens": 1000, "max_output_tokens": 1000},
        "Provider-6/sana-6b": {"max_input_tokens": 1000, "max_output_tokens": 1000},
        
        "Provider-7/gpt-4o": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/gemini-2.0-flash": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/gpt-4o-mini": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/grok-2": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/command-a": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/claude-3.5-sonnet": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/claude-3.5-sonnet-v2": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/claude-3.7-sonnet": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/gpt-4.5-preview": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/gpt-4.5": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/o1": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/chatgpt-4o-latest": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/sonar-pro": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/grok-3": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/gpt-4o-mini-search-preview": {"max_input_tokens": 8192, "max_output_tokens": 4096},
        "Provider-7/deepseek-r1": {"max_input_tokens": 32768, "max_output_tokens": 8192},
        "Provider-7/deepseek-v3": {"max_input_tokens": 32768, "max_output_tokens": 8192},

        # Provider 8 Models (Using default limits as placeholders)
        "Provider-8/llama-4-maverick:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/llama-4-maverick": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/llama-4-scout:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/llama-4-scout": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gemini-2.5-pro-preview-03-25": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/quasar-alpha": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/deepseek-v3-base:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/deepseek-chat-v3-0324:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/deepseek-chat-v3-0324": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o1-pro": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/command-a": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o-mini-search-preview": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o-search-preview": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/sonar-reasoning-pro": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/sonar-reasoning": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/sonar-pro": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4.5-preview": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gemini-2.0-flash-lite-001": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.7-sonnet": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.7-sonnet:thinking": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.7-sonnet:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o3-mini-high": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gemini-2.0-flash-001": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gemini-2.0-pro-exp-02-05:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o3-mini": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gemini-2.0-flash-thinking-exp:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/deepseek-r1:free": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/deepseek-r1": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/grok-2-vision-1212": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/grok-2-1212": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-haiku:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-haiku": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-haiku-20241022:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-haiku-20241022": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-sonnet:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-sonnet": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o1-preview": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o1-preview-2024-09-12": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o1-mini": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/o1-mini-2024-09-12": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/chatgpt-4o-latest": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o-2024-08-06": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o-mini": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o-mini-2024-07-18": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-sonnet-20240620:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3.5-sonnet-20240620": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gemini-flash-1.5": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o:extended": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/gpt-4o-2024-05-13": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3-haiku:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3-haiku": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3-opus:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3-opus": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3-sonnet:beta": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-8/claude-3-sonnet": {"max_input_tokens": 4000, "max_output_tokens": 4000},
        "Provider-9/gpt-4.1": {"max_input_tokens": 32768, "max_output_tokens": 4096},
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
