import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:5000"


def request_json(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(BASE_URL + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = resp.read().decode("utf-8")
            return resp.getcode(), json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        return exc.code, json.loads(payload) if payload else {}


def print_case(name, passed, detail=""):
    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] {name} :: {detail}")
    return passed


def wait_server():
    for _ in range(20):
        code, _ = request_json("GET", "/api/health")
        if code == 200:
            return True
        time.sleep(0.3)
    return False


def main():
    if not wait_server():
        print("Server is not ready:", BASE_URL)
        return

    passed_count = 0
    total = 0
    ts = int(time.time())

    user = {
        "username": f"blog_user_{ts}",
        "email": f"blog_user_{ts}@example.com",
        "password": "123456",
    }

    # 1) 用户注册
    total += 1
    code, body = request_json("POST", "/api/users/register", user)
    ok = code == 201
    passed_count += 1 if print_case("1. 用户注册", ok, str(code)) else 0

    # 2) 用户登录
    total += 1
    code, body = request_json(
        "POST",
        "/api/users/login",
        {"email": user["email"], "password": user["password"]},
    )
    token = body.get("data", {}).get("token") if code == 200 else None
    ok = code == 200 and bool(token)
    passed_count += 1 if print_case("2. 用户登录", ok, str(code)) else 0

    # 3) 发布文章
    total += 1
    code, body = request_json(
        "POST",
        "/api/posts",
        {"title": "simple blog test", "content": "simple content"},
        token=token,
    )
    ok = code == 201
    passed_count += 1 if print_case("3. 发布文章", ok, str(code)) else 0

    print(f"SUMMARY: {passed_count}/{total} passed")


if __name__ == "__main__":
    main()
