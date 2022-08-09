import motor.motor_asyncio
from model import Url,API_Key
from beanie import init_beanie
from api_key import hashText,generate_key

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://lilo786:9AQBmtsNjgUKSZdv@cluster0.qlj5qef.mongodb.net/?retryWrites=true&w=majority")
db_inited = [False]

async def init_db():
    await init_beanie(database=client.Urls, document_models=[Url])
    await init_beanie(database=client.Keys,document_models=[API_Key])
    db_inited[0] = True



database = client.Urls
db = client.Keys
url_collection = database.get_collection('Url')
API_Key_collection = db.get_collection('API_Key')

async def fetch_url_by_key(key):
    if not db_inited[0]:await init_db()
    return await url_collection.find_one({"key":key})

async def fetch_url_by_url(url):
    if not db_inited[0]:await init_db()
    return await url_collection.find_one({"url":url})

async def add_url(url ,key):
    if not db_inited[0]:await init_db()
    document = {
                'url': url,
                'key': key
    }
    await url_collection.insert_one(document)
    return document

async def create_api_key():
    if not db_inited[0]:await init_db()

    key = generate_key()
    hashed_key = hashText(key)

    while await fetch_api_key(hashed_key) != None:
        key = generate_key()
        hashed_key = hashText(key)
        
    document = {
        'key':hashed_key
    }
    
    await API_Key_collection.insert_one(document)
    return key

async def fetch_api_key(key):
    if not db_inited[0]:await init_db()
    return await API_Key_collection.find_one({'key':hashText(key)})