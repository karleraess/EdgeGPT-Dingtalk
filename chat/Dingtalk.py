# !/usr/bin/env python

import argparse
import logging
from dingtalk_stream import AckMessage, ChatbotMessage
import dingtalk_stream

import asyncio
import json

from re_edge_gpt import Chatbot
from re_edge_gpt import ConversationStyle

import nest_asyncio
import re


async def test_ask(query, incoming_message: ChatbotMessage, handler: dingtalk_stream.ChatbotHandler) -> None:
    bot = None
    try:
        # cookies = json.loads(open(
        #     str(Path(str(Path.cwd()) + "/bing_cookies.json")), encoding="utf-8").read())
        cookies = json.loads(open("./bing_cookies.json", encoding="utf-8").read())
        bot = await Chatbot.create(cookies=cookies)
        # print(query)
        response = await bot.ask(
            prompt=query,
            # prompt="杭州的天气",
            conversation_style=ConversationStyle.precise,
            simplify_response=True
        )
        # If you are using non ascii char you need set ensure_ascii=False
        # print(json.dumps(response, indent=2, ensure_ascii=False))
        text = re.sub(r'\[\^\d\^\]', '', response["text"])
        handler.reply_markdown('EdgeGPT', text, incoming_message)

        # Raw response
        # print(response)
        assert response
    except Exception as error:
        raise error
    finally:
        if bot is not None:
            await bot.close()

def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def define_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--client_id', dest='client_id', required=True,
        help='app_key or suite_key from https://open-dev.digntalk.com'
    )
    parser.add_argument(
        '--client_secret', dest='client_secret', required=True,
        help='app_secret or suite_secret from https://open-dev.digntalk.com'
    )
    options = parser.parse_args()
    return options


class CalcBotHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, logger: logging.Logger = None):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        if logger:
            self.logger = logger

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        msg = incoming_message.text.content.strip()
        # self.logger.info('msg = %s' % (msg))

        try:
            nest_asyncio.apply()
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            loop.run_until_complete(test_ask(msg, incoming_message, self))
        except Exception as e:
            self.reply_text(str(e), incoming_message)

        # response = msg
        # self.reply_text(response, incoming_message)

        return AckMessage.STATUS_OK, 'OK'

def main():
    logger = setup_logger()
    # options = define_options()

    credential = dingtalk_stream.Credential('dingcist2sdawbz05oyn', 'dmECz-lO5n5f2g21qSejlqnJlShc5eynvylHmrmWlpFBtgaumKW6fL1oCUyr0Eop')
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, CalcBotHandler(logger))
    client.start_forever()


if __name__ == '__main__':
    main()