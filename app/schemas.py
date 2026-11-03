
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message"
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation ID"
    )


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    model: str


class MessageSchema(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None


class ConversationSchema(BaseModel):
    conversation_id: str
    created_at: datetime
    messages: List[MessageSchema] = []


class UsageResponse(BaseModel):
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_usd: float


class ReliabilityResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    failure_rate: float
    average_response_time: float


class ErrorResponse(BaseModel):
    detail: str
