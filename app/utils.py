import base64
import imghdr
import re

import requests
from flask import request, jsonify

from app.log import logger


def parse_markdown_text(text: str) -> list[dict]:

    result = []
    # 提取第一句话
    first_sentence = text.split('\n')[0].strip()

    # 正则表达式匹配图片和文件链接
    image_pattern = r'\!\[.*?\]\((.*?)\)'
    file_pattern = r'\[.*?\]\((.*?)\)'

    # 查找所有匹配的图片链接
    image_links = re.findall(image_pattern, text)
    # 查找所有匹配的文件链接
    file_links = re.findall(file_pattern, text)

    element = set(image_links + file_links)

    files = ("jpg", "jpeg", "png", "gif", "img","mp4", "avi", "mov", "pdf","doc", "docx", "xls", "xlsx", "zip", "rar", "txt")

    # 构建输出格式
    if first_sentence:
        result = [first_sentence]

    for e in element:
        if contains_str(e.lower(), files):
            result.append(e)

    logger.info(f"element: {str(result)}")
    return result

def contains_str(content,strs):
    for s in strs:
        if s in content:
            return True
    return False

def get_auth_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    return auth_header.split(" ")[0]


def handle_error(e):
    error_response = {
        "error": {
            "message": str(e),
            "type": "coze_2_api_error"
        }
    }
    return jsonify(error_response), 500


def generate_error_response(message, status_code):
    error_response = {
        "error": {
            "message": str(message),
            "type": "coze_api_error"
        }
    }
    return jsonify(error_response), 500


def upload_image_to_telegraph(base64_string):
    try:
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        image_data = base64.b64decode(base64_string)

        image_type = imghdr.what(None, image_data)
        if image_type is None:
            raise ValueError("Invalid image data")

        mime_type = f"image/{image_type}"
        files = {'file': (f'image.{image_type}', image_data, mime_type)}
        response = requests.post('https://telegra.ph/upload', files=files)

        response.raise_for_status()
        json_response = response.json()
        if isinstance(json_response, list) and 'src' in json_response[0]:
            return 'https://telegra.ph' + json_response[0]['src']
        else:
            raise ValueError(f"Unexpected response format: {json_response}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to upload image. Error: {e}")
    except Exception as e:
        raise Exception(f"Failed to upload image. An error occurred: {e}")


def is_dict_list(obj):
    if not isinstance(obj, list):
        return False
    for element in obj:
        if not isinstance(element, dict):
            return False
    return True
