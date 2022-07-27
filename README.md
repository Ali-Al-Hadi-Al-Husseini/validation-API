
# Multi-Task API 

## General request
```python
from requests import get 
respsone = get('domain/route?argument=Your-Input')# Card-Number
```

| Description                       		| Route  | Argument | 
|---------------------------------------|--------|----------|
| Validates visa/mastercard numbers 		| /card   | number   |
| Validates Email                   		| /email  | email    |
| Validates Domain                  		| /domain | domain   |
| Validates SSL Ceritifacte         		| /ssl    | url      |
| Validate US Zip Code              		| /uszip  | zip      |
| validate LB Zip Code              		| /lbzip  | zip      |
| Shorten url and responds with code		|/shorten | url      |

## URL Shortening

```python
from requests import get
response = get('domain/shorten?url=URL_You_want_to_shorten')
shortened_code = response.content.key
# you  need to convert the response from json
#you can visit your link by visit domain/shotened_code
```
