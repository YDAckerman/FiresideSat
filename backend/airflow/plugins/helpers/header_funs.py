import base64


def get_auth_basic(usr, pw):
    usr_pw = f'{usr}:{pw}'
    b64_val = base64.b64encode(usr_pw.encode()).decode()
    return {"Authorization": "Basic %s" % b64_val}
