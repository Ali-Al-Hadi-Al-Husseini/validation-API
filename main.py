from flask import Flask
from re import search 
from socket import gethostname
from smtplib import SMTP
import dns.resolver

app = Flask(__name__)


@app.route('/email/<email>')
def email_validator(email):
    email_regex = '^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$'

    if search(email_regex, email):
            domain_name = email.split('@')[1]

        # try:
            records = dns.resolver.resolve(domain_name, 'MX')
            mxrecord = records[0].exchange
            mxrecord = str(mxrecord)

            host = gethostname()

            server = SMTP()
            server.set_debuglevel(0)
            print(domain_name)
            server.connect(mxrecord)
            server.helo(host)
            server.mail(email)
            code, message = server.rcpt(str(email))
            server.quit()

            return code
        #
        # except:
        #     return 'False'

    else:
        return "False"


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
        print(numbers_list[idx])
        if new_num > 9:
            new_num = sum_of_num(new_num)

        numbers_list[idx] = new_num
    print(numbers_list)
    return str(sum(numbers_list) % 10 == 0)


if __name__ == "__main__":
    app.run(debug=True)
