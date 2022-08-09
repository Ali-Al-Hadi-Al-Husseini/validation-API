from importlib.resources import path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse,HTMLResponse,JSONResponse
from re import search
from os import popen
from string import ascii_letters, digits
from random import choice
from requests import get
import smtplib
import dns.resolver
import uvicorn


from database import (
    fetch_url_by_key,
    fetch_url_by_url,
    add_url,
    fetch_api_key,
    create_api_key
)

app = FastAPI()



def find_best_mx(result):

    mx_score   = [result[8], result[17],result[26],result[35],result[44]]
    mx_records = [result[12], result[21],result[30],result[39], result[48]]
    smallest = float('inf')

    for i in range(len(mx_score)):
        if smallest > 1:
            smallest = i

    return mx_records[smallest]

@app.get('/',response_class=HTMLResponse)
def main():
    return """To visit the shoterned url use the WEBSITE_URL/given_key. 
              To test the api visit <a href="/docs#/">here</a>.
              To see API's code visit <a href="https://github.com/Ali-Al-Hadi-Al-Husseini/validation-API" target="_blank">Github</a>"""

@app.get('/email')
async def email_validator(email: str,apiKey:str):
    email_regex = "^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$"
    
    if search(email_regex, email):

        domain_name = email.split('@')[1]

        if _domain_validator(domain_name):
            code = 0
            try:
                records = dns.resolver.resolve(domain_name, 'MX')
                mxRecord = records[0].exchange
                mxRecord = str(mxRecord)

                # SMTP lib setup
                server = smtplib.SMTP()

                fromAddress = 'just_a_place_holder@domain.com'

                # SMTP Conversation
                for _ in range(10):
                    server.connect(mxRecord)
                    server.helo(server.local_hostname)  ### server.local_hostname(Get local server hostname)
                    server.mail(fromAddress)
                    code, message = await server.rcpt(str(email))
                    server.quit()
                    break
            finally:

                result = "true" if (code == 250) else 'false'

                return ({
                    'type': "email",
                    "valid": result,
                    "form": "true",
                    "domain": "true"

            })
        else:
            return ({
                'type': "email",
                "valid": "false",
                "form": "true",
                "domain": "false"

            })
    else:
        return ({
            'type': "email",
            "vaild": "false",
            "form": "false"

        })


def sum_of_num(num):
    num_sum = 0
    for digit in str(num):
        num_sum += int(digit)

    return num_sum


# using luhan algo
@app.get("/card")
def card_validator(number: int,apiKey:str):

    numbers_list = [int(num) for num in list(str(number))]
    numbers_list.reverse()

    for idx in range(1, len(numbers_list), 2):
        new_num = numbers_list[idx] * 2

        if new_num <= 9:
            pass
        else:
            new_num = sum_of_num(new_num)

        numbers_list[idx] = new_num

    result = "true" if sum(numbers_list) % 10 == 0 else "false"

    return ({
        "type": "card",
        "valid": result,
    })

@app.get("/domain")
async def domain_validator(domain: str):

    domain_name = domain
    response = await popen(f"ping {domain_name}").read()

    if "Received = " in response:
        return ({
            "type": "domain",
            "valid": "true"
        })
    else:
        return ({
            "type": "domain",
            "valid": "false"
        })

#for internal use only
def _domain_validator(domain_name):
    response = popen(f"ping {domain_name}")

    if "Received = " in response.read():
        return True
    else:
        return False


@app.get("/ssl/")
async def ssl_validator(url: str,apiKey:str):

    ssl_regex = "^(http://)"
    if search(ssl_regex, url):
        url = url[8:]
    if url[-1] == '/':
        url = url[:-1]

 
    if  _domain_validator(url):
        try:
            req = await get("https://" + url)
            
            return ({
                "type": "ssl",
                "valid": "true",
                "domain": "true"
            })

        except Exception:
            return ({
                "type": "ssl",
                "valid": "false",
                "domain": "true"
            })
    else: return ({
                "type": "ssl",
                "valid": "false",
                "domain": "false"
            })

def generate_random_key():
    return ''.join(choice(ascii_letters + digits) for i in range(8))

async def check_if_exists(key):
    result = await fetch_url_by_key(key)    
    return result != None

# model for url shortner
# class Url(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     shortened_url = db.Column(db.String(100), unique=True)
#     url = db.Column(db.String(1000))

#     def __init__(self, url, shortened):
#         self.url = str(url)
#         self.shortened_url = str(shortened)


@app.get("/shorten")
async def shorten_url(url: str,apiKey:str):

    http_regex =  "^(http://)"
    https_regex = "^(https://)"

    
    # if not   _domain_validator(url):
    #     return ({
    #         "domain": "false",
    #         "shorten": "false",
    #         "key": ""
    #     })

    document = await fetch_url_by_url(url)
    if document != None:
        return ({
            "domain": "True",
            "shorten": "false",
            "key": document['key']
        })

    key = generate_random_key()

    while await check_if_exists(key):
        key = generate_random_key()

    await add_url(url,key)

    return ({
        "domain": "true",
        "shorten": "true",
        "key": key
    })

#holas
@app.get("/visit/{key}",response_class=RedirectResponse ,status_code=302)
async def visit_shortend(key: str):
    URL = await fetch_url_by_key(key)
    if URL == None:return "No such url path or code"
    if "https://" in URL['url'] or "http://" in URL['url']:
        return (URL["url"])
    else:
        return "http://" + URL["url"]

@app.get("/uszip")
def visit_uszip(zip: int, apiKey:str):

    zip_code = zip
    us_zip_regex = "^[0-9]{5}(?:-[0-9]{4})?$"

    if search(us_zip_regex, zip_code):
        return ({
            "type": "zip",
            "country": "us",
            "valid": "true"
        })
    return ({
            "type": "zip",
            "country": "us",
            "valid": "false"
        })

@app.get("/lbzip")
def visit_lbzip(zip: int,apiKey:str):

    zip_code = zip
    us_zip_regex = "^1[0-9]{3}$"

    if search(us_zip_regex, zip_code):
        return ({
            "type": "zip",
            "country": "lb",
            "valid": "true"
        })
    return {
            "type": "zip",
            "country": "lb",
            "valid": "false"
        }



@app.get("/api-key")
async def give_me_my_key():
    key = await create_api_key()
    return HTMLResponse(f""" {key} is your API code make sure to save it some because it's only showen once """)

@app.middleware('http')
async def check_for_key(request, call_next):
    exceptions = set(['/api-key','/','/docs#'])
    key = request.query_params.get('apiKey',None)

    if request.url.path not in routes:
        JSONResponse({'response':"URL Path is not valid"})

    elif request.url.path in exceptions or 'visit' in request.url.path:
        pass

    elif key == None:
        return JSONResponse({'response':"You need an api key tp use this api"})

    elif await fetch_api_key(key) == None  : 
        return JSONResponse({'response':"api-key is not valid"})

    return await call_next(request)

routes = set([route.path for route in app.routes])
if __name__ == "__main__":
    routes = set([route.path for route in app.routes])
    uvicorn.run(app)