from datetime import datetime
import requests

SMS_LOGIN = ''
SMS_PASSWORD = ''
SMS_URL = ''

def send_verification_code(phone, code):
    message_id = str(datetime.now()) # noqa
#    requests.post(
#        SMS_URL,
#        auth=(SMS_LOGIN, SMS_PASSWORD),
#        json={
#            "messages": [
#                {
#                    "recipient": str(phone),
#                    "message-id": message_id,
#                    "sms": {
#                        "originator": "3700",
#                        "content": {
#                            "text": f"Fast food <#> Your verification code is {code}"
#                        },
#                    },
#                }
#            ]
#        },
#    )


