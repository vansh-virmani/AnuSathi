import os
from dotenv import load_dotenv
load_dotenv()  #this load env varibales from .env file
class Settings:
    QDRANT_KEY=os.getenv('QDRANT_KEY')
    QDRANT_ENDPOINT=os.getenv('QDRANT_ENDPOINT') #connects to quadrant 
    QDRANT_COLLECTION_NAME="research_papers" #whenever the qdrant pipeline will run we'll see this name there in collections
    HF_TOKEN=os.getenv('HF_TOKEN')
    HF_MODEL=os.getenv('HF_MODEL')
    EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"
    MAX_NEW_TOKENS = 1024
    TEMPERATURE = 0.2
    TOP_P = 0.9
    
    
settings=Settings()
    
    

