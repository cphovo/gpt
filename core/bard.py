import json
import random
import re
import string
import requests


class Chatbot:
    """A class to interact with Google Bard.

    Args:
    - session_id: str, The __Secure-1PSID cookie.
    - proxy: str
    - timeout: int, Request timeout in seconds.
    - session: requests.Session, Requests session object.
    """

    __slots__ = [
        "headers",
        "_reqid",
        "SNlM0e",
        "conversation_id",
        "response_id",
        "choice_id",
        "proxy",
        "session_id",
        "session",
        "timeout",
    ]

    def __init__(
        self,
        session_id: str,
        proxy: dict = None,
        timeout: int = 20,
        session: requests.Session = None,
    ):
        headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
        self._reqid = int("".join(random.choices(string.digits, k=4)))
        self.proxy = proxy
        self.conversation_id = ""
        self.response_id = ""
        self.choice_id = ""
        self.session_id = session_id
        self.session = session or requests.Session()
        self.session.headers = headers
        self.session.cookies.set("__Secure-1PSID", session_id)
        self.SNlM0e = self.__get_snlm0e()
        self.timeout = timeout

    def __get_snlm0e(self):
        if not self.session_id or self.session_id[-1] != ".":
            raise Exception(
                "__Secure-1PSID value must end with a single dot. Enter correct __Secure-1PSID value."
            )
        resp = self.session.get(
            "https://bard.google.com/", timeout=10, proxies=self.proxy
        )
        if resp.status_code != 200:
            raise Exception(
                f"Response code not 200. Response Status is {resp.status_code}"
            )
        SNlM0e = re.search(r"SNlM0e\":\"(.*?)\"", resp.text)
        if not SNlM0e:
            raise Exception(
                "SNlM0e value not found in response. Check __Secure-1PSID value."
            )
        return SNlM0e.group(1)

    def ask(self, message: str) -> dict:
        """Send a message to Google Bard and return the response."""
        # url params
        params = {
            "bl": "boq_assistant-bard-web-server_20230523.13_p0",
            "_reqid": str(self._reqid),
            "rt": "c",
        }

        # message arr -> data["f.req"]. Message is double json stringified
        message_struct = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        data = {
            "f.req": json.dumps([None, json.dumps(message_struct)]),
            "at": self.SNlM0e,
        }
        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=self.timeout,
            proxies=self.proxy,
        )
        chat_data = json.loads(resp.content.splitlines()[3])[0][2]
        if not chat_data:
            return {"content": f"Google Bard encountered an error: {resp.content}."}
        json_chat_data = json.loads(chat_data)
        images = set()
        if len(json_chat_data) >= 3:
            if len(json_chat_data[4][0]) >= 4:
                for img in json_chat_data[4][0][4]:
                    images.add(img[0][0][0])
        results = {
            "content": json_chat_data[0][0],
            "conversation_id": json_chat_data[1][0],
            "response_id": json_chat_data[1][1],
            "factualityQueries": json_chat_data[3],
            "textQuery": json_chat_data[2][0] if json_chat_data[2] is not None else "",
            "choices": [{"id": i[0], "content": i[1]} for i in json_chat_data[4]],
            "images": images,
        }
        self.conversation_id = results["conversation_id"]
        self.response_id = results["response_id"]
        self.choice_id = results["choices"][0]["id"]
        self._reqid += 100000
        return results


if __name__ == "__main__":
    print("Welcome to Google Bard Chatbot!")
