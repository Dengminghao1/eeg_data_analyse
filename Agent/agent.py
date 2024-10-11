from typing import Optional, Union, List, Dict
from WebSocket import WebSocketClient


class Assistant_Agent(object):
    def __init__(
            self,
            name: str,
            system_message: Optional[Union[str, List]] = "You are a helpful AI Assistant.",
            llm_config: Optional[Union[Dict]] = None,
            description: Optional[str] = None,

    ):
        self._name = name
        self._oai_system_message = [{"content": system_message, "name": name, "role": "system"}]
        self._description = description if description is not None else system_message

    def generate_reply(self):
        pass

    def send_message(self):
        WebSocketClient.process_and_respond()

    def receive_message(self):
        WebSocketClient.listen_to_server()


    def analyse_data(self):
        pass



