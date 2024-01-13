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

bing_cookies = '[{"domain":".microsoft.com","expirationDate":1736607283.76877,"hostOnly":false,"httpOnly":false,"name":"MC1","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"GUID=d8e20e8d14c64e73b9f01f80b3a142cf&HASH=d8e2&LV=202401&V=4&LU=1705071282789","id":1},{"domain":"copilot.microsoft.com","hostOnly":true,"httpOnly":true,"name":"_EDGE_S","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"SID=26A945774B576D9734C451734A566C5C","id":2},{"domain":"copilot.microsoft.com","expirationDate":1738767251.300868,"hostOnly":true,"httpOnly":true,"name":"_EDGE_V","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"1","id":3},{"domain":"copilot.microsoft.com","expirationDate":1739635290.722475,"hostOnly":true,"httpOnly":false,"name":"_RwBf","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"mta=0&rc=0&rb=0&gb=0&rg=0&pc=0&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=2&l=2024-01-12T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&ard=0001-01-01T00:00:00.0000000&rwdbt=0001-01-01T16:00:00.0000000-08:00&o=0&p=MSAAUTOENROLL&c=MR000T&t=2790&s=2023-11-20T03:18:54.9869465+00:00&ts=2024-01-12T16:01:14.9208815+00:00&rwred=0&wls=2&wlb=0&wle=0&ccp=0&lka=0&lkt=0&aad=0&TH=&dci=0&e=4KR0ciU6wKHWb13cmoLJmmnBE35VOyW5qxN86KIFOBPfIYrrOgjKOYM8PCUnXBWcob5jixsBWFvaL38RuPW9ZsGdwIqYssNSvKTt1rpRN0c&A=DEEBC9C376F36F3F98ADC479FFFFFFFF","id":4},{"domain":"copilot.microsoft.com","hostOnly":true,"httpOnly":true,"name":"_Rwho","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"u=d","id":5},{"domain":"copilot.microsoft.com","hostOnly":true,"httpOnly":false,"name":"_SS","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"SID=26A945774B576D9734C451734A566C5C&R=0&RB=0&GB=0&RG=0&RP=0","id":6},{"domain":"copilot.microsoft.com","expirationDate":1706280909.649864,"hostOnly":true,"httpOnly":false,"name":"_U","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"1QGnP2H0G7NhgkvssUyEhN7xtBPnttdAjqyrvOtPfy40w89PACduhKbZkW-BAyoxS4MtRJvmEkds0NUhvmT4KBr0G-wq82zh-SPeL2Wx3D3hZJMYpm3FGmsN4zcV9fGIBxjJiF02lMkbd3iNjvEG14ls8ALsu8ua55qZ5_pH8rVzDWPNThc3EiyFXiMK95j_7kqJrWuXBouqRC6a-tmJNVg","id":7},{"domain":"copilot.microsoft.com","expirationDate":1720796109.649761,"hostOnly":true,"httpOnly":false,"name":"ANON","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"A=DEEBC9C376F36F3F98ADC479FFFFFFFF&E=1d48&W=1","id":8},{"domain":"copilot.microsoft.com","expirationDate":1739631309.649822,"hostOnly":true,"httpOnly":true,"name":"KievRPSSecAuth","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"FABaBBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACOwK+mXDZIidGATSYeDKkZBpePHq+e31ZXI7ltkoDMtfinNjgzAF1+WXwkZ9Vea1jrcZd9ste+FXWzVqZZlY/a4llQHvs1lPlza5BvY/ORzL5nGCVibMsNCwkn4Y26I612e7rOlMuUYx6xefb4mICmQssemmkwuR6ggxFz75WP8WHdUnn4Wc1K4E+1lENHXvnoox2u0nw4qp/H3qoy7fCiew30vNEb0PcZlwRfqssrkT0Y5HbKgmTI3uuI4NWrvnt87AsfmsLf9o1u2H7sUxJItPIq9TiAE0Zb1w6hVGcrMEUTxjql6gAZP1dIhYw9guKpODViq30AoAoxR6nKcrzkd4Sf9WCS/qIghRAo5pMeDKBbpSDm+c+kE0eSxFCXFF2diCievOC2NuP7d65DM3iW7EGn2mjVzuF/BH/c36WUydPUeR5j153MP0WnzGDdENtBlVL5DypJGgUmlH0K4vnqSuTR578GZYs9AjkNjztJnLMAMSU0PPuzaAGG7nN6Fo0wrZdM+9OoV91ES8jsxpqO2UjfUBOUx1QdhkRF5SqrWSHRfV1IWjkZiBnsmrlE2dGKHlnB0DzDTfKgo476sJXz+Nfbluerikh9oGUixV2MgolftMT1U6Oz4VJFJhu2MFQZVi954qhbeIzSBLN1FNx0yKKN62ROAOWMYuz4ONXLniRuXD9f2VYEiiUdSZutkZR0QyuU/A8i+YUrc7LAkETnmoj3jGlWIl9OhgUrnA1B0lZByZlVGYg+v34tTOE1dShaHJJqVI5aZp5ezXOziSkXzNZo1vHJTN7jfNrNgDIZg3jEAWL8ONtjlSi2jB+6t9CK11fbGAPWnGGA3UwApWBxv9Wz+vUz9fWOysJt02FxfjawxVzl6Rz6iLwU9+u5DrqvCRIyqhQi3LMPOH9/37Z75M6BMATtAEbC/ZMaWVn9vF6HuryYNaHn4UAiRu6BmiGBfcm2lVpS8hodcTIZEORX4qs4AXaJkTjz6pXvtpX1yj4BBti9BOIbSnTkfsA0LpdSHzZJ+fyg5fs9ZOIdEY6tmkbvRVA/DThXYYCkrhAo99rrRO6IdldbWTx2WID2rziy1ss77peIB6GSWyRpCiBTrmGQaUP9lPeKdTIek2TZkfijVuLl+YPFv/x212EWUzu/4jJ7JtXdiNQFf1gW1y3/TElFQrbzr1Zxk/hEA8m0GtFEbs5DiZypqONeryOM0AzSa+M6XIkYAeUuG87+I0ca8Lp6vdZrHuijXQBVhNVaFl4mRgmv0n0Por5XMnQGTVadsyK/viee7cmeqhx2p1BsWCt8T5JEww7v1senJM8oTZW2WCaai5WtWEJiAm0s08OH9lgK+fY5ll8naCNOXcJF0Uqw0PFfipn/8wyjP7sEZyJeRxwMrDReRvtAYhrhVi73tMFAAE0XfBSYl0fojSwI+VJhdA6O7NCQ==","id":9},{"domain":"copilot.microsoft.com","expirationDate":1738767251.300601,"hostOnly":true,"httpOnly":false,"name":"MUID","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"0253A33390726EF436A8B73791986F36","id":10},{"domain":"copilot.microsoft.com","expirationDate":1738771646.266151,"hostOnly":true,"httpOnly":true,"name":"MUIDB","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"0253A33390726EF436A8B73791986F36","id":11},{"domain":"copilot.microsoft.com","expirationDate":1722376509.649783,"hostOnly":true,"httpOnly":false,"name":"NAP","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"V=1.9&E=1cee&C=uZdnePvDK5ymDaO_JLec9qIm6KBF52NB8JlGYHKbKJ513v2Y0otzsQ&W=1","id":12},{"domain":"copilot.microsoft.com","expirationDate":1739631309.649802,"hostOnly":true,"httpOnly":false,"name":"PPLState","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"1","id":13},{"domain":"copilot.microsoft.com","expirationDate":1739631250.300958,"hostOnly":true,"httpOnly":false,"name":"SRCHD","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AF=NOFORM","id":14},{"domain":"copilot.microsoft.com","expirationDate":1739635274.539417,"hostOnly":true,"httpOnly":false,"name":"SRCHHPGUSR","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"SRCHLANG=zh-Hans&PV=12.6.0&BRW=W&BRH=M&CW=1432&CH=733&SCW=1432&SCH=733&DPR=2.0&UTC=480&DM=0&PRVCW=1432&PRVCH=733&CIBV=1.1418.9-suno","id":15},{"domain":"copilot.microsoft.com","expirationDate":1739631250.301005,"hostOnly":true,"httpOnly":false,"name":"SRCHUID","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"V=2&GUID=CD48F96ACE614913929052E57B3B07A8&dmnchg=1","id":16},{"domain":"copilot.microsoft.com","expirationDate":1739631251.649031,"hostOnly":true,"httpOnly":false,"name":"SRCHUSR","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"DOB=20240112&POEX=W","id":17},{"domain":"copilot.microsoft.com","expirationDate":1739631250.300912,"hostOnly":true,"httpOnly":true,"name":"USRLOC","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"HS=1","id":18},{"domain":"copilot.microsoft.com","expirationDate":1706280909.794725,"hostOnly":true,"httpOnly":true,"name":"WLID","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"nN+tlfaKPsUmPY0eUy7h4LjAOM+rPvUMmDYTPcZbDwHTfuSF18+9apnlwOBuX3kqDCnx177gVquU2+wwBh+Apv7YRq7fI3GSEVWcc65gq1I=","id":19},{"domain":"copilot.microsoft.com","hostOnly":true,"httpOnly":false,"name":"WLS","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"C=ddb6d8dd0d4367d3&N=S","id":20}]'


async def test_ask(query, incoming_message: ChatbotMessage, handler: dingtalk_stream.ChatbotHandler) -> None:
    bot = None
    try:
        # cookies = json.loads(open(
        #     str(Path(str(Path.cwd()) + "/bing_cookies.json")), encoding="utf-8").read())
        # cookies = json.loads(open("./bing_cookies.json", encoding="utf-8").read())
        cookies = json.loads(bing_cookies)
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

        if (msg.startswith('更换cookies=')):
            global bing_cookies
            bing_cookies = msg.removeprefix('更换cookies=')
            self.reply_text('更换成功', incoming_message)
            return AckMessage.STATUS_OK, 'OK'

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