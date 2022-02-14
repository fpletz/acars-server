from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from typing import Any, Optional, Generator
from pydantic import BaseModel
from enum import Enum
import uvicorn
import requests
import re

HOPPIE_URL = "http://www.hoppie.nl/acars/system/connect.html"

app = FastAPI()


class HoppieMessageType(Enum):
    PING = "ping"
    PROGRESS = "progress"
    CPDLC = "cpdlc"
    TELEX = "telex"
    POSREQ = "posreq"
    POSITION = "position"
    DATAREQ = "datareq"
    INFOREQ = "inforeq"
    POLL = "poll"
    PEEK = "peek"


class HoppieMessage(BaseModel):
    id: Optional[int]
    sender: str
    recipient: Optional[str]
    type: HoppieMessageType
    request: Optional[str]
    payload: Optional[str]

    def __str__(self) -> str:
        maybe_id = (str(self.id) + " ") if self.id is not None else ""
        return f"{{{maybe_id}{self.sender} {self.type.value} {{{self.get_packet()}}}}}"

    def get_packet(self) -> str:
        maybe_request = self.request or ""
        maybe_payload = self.payload or ""
        return (
            maybe_request
            + ("\n" if len(maybe_request) > 0 and len(maybe_payload) > 0 else "")
            + maybe_payload
        )


def hoppie_msgs_from_str(s: str) -> Generator[HoppieMessage, None, None]:
    for msg in re.finditer(r"{([0-9]+)? ?([^ ]+) ([^ ]+) {([^}]*)}}", s, re.DOTALL):
        print(msg)
        packet = msg.group(4).split("\n")
        assert len(packet) in (1, 2)
        yield HoppieMessage(
            id=int(msg.group(1)) if msg.group(1) is not None else None,
            sender=msg.group(2),
            type=msg.group(3),
            request=packet[0] if len(packet) == 2 else None,
            payload=packet[1] if len(packet) == 2 else packet[0],
        )


def hoppie_request(logon: str, msg: HoppieMessage) -> requests.Response:
    return requests.get(
        f"{HOPPIE_URL}?logon={logon}&type={msg.type.value}&"
        + f"from={msg.sender}&to={msg.recipient}&packet={msg.get_packet()}"
    )


def forward_to_hoppie(logon: str, msg: HoppieMessage) -> PlainTextResponse:
    req = hoppie_request(logon, msg)
    return PlainTextResponse(status_code=req.status_code, content=req.text)


@app.get("/hoppie/connect", response_class=PlainTextResponse)
@app.post("/hoppie/connect", response_class=PlainTextResponse)
async def hoppie_connect(
    logon: str,
    type: HoppieMessageType,
    sender: str = Query(None, alias="from"),
    recipient: str = Query(None, alias="to"),
    packet: Optional[str] = None,
) -> Any:
    msg = HoppieMessage(sender=sender, recipient=recipient, type=type, request=packet)
    print(str(msg))
    print(repr(msg))
    if type == HoppieMessageType.PING:
        if packet != "ALL-CALLSIGNS":
            return "ok"
        else:
            return forward_to_hoppie(logon, msg)
    elif type in (HoppieMessageType.CPDLC, HoppieMessageType.TELEX):
        return forward_to_hoppie(logon, msg)
    elif type in (HoppieMessageType.PEEK, HoppieMessageType.POLL):
        req = hoppie_request(logon, msg)
        if req.text.startswith("ok"):
            msgs = hoppie_msgs_from_str(req.text)
            for msg in msgs:
                print(str(msg))
                print(repr(msg))
        else:
            return "fail"
        return req.text
    elif type in (
        HoppieMessageType.INFOREQ,
        HoppieMessageType.PROGRESS,
        HoppieMessageType.POSREQ,
        HoppieMessageType.POSITION,
    ):
        return forward_to_hoppie(logon, msg)
    elif type == HoppieMessageType.DATAREQ:
        # WTF, fileupload?!
        return PlainTextResponse(status_code=500, content="notimplemented")


def run() -> None:
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))
    server.run()
