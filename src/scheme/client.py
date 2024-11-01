from dataclasses import dataclass


@dataclass
class ClientInfo:
    host: str
    agent: str
