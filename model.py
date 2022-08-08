from pydantic import BaseModel
from beanie import Document




class API_Key(Document):
    Key_Hash:str

    class Settings:
        name = "api-key-hash"

    class Config:
        schema_extra = {
            "example": {
                "Key_Hash": "1812592afaf8ece2f762c611caac0c9421a92fa256b56e7ffde4915f149a2d73",
            }
        }

class Url(Document):
    url: str
    key: str    


    class Settings:
        name = "URL"

    class Config:
        schema_extra = {
            "example": {
                "url": "www.google.com",
                "key": "9ad3s52",
            }
        }