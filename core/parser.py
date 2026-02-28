import re, math
from datetime import datetime
from dataclasses import dataclass, field
from typing import List

@dataclass
class Message:
    timestamp: datetime
    sender:    str
    content:   str
    index:     int

@dataclass
class UserStats:
    name:                str
    messages:            List[Message] = field(default_factory=list)
    replies_triggered:   int  = 0
    unique_engagers:     set  = field(default_factory=set)
    conversation_starts: int  = 0
    questions_asked:     int  = 0
    questions_answered:  int  = 0
    code_snippets:       int  = 0
    links_shared:        int  = 0
    total_words:         int  = 0
    unique_words:        set  = field(default_factory=set)
    msg_embeddings:      list = field(default_factory=list)
    msg_types:           list = field(default_factory=list)
    sentiment_scores:    list = field(default_factory=list)
    response_latencies:  list = field(default_factory=list)

    @property
    def message_count(self): return len(self.messages)

    @property
    def avg_msg_len(self):
        return self.total_words / max(len(self.messages), 1)

    @property
    def vocab_richness(self):
        return len(self.unique_words) / math.sqrt(max(self.total_words, 1))

class WhatsAppParser:
    PATTERNS = [
        r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.*)',
        r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*[-–]\s*([^:]+):\s*(.*)',
    ]
    SYSTEM_TOKENS = [
        'end-to-end', 'added', 'removed', 'left', 'joined', 'created group',
        'security code', '<media omitted>', 'deleted this message',
        'null', 'missed voice call', 'missed video call', 'you deleted',
    ]
    DATE_FMTS = [
        '%d/%m/%Y %I:%M %p', '%d/%m/%Y %H:%M', '%d/%m/%y %I:%M %p', '%d/%m/%y %H:%M',
        '%m/%d/%Y %I:%M %p', '%m/%d/%Y %H:%M', '%d/%m/%Y %H:%M:%S', '%d/%m/%y %H:%M:%S',
    ]

    def parse(self, text: str) -> List[Message]:
        msgs, current, idx = [], None, 0
        for line in text.strip().split('\n'):
            p = self._try_parse(line, idx)
            if p:
                if current: msgs.append(current)
                current = p; idx += 1
            elif current:
                current.content += '\n' + line
        if current: msgs.append(current)
        return [m for m in msgs
                if not any(t in m.content.lower() for t in self.SYSTEM_TOKENS)]

    def _try_parse(self, line, idx):
        for pat in self.PATTERNS:
            m = re.match(pat, line.strip())
            if m:
                ds, ts, sender, content = m.groups()
                t = self._parse_ts(ds, ts)
                if t: return Message(t, sender.strip(), content.strip(), idx)
        return None

    def _parse_ts(self, ds, ts):
        combined = f"{ds} {ts}".strip()
        for fmt in self.DATE_FMTS:
            try: return datetime.strptime(combined, fmt)
            except: pass
        return None
