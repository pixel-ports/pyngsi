import json

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime
from enum import Enum, unique
from loguru import logger

from pyngsi.sources.source import Source, Row
from pyngsi.sources.server import ServerHttpUpload
from pyngsi.sink import SinkOrion


@unique
class EntityId(Enum):
    ID = "id"
    PATTERN = "idPattern"


@unique
class EntityType(Enum):
    TYPE = "type"
    PATTERN = "typePattern"


@unique
class AttrsFormat(Enum):
    NORMALIZED = "normalized"
    KEYVALUES = "keyValues"
    VALUES = "values"


@dataclass
class Entity:
    id: Tuple[str, str] = None
    type: Tuple[str, str] = None


@dataclass
class Condition:
    attrs: list[str] = field(default_factory=list)
    expression: str = None


@dataclass
class Subject:
    entities: list[Entity] = field(default_factory=list)
    condition: Condition = Condition()


@dataclass
class Notification:
    url: str
    attrs: list[str] = field(default_factory=list)
    except_attrs: list[str] = field(default_factory=list)
    attrs_format: str = None


class Subscription:

    def __init__(self, description: str, notification_url: str):
        self.description: str = description
        self.subject: Subject = Subject()
        self.notification: Notification = Notification(notification_url)
        self.expires = None
        self.throttling = -1

    def _build_payload(self) -> dict:
        subject = {"entities": [], "condition": {}}
        notification = {"http": self.notification.url}
        for entity in self.subject.entities:
            if entity.type:
                subject["entities"].append(dict([entity.id, entity.type]))
            else:
                subject["entities"].append(dict([entity.id]))
        if self.subject.condition.attrs:
            subject["condition"]["attrs"] = self.subject.condition.attrs
        if self.subject.condition.expression:
            subject["condition"]["exceptAttrs"] = self.subject.condition.expression
        if self.notification.attrs:
            notification["attrs"] = self.notification.attrs
        if self.notification.except_attrs:
            notification["expect_attrs"] = self.notification.except_attrs
        if self.notification.attrs_format:
            notification["attrsFormat"] = self.notification.attrs_format
        payload = {}
        payload["description"] = self.description
        payload["subject"] = subject
        payload["notification"] = notification
        if self.expires:
            payload["expires"] = self.expires
        if self.throttling > 0:
            payload["throttling"] = self.throttling
        return payload

    def __repr__(self):
        return self._build_payload().__repr__()

    def json(self):
        return json.dumps(self._build_payload(), default=str, ensure_ascii=False)

    def pprint(self):
        print(json.dumps(self._build_payload(), default=str, indent=2))


class SubscriptionBuilder:

    def __init__(self, description: str, notification_url: str):
        if not description:
            print("description is mandatory")
        if not notification_url:
            print("notification url is mandatory")
        if not notification_url.startswith("http://") and not notification_url.startswith("https://"):
            print("bad scheme for notification url : must be http:// or https://")
        self._subscription = Subscription(description, notification_url)

    def add_subject_entity(self, id: Tuple[EntityId, str], type: Tuple[EntityType, str] = None):
        k, v = id
        if type:
            k2, v2 = type
            entity = Entity((k.value, v), (k2.value, v2))
        else:
            entity = Entity((k.value, v))
        self._subscription.subject.entities.append(entity)
        return self

    def add_subject_condition_attr(self, attr: str):
        if not attr:
            print("empty attr")
        self._subscription.subject.condition.attrs.append(attr)
        print(f"add attr {attr}")
        return self

    def set_subject_condition_expr(self, expr: str):
        if not expr:
            print("empty attr")
        self._subscription.subject.condition.expression = expr
        return self

    def add_notification_attr(self, attr: str):
        self._subscription.notification.attrs.append(attr)
        return self

    def add_notification_except_attr(self, attr: str):
        self._subscription.notification.except_attrs.append(attr)
        return self

    def set_notification_attr_format(self, format: AttrsFormat):
        self._subscription.notification.attrs_format = format.value
        return self

    def set_expires(self, expires: datetime):
        self._subscription.expires = expires
        return self

    def set_throttling(self, throttling: int):
        self._subscription.throttling = throttling
        return self

    def build(self):
        return self._subscription


class SourceOrion(ServerHttpUpload):

    def __init__(self):
        sink = SinkOrion(post_endpoint="/v2/subscriptions")
        self.src = Source

    def __iter__(self):
        pass  # TODO
