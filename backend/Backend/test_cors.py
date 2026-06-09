import urllib.request

url = "http://localhost:8000/api/v1/auth/login"
req = urllib.request.Request(url, method="OPTIONS")
req.add_header("Origin", "https://ai-attendance-system-s8wy.vercel.app")
req.add_header("Access-Control-Request-Method", "POST")
req.add_header("Access-Control-Request-Headers", "Content-Type")

try:
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
        print("Headers:", resp.headers)
except Exception as e:
    if hasattr(e, 'headers'):
        print("Error Status:", e.code)
        print("Error Headers:", e.headers)
    else:
        print("Error:", e)
