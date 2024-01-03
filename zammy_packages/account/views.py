import requests, os, jwt, random, string
from django.shortcuts import redirect
from django.http import JsonResponse


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")
LINE_CLIENT_ID = os.environ.get("LINE_CHANNEL_ID")
LINE_CLIENT_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.environ.get("LINE_REDIRECT_URI")


def create_nonce_string():
    nonce_len = 7
    nonce = ""
    for i in range(0, 3):
        for _ in range(nonce_len):
            nonce += str(random.randint(0, 9))
        if i < 2:
            nonce += "-"
    return nonce


def google_login(request):
    nonce = create_nonce_string()
    url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&scope=openid%20profile%20email&redirect_uri={GOOGLE_REDIRECT_URI}&nonce={nonce}"
    return redirect(url)


def google_callback(request):
    code = request.GET.get("code")
    ContentType = "application/x-www-form-urlencoded"
    url = f"https://www.googleapis.com/oauth2/v4/token?grant_type=authorization_code&code={code}&client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_CLIENT_SECRET}&redirect_uri={GOOGLE_REDIRECT_URI}"
    info = requests.post(url, headers={"Content-type": ContentType}).json()
    if "error" in info:
        print("error", info["error"])
        return info["error"]
    id_token = info["id_token"]
    decoded = jwt.decode(
        id_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    return JsonResponse({"id_token": id_token})


def create_state_string():
    state_len = 10
    state_cadidate = (
        string.ascii_letters
        + string.digits
        + string.punctuation.replace('"', "%").replace("=", "%")
    )

    state = ""
    for i in range(state_len):
        state += random.choice(state_cadidate)

    return state


def line_login(request):
    nonce = create_nonce_string()
    state = create_state_string()
    url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={LINE_CLIENT_ID}&redirect_uri={LINE_REDIRECT_URI}&state={state}&scope=profile%20openid%20email&nonce={nonce}"
    return redirect(url)


def line_callback(request):
    code = request.GET.get("code")
    ContentType = "application/x-www-form-urlencoded"
    url = "https://api.line.me/oauth2/v2.1/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINE_REDIRECT_URI,
        "client_id": LINE_CLIENT_ID,
        "client_secret": LINE_CLIENT_SECRET,
    }
    info = requests.post(
        url, headers={"Content-type": ContentType}, data=payload
    ).json()
    if "error" in info:
        print("error", info["error"])
        return JsonResponse(info["error"])
    id_token = info["id_token"]
    decoded = jwt.decode(
        id_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    return JsonResponse({"id_token": id_token})
