import requests
import base64
from PIL import Image
from io import BytesIO
import io
import cv2
import numpy as np
import os


def image2base64(image_file_path: str, use_opencv: bool = False):
    base64str = ""
    if use_opencv:
        image = cv2.imread(image_file_path)
        _, buffer = cv2.imencode(".jpg", image)
        base64str = base64.b64encode(buffer)
    else:
        with open(image_file_path, "rb") as image_file:
            image = Image.open(image_file).convert("RGB")
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            base64str = base64.b64encode(buffered.getvalue())
    return base64str.decode("utf-8")


def base642image(base64str: str, use_opencv: bool = False):
    image = None
    if use_opencv:
        data_bytes = np.frombuffer(base64.b64decode(base64str), np.uint8)
        image = cv2.imdecode(data_bytes, cv2.IMREAD_COLOR)
    else:
        image_bytes = base64.b64decode(base64str)
        image = Image.open(io.BytesIO(image_bytes))
    return image


def authenticate_user(username: str, password: str) -> str:
    login_url = "http://127.0.0.1:8001/user/login"
    login_data = {"user_name": username, "password": password}

    response = requests.post(login_url, json=login_data)
    # print(f"Login response: {response.status_code} - {response.text}")

    if response.status_code == 200:
        tokens = response.json()
        return tokens.get('access_token')
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None


def upload_image(access_token: str, image_file_path: str):
    print(f"Using access token: {access_token}")  # Debugging line
    b64str = image2base64(image_file_path, use_opencv=True)
    url = "http://127.0.0.1:8000/face/detect_faces"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    data = {"image_base64": b64str}
    response = requests.post(url, json=data, headers=headers)

    # Debugging line
    print(f"Upload response: {response.status_code} - {response.text}")

    if response.status_code == 200:
        result_json = response.json()
        if "result" in result_json:
            output_dir = "../output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            image = base642image(result_json["result"], use_opencv=True)
            cv2.imwrite(os.path.join(output_dir, "result.jpg"), image)
        else:
            print("Response does not contain 'result'")
    else:
        print(
            f"Request failed with status code {response.status_code}: {response.text}")


if __name__ == "__main__":
    username = "test1"
    password = "test123"

    access_token = authenticate_user(username, password)
    if access_token:
        upload_image(access_token, "../client/test_image.png")
