from flask import Flask, redirect, jsonify
from re import search
import smtplib
from os import popen
import dns.resolver
from flask_sqlalchemy import SQLAlchemy
from string import ascii_letters, digits
from random import choice
from requests import get

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def find_best_mx(result):
    mx_score   = [result[8], result[17],result[26],result[35],result[44]]
    mx_records = [result[12], result[21],result[30],result[39], result[48]]
    smallest = float('inf')
    for i in range(len(mx_score)):
        if smallest > 1:
            smallest = i

    return mx_records[smallest]

@app.route('/email/<email>')
def email_validator(email):
    email_regex = "^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$"

    if search(email_regex, email):
        domain_name = email.split('@')[1]
        if _domain_validator(domain_name):
            try:
                records = dns.resolver.resolve(domain_name, 'MX')
                mxRecord = records[0].exchange
                mxRecord = str(mxRecord)

                # SMTP lib setup
                server = smtplib.SMTP()

                fromAddress = 'just_a_place_holder@domain.com'

                # SMTP Conversation
                server.connect(mxRecord)
                server.helo(server.local_hostname)  ### server.local_hostname(Get local server hostname)
                server.mail(fromAddress)
                code, message = server.rcpt(str(email))
                server.quit()
            finally:
                result = "true" if (code == 250) else 'false'

                return jsonify({
                    'type': "email",
                    "valid": result,
                    "form": "true",
                    "domain": "true"

            })
        else:
            return jsonify({
                'type': "email",
                "valid": "false",
                "form": "true",
                "domain": "false"

            })
    else:
        return jsonify({
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
@app.route("/card/<number>")
def card_validator(number):
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
    return jsonify({
        "type": "card",
        "valid": result,
    })

@app.route("/domain/<domain_name>")
def domain_validator(domain_name):
    response = popen(f"ping {domain_name}").read()

    if "Received = " in response:
        return jsonify({
            "type": "domain",
            "valid": "true"
        })
    else:
        return jsonify({
            "type": "domain",
            "valid": "false"
        })

#for internal use only
def _domain_validator(domain_name):
    response = popen(f"ping {domain_name}").read()

    if "Received = " in response:
        return True
    else:
        return False


@app.route("/ssl/<path:url>")
def ssl_validator(url):
    ssl_regex = "^(http://)"
    if search(ssl_regex, url):
        url = url[8:]
    if url[-1] == '/':
        url = url[:-1]
    print(url)
    if _domain_validator(url):
        try:
            req = get("https://" + url)
            print(req)
            return jsonify({
                "type": "ssl",
                "valid": "true",
                "domain": "true"
            })

        except Exception:
            return jsonify({
                "type": "ssl",
                "valid": "false",
                "domain": "true"
            })
    else: return jsonify({
                "type": "ssl",
                "valid": "false",
                "domain": "false"
            })

def generate_random_key():
    return ''.join(choice(ascii_letters + digits) for i in range(8))

def check_if_exists(url):
    url = Url.query.filter_by(shortened_url=url).first()
    result = url != None
    return result

# model for url shortner
class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortened_url = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(1000))

    def __init__(self, url, shortened):
        self.url = str(url)
        self.shortened_url = str(shortened)


# @app.route("/shorten/<url>/<shortened_version>")
@app.route("/shorten/<path:url>")
def shorten_url(url):
    http_regex =  "^(http://)"
    https_regex = "^(https://)"

    if search(http_regex, url):
        url = url[11:]
    if search(https_regex, url):
        url = url[12:]

    path_list = list(str(url).split("/"))
    last_path = path_list[-1]
    url = ''.join(path_list[:len(path_list) - 1]) if len(path_list) > 1 else ''.join(path_list[:])
    shortened_version = last_path[2:] if last_path[:2] == "==" else None

    if not _domain_validator(url):
        return jsonify({
            "domain": "false",
            "shorten": "false",
            "key": ""
        })

    if shortened_version is not None:
        shortened_version = str(shortened_version)
        does_exist = check_if_exists(shortened_version)
        if does_exist:
            return jsonify({
            "domain": "true",
            "shorten": "false",
            "key": ""
        })
        else:
            new_url = Url(url, shortened_version)
            key = shortened_version
    else:
        key = generate_random_key()
        while check_if_exists(key):
            key = generate_random_key()
        new_url = Url(url, key)

    db.session.add(new_url)
    db.session.commit()
    return jsonify({
        "domain": "true",
        "shorten": "true",
        "key": key
    })

@app.route("/<key>")
def visit_shortend(key):
    URL = Url.query.filter_by(shortened_url=str(key)).first()
    return redirect("http://" + URL.url)

@app.route("/uszip/<zip_code>")
def visit_uszip(zip_code):
    us_zip_regex = "^[0-9]{5}(?:-[0-9]{4})?$"

    if search(us_zip_regex, zip_code):
        return jsonify({
            "type": "zip",
            "country": "us",
            "valid": "true"
        })
    return jsonify({
            "type": "zip",
            "country": "us",
            "valid": "false"
        })

@app.route("/lbzip/<zip_code>")
def visit_lbzip(zip_code):
    us_zip_regex = "^1[0-9]{3}$"

    if search(us_zip_regex, zip_code):
        return jsonify({
            "type": "zip",
            "country": "lb",
            "valid": "true"
        })
    return jsonify({
            "type": "zip",
            "country": "lb",
            "valid": "false"
        })

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
