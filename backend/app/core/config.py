import os
import certifi
from dotenv import load_dotenv

# automatic fix for SSL certificate verification issues
ssl_cert_file = os.environ.get("SSL_CERT_FILE")
if ssl_cert_file and not os.path.exists(ssl_cert_file):
    os.environ["SSL_CERT_FILE"] = certifi.where()
elif not ssl_cert_file:
    os.environ["SSL_CERT_FILE"] = certifi.where()    


load_dotenv()  # Load environment variables from .env file
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = ''
    tavily_api_key: str = ''
    pinecone_api_key: str = ''
    
    # Pinecone Configuration
    pinecone_environment: str = 'us-east1-gcp'
    pinecone_index_name: str = 'medical-agent-index' # Changed from generic 'groqai'
    
    # Groq LLM Configuration (Using real, fast Groq models)
    groq_model_name: str = 'llama-3.3-70b-versatile'
    groq_chat_model_name: str = 'llama-3.3-70b-versatile'
    groq_chat_model_temperature: float = 0.7
    groq_chat_model_max_tokens: int = 1000
    
    # Embedding Model (Groq doesn't do embeddings; typically handled via HuggingFace or OpenAI)
    groq_embedding_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    groq_embedding_model_dimensions: int = 384  # Matches all-MiniLM-L6-v2 (change to 1536 if using OpenAI text-embedding-3-small)
    
    # Vision Model (Optional, using a valid Groq vision-supported model)
    groq_vision_model_name: str = 'llama-3.2-11b-vision-preview'
    
    # App & API settings
    api_token: str = ''
    allowed_origins: str = 'http://localhost:8000,https://127.0.0.1:8000'
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()    
