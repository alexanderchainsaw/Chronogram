from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InnerChronogramUserData:
    tg_uid: int
    utc_offset_minutes: int
    language: str
    joined: datetime = datetime.utcnow()
    subscription_deadline: Optional[datetime] = None
    subscription: bool = False
    notified_deadline: bool = False
    space_available: int = 250000
    space_taken: int = 0


@dataclass
class InnerChronogramPaymentData:
    timestamp: datetime
    user_id: int
    invoice_id: str
    tg_transaction_id: str
    xtr_amount: int
    type: str
    status: str = "processed"


@dataclass
class InnerTimeCapsuleData:
    user_id: int
    send_timestamp: datetime
    receive_timestamp: datetime
    text_content: bytes
    size: int
    received: bool = False
    image: Optional[bytearray] = None
    image_data: Optional[str] = None


@dataclass
class OuterChronogramUserData:
    tg_uid: int
    utc_offset_minutes: int
    language: str
    joined: datetime = datetime.utcnow()
    subscription_deadline: Optional[datetime] = None
    subscription: bool = False
    notified_deadline: bool = False
    space_available: int = 250000
    space_taken: int = 0

    def __post_init__(self) -> None:
        if self.language not in ("en", "ru"):
            raise ValueError(f"Unsupported language: {self.language}")


@dataclass
class OuterChronogramPaymentData:
    timestamp: datetime
    tg_uid: int
    invoice_id: str
    tg_transaction_id: str
    xtr_amount: int
    type: str
    status: str = "processed"

    def __post_init__(self) -> None:
        if self.type not in ("subscription", "donation"):
            raise ValueError(f"Unknown payment type: {self.type}")


@dataclass
class OuterTimeCapsuleData:
    tg_uid: int
    send_timestamp: datetime
    receive_timestamp: datetime
    text_content: str
    size: int
    received: bool = False
    image: Optional[bytearray] = None
    image_data: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.image and len(self.text_content) > 1600:
            raise ValueError(
                f"Text content length exceeds allowed 1600 for text-only: {len(self.text_content)}"
            )
        elif self.image and len(self.text_content) > 800:
            raise ValueError(
                f"Text content length exceeds allowed 800 for text with image: {len(self.text_content)}"
            )
