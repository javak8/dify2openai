import io
import logging
import time

import requests
from flask import request, jsonify, Response, g, current_app as app,session

from .dify_client import ChatClient
from .log import logger
from .utils import get_auth_token, handle_error, parse_markdown_text

logging.basicConfig(level=logging.DEBUG)


@app.before_request
def before_request():
    g.data = request.get_json(silent=True)
    print(request.get_json(silent=True))


@app.route('/', methods=['GET'])
def index():
    return '''
        <html>
            <head>
                <title>Coze2OpenAI</title>
            </head>
            <body>
                <h1>Coze2OpenAI</h1>
                <p>DONE.</p>
            </body>
        </html>
    '''


@app.route('/v1/chat/completions', methods=['GET', 'POST', 'OPTIONS'])
def chat_completions():

    if request.method == "OPTIONS":
        return Response(status=204)

    api_key = get_auth_token()
    if not api_key:
        return jsonify({'code': 401, 'errmsg': 'Unauthorized.'}), 401

    try:
        data = g.data
        messages = data.get("messages", [])
        model = data.get("model")
        user = data.get("user")

        bot_type = model.split(":")[0]
        conversation_id = data.get("conversation_id","")
        query = messages[-1]

        if bot_type.lower() == 'chatbot':
            return handle_chatbot(api_key=api_key, query=query,conversation_id=conversation_id, user=user ,model=model)


    except Exception as e:
        return handle_error(e)


def handle_chatbot(api_key, query ,conversation_id, user, model):
    api_base = app.config.get("API_BASE", 'http://dify.com')
    api_key = api_key
    api_base = api_base

    # todo: bot类型和stream类型的处理
    stream = model.split(":")[1] if len(model.split(":")) > 1 else 'blocking'

    # todo: files的处理，query可能包含url地址（file,image), 则需要赋值到file[{
    #         "type": "image",
    #         "transfer_method": "remote_url",
    #         "url": "https://cloud.dify.ai/logo/logo-site.png"
    #       }]中
    files = []

    chat_client = ChatClient(api_key, api_base)
    payload = get_payload(query, conversation_id, stream, user)

    response = chat_client.create_chat_message(
        inputs=payload['inputs'],
        query=payload['query'],
        user=payload['user'],
        response_mode=payload['response_mode'],
        conversation_id=payload['conversation_id'],
        files= files
    )

    if response.status_code != 200:
        error_info = f"[DIFY] response text={response.text} status_code={response.status_code}"
        logger.warn(error_info)
        return None, error_info

    rsp_data = response.json()
    logger.debug("[DIFY] usage {}".format(rsp_data.get('metadata', {}).get('usage', 0)))

    answer = rsp_data['answer']
    content = parse_markdown_text(answer)

    if session.get('conversation_id') == '' or session.get('conversation_id') == None:
        session['conversation_id'] = rsp_data['conversation_id']
    logger.info(session.get('conversation_id'))
    usage_data = {
        "prompt_tokens": rsp_data['metadata']['usage']['prompt_tokens'],
        "completion_tokens": rsp_data['metadata']['usage']['completion_tokens'],
        "total_tokens": rsp_data['metadata']['usage']['total_tokens']
    }

    formatted_response = {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content
            },
            "logprobs": None,
            "finish_reason": "stop"
        }],
        "usage": usage_data,
        "system_fingerprint": "fp_2f57f81c11"
    }
    return jsonify(formatted_response)


def get_payload(query, conversation_id, response_mode,user):
    return {
        'inputs': {},
        "query": query,
        "response_mode": response_mode,
        "conversation_id": conversation_id,
        "user": user
    }

def fill_file_base_url(url: str):
    if url.startswith("https://") or url.startswith("http://"):
        return url
    # 补全文件base url, 默认使用去掉"/v1"的dify api base url
    return get_file_base_url() + url

def get_file_base_url(self) -> str:
    api_base = app.config["dify_api_base", "https://api.dify.ai/v1"]
    return api_base.replace("/v1", "")

def download_image(self, url):
    try:
        pic_res = requests.get(url, stream=True)
        pic_res.raise_for_status()
        image_storage = io.BytesIO()
        size = 0
        for block in pic_res.iter_content(1024):
            size += len(block)
            image_storage.write(block)
        logger.debug(f"[WX] download image success, size={size}, img_url={url}")
        image_storage.seek(0)
        return image_storage
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
    return None
