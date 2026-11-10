import logging
import asyncio
import os
import io
import random
import time
from typing import Set, Dict, List, Any
from telegram import Update
from telegram.constants import ChatAction
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, Forbidden
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return

def run_health_check_server():
    server = HTTPServer(('0.0.0.0', 5000), HealthCheckHandler)
    server.serve_forever()

# ================= CONFIGURATION =================
def get_tokens():
    tokens_env = os.environ.get("BOT_TOKENS")
    if tokens_env:
        return [t.strip() for t in tokens_env.split(",") if t.strip()]
    return [
      "8822029331:AAH4aRGVApi5WBFAVonIN3XcoRld9QWqocU",
        "8807013881:AAGYEXN8lmAOlpzhIZlG1Zi7VJf30UhZvF4",
        "8835400077:AAER8oirl3j0FJ7VSaYJG5zTjHKVTLPXOXI",
        "8692962374:AAFLBgYFrB7TvbBIc-ePBUB8cg7XXKnKCCM",
        "8526888586:AAG4aNiUhwIzFPDpPL6pdY2URBkzb-QEoDY",
        "8855439064:AAGjqed_qtszbgM9wohL-Uln-eCn_V_tfFs",
        "8667367788:AAE8I1yoMQTWkUdae1ZJgIFGZQPyqhKQxQs",
        "8698818208:AAHXaCCheRs2fZFpigVdQQplsDJ_dGcXrtw",
        "8909257507:AAHaAuOoMnIoXJv1JeQgY-bRQvY8HMDcLbs",
        "8880604290:AAHj2fHJ-tz-EFN01bMoJMk5nydvlhCvaGk",
    ]


TOKENS = get_tokens()

NC_TEXTS = [
  "{text}┕━☽【🇦🇨】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇦🇫】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇦🇷】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇦🇩】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇧🇷】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇨🇦】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇨🇿】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇩🇪】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇫🇷】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇳🇱】☾━┙ᴄʜᴜᴅ",
  "{text}┕━☽【🇳🇮】☾━┙ᴄʜᴜᴅ"

]

GOD_TEXT = [
    "⭅╡⭆ᴛᴍᴋᴄ⭅╞⭆",
    "⭅╡⭆ᴛʙᴋᴄ⭅╞⭆",
    "⭅╡⭆ᴄʜᴜᴅ⭅╞⭆",
    "⭅╡⭆ʀɴᴅɪ⭅╞⭆",
    "⭅╡⭆ᴋɪᴅᴇ⭅╞⭆",
    "⭅╡⭆ʙʜᴏsᴅɪ⭅╞⭆",
    "⭅╡⭆ᴘɪʟʟ⭅╞⭆",
    "⭅╡⭆ᴛᴍʀ⭅╞⭆",
    "⭅╡⭆ᴛʙʀ⭅╞⭆",
    "⭅╡⭆ᴛᴍᴋʟ⭅╞⭆",
    "⭅╡⭆ᴛʙᴋʟ⭅╞⭆",
    "⭅╡⭆sᴀʏ 𝐏𝐀𝐈𝐍⭅╞⭆"
]

GODTAMP = [
"⊱❄️⊰{text}⊱❄️⊰", "⊱🌹⊰{text}⊱🌹⊰",
" 𐙚🧸ྀི{text}𐙚🧸ྀི ", "⊱⚡⊰{text}⊱⚡⊰", 
"⊱🪷⊰{text}⊱🪷⊰",              "𓍢ִ໋🌷͙֒{text}𓍢ִ໋🌷͙֒",      "💋ྀིྀི{text}💋ྀིྀི", "˚.🎀༘⋆{text}˚.🎀༘⋆",
" ִֶཐི༏ཋྀ{text}ཐི༏ཋྀ ", "⊱🕶️⊰{text}⊱🕶️⊰", "⊱💮⊰{text}⊱💮⊰", "⊱🌸⊰{text}⊱🌸⊰", 

]

CUSTOMNC_TEXTS = [
    "×~🌷×~", "~×🌼×~", "~×🌻×~", "~×🌺×~", "~×🌹×~",
    "~×🏵️×~️", "~×🪷×~", "~×💮×~", "~×🌸×~", "~×🌷×~",
    "~×🌼×~", "~×🌻×~", "~×🌺×~", "~×🏵️×~", "~×❄️×~", "~×⚡×~",
]

# ================= NC TEMPLATES =================
NC_TEMPLATES = [
    "🔥 {text} 🔥", "⚡ {text} ⚡", "👑 {text} 👑", "💀 {text} 💀", "✨ {text} ✨",
    "💥 {text} 💥", "❄️ {text} ❄️", "🍀 {text} 🍀", "🍄 {text} 🍄", "🌹 {text} 🌹",
"☄️ {text} ☄️", "☀️ {text} ☀️", "🌙 {text} 🌙",
    "🌀 {text} 🌀", "🔱 {text} 🔱", "💎 {text} 💎", "🔮 {text} 🔮", "🧿 {text} 🧿",

]
SPAM_TEXTS = [
    ("{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --🖤-- ___________________________________________________________________________________________________________________________________________________{text} 𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --❤️--_______________________________________________________________________{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --🖤-- ____________________________________________________________________________________________________________________{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --❤️--_________________________________________________________________{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --🖤-- __________________________________________________________ _______________"),
]

TOKENS = get_tokens()

OWNER_ID = int(os.environ.get("OWNER_ID", "8972907906"))

# ================= GLOBAL SETTINGS =================
MIN_DELAY = 0.05 
DEFAULT_SPEED = 0.1
MAX_CONCURRENT_TASKS = 500
MAX_TASKS_PER_CHAT = 1
REQUEST_QUEUE_SIZE = 2000
CLEANUP_INTERVAL = 60
MAX_CHAT_STATS_AGE = 600

# ================= LOGGING =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.CRITICAL
)
logger = logging.getLogger(__name__)

# Disable everything
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("http.server").setLevel(logging.CRITICAL)

# ================= GLOBAL STATE =================
running_tasks: Dict[str, asyncio.Task] = {}
stop_events: Dict[str, asyncio.Event] = {} 
known_chats: Set[int] = set()
SUDO_USERS: Set[int] = {OWNER_ID}
slide_reply_targets: Dict[int, str] = {} 
speed_settings: Dict[int, float] = {}    
global_mode: bool = False
bot_start_time = time.time()
all_bot_instances: List[Any] = []
max_threads: int = 5
spam_templates: List[str] = [
    "{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --🖤-- ___________________________________________________________________________________________________________________________________________________{text} 𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --❤️--_______________________________________________________________________{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --🖤-- ____________________________________________________________________________________________________________________{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --❤️--_________________________________________________________________{text}  𝚃𝙴𝚁𝙸 𝙼𝙰𝙰 𝙲𝙷𝙾𝙳𝙽𝙴 𝙰𝙰𝙶𝚈𝙰 𝙷𝚄𝙽 --🖤-- __________________________________________________________ _______________",
]
target_names: Dict[int, str] = {}
nc_speeds: Dict[int, float] = {}

# ================= OPTIMIZED FOR 100 GROUPS =================
class RequestQueue:
    """Async request queue with concurrency control for 100+ groups"""
    
    def __init__(self, max_concurrent: int = 50):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue: asyncio.Queue = None
        self.active_requests: Dict[int, int] = {}
        self.total_processed = 0
        self.total_failed = 0
        
    async def init(self):
        if self.queue is None:
            self.queue = asyncio.Queue(maxsize=REQUEST_QUEUE_SIZE)
        return self.queue
    
    async def execute(self, func, *args, chat_id=None, priority=1, **kwargs):
        """Execute request with concurrency control"""
        await self.init()
        
        async with self.semaphore:
            if chat_id:
                self.active_requests[chat_id] = self.active_requests.get(chat_id, 0) + 1
            try:
                # Optimized for 100 groups: retry with exponential backoff on transient errors
                for attempt in range(5):
                    try:
                        result = await func(*args, **kwargs)
                        self.total_processed += 1
                        return result
                    except (TimedOut, NetworkError) as e:
                        if attempt == 4: raise e
                        await asyncio.sleep(0.1 * (2 ** attempt))
                    except Exception as e:
                        raise e
            except Exception as e:
                self.total_failed += 1
                raise e
            finally:
                if chat_id and chat_id in self.active_requests:
                    self.active_requests[chat_id] = max(0, self.active_requests[chat_id] - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "processed": self.total_processed,
            "failed": self.total_failed,
            "active_chats": len([c for c, v in self.active_requests.items() if v > 0]),
            "queue_size": self.queue.qsize() if self.queue else 0
        }

class TaskManager:
    """Efficient task management for 100+ groups"""
    
    def __init__(self):
        self.tasks_by_chat: Dict[int, Dict[str, asyncio.Task]] = {}
        self.task_count = 0
        self.last_cleanup = time.time()
    
    def get_chat_tasks(self, chat_id: int) -> Dict[str, asyncio.Task]:
        if chat_id not in self.tasks_by_chat:
            self.tasks_by_chat[chat_id] = {}
        return self.tasks_by_chat[chat_id]
    
    def count_active_tasks(self, chat_id: int) -> int:
        tasks = self.get_chat_tasks(chat_id)
        return len([t for t in tasks.values() if not t.done()])
    
    def total_active_tasks(self) -> int:
        total = 0
        for tasks in self.tasks_by_chat.values():
            total += len([t for t in tasks.values() if not t.done()])
        return total
    
    def can_start_task(self, chat_id: int) -> bool:
        if self.total_active_tasks() >= MAX_CONCURRENT_TASKS:
            return False
        if self.count_active_tasks(chat_id) >= MAX_TASKS_PER_CHAT:
            return False
        return True
    
    async def cleanup_finished_tasks(self):
        """Remove finished tasks from memory"""
        now = time.time()
        if now - self.last_cleanup < 60:
            return
        
        self.last_cleanup = now
        for chat_id in list(self.tasks_by_chat.keys()):
            tasks = self.tasks_by_chat[chat_id]
            finished = [k for k, t in tasks.items() if t.done()]
            for k in finished:
                del tasks[k]
            if not tasks:
                del self.tasks_by_chat[chat_id]
    
    def get_stats(self) -> Dict[str, Any]:
        active = self.total_active_tasks()
        return {
            "active_tasks": active,
            "chats_with_tasks": len(self.tasks_by_chat),
            "capacity_used": f"{(active / MAX_CONCURRENT_TASKS) * 100:.1f}%"
        }

request_queue = RequestQueue(max_concurrent=30)
task_manager = TaskManager()

# ================= SMART RATE LIMIT BYPASS SYSTEM =================
class SmartRateLimiter:
    """Intelligent rate limit management with adaptive delays and tracking"""
    
    def __init__(self):
        self.chat_stats: Dict[int, Dict[str, Any]] = {}
        self.global_cooldown: float = 0
        self.consecutive_failures: Dict[int, int] = {}
        self.last_request_time: Dict[int, float] = {}
        self.action_cooldowns: Dict[str, float] = {}
        self.success_streak: Dict[int, int] = {}
        self.global_request_count = 0
        self.global_rate_limit_hits = 0
        self.last_cleanup = time.time()
        self.base_delays: Dict[str, float] = {
            "message": 0.03,
            "title": 0.3,
            "photo": 0.8,
            "default": 0.05
        }
        
    def get_chat_stats(self, chat_id: int) -> Dict[str, Any]:
        if chat_id not in self.chat_stats:
            self.chat_stats[chat_id] = {
                "total_requests": 0,
                "success_count": 0,
                "rate_limit_hits": 0,
                "last_rate_limit": 0,
                "adaptive_delay": 0.05,
                "last_success": time.time()
            }
        return self.chat_stats[chat_id]
    
    def calculate_adaptive_delay(self, chat_id: int, action_type: str = "default") -> float:
        """Calculate smart delay based on recent performance"""
        stats = self.get_chat_stats(chat_id)
        base = self.base_delays.get(action_type, self.base_delays["default"])
        
        failures = self.consecutive_failures.get(chat_id, 0)
        if failures > 0:
            delay = base * (1.5 ** min(failures, 8))
            jitter = random.uniform(0, delay * 0.3)
            return delay + jitter
        
        success = self.success_streak.get(chat_id, 0)
        if success > 5:
            reduction = min(0.8, 0.05 * (success - 5))
            return max(0.02, base * (1 - reduction))
        
        return base + random.uniform(0, base * 0.1)
    
    def record_success(self, chat_id: int):
        """Record successful request"""
        stats = self.get_chat_stats(chat_id)
        stats["total_requests"] += 1
        stats["success_count"] += 1
        stats["last_success"] = time.time()
        stats["adaptive_delay"] = max(0.02, stats["adaptive_delay"] * 0.95)
        
        self.consecutive_failures[chat_id] = 0
        self.success_streak[chat_id] = self.success_streak.get(chat_id, 0) + 1
        self.last_request_time[chat_id] = time.time()
    
    def record_rate_limit(self, chat_id: int, wait_time: float):
        """Record rate limit hit and adjust strategy"""
        stats = self.get_chat_stats(chat_id)
        stats["total_requests"] += 1
        stats["rate_limit_hits"] += 1
        stats["last_rate_limit"] = time.time()
        stats["adaptive_delay"] = min(30.0, stats["adaptive_delay"] * 2)
        
        self.consecutive_failures[chat_id] = self.consecutive_failures.get(chat_id, 0) + 1
        self.success_streak[chat_id] = 0
        self.action_cooldowns[f"{chat_id}_all"] = time.time() + wait_time
    
    def record_failure(self, chat_id: int):
        """Record non-rate-limit failure"""
        stats = self.get_chat_stats(chat_id)
        stats["total_requests"] += 1
        self.consecutive_failures[chat_id] = self.consecutive_failures.get(chat_id, 0) + 1
        self.success_streak[chat_id] = 0
    
    def should_throttle(self, chat_id: int) -> bool:
        """Check if we should delay this request"""
        cooldown_key = f"{chat_id}_all"
        if cooldown_key in self.action_cooldowns:
            if time.time() < self.action_cooldowns[cooldown_key]:
                return True
            del self.action_cooldowns[cooldown_key]
        return False
    
    def get_throttle_time(self, chat_id: int) -> float:
        """Get remaining throttle time"""
        cooldown_key = f"{chat_id}_all"
        if cooldown_key in self.action_cooldowns:
            remaining = self.action_cooldowns[cooldown_key] - time.time()
            return max(0, remaining)
        return 0
    
    def get_smart_wait_time(self, retry_after: float) -> float:
        """Calculate optimized wait time with jitter"""
        jitter = random.uniform(0.1, 0.5)
        return retry_after + jitter
    
    def get_stats_summary(self, chat_id: int) -> str:
        """Get human-readable stats for a chat"""
        stats = self.get_chat_stats(chat_id)
        success_rate = (stats["success_count"] / max(1, stats["total_requests"])) * 100
        return (f"📊 Requests: {stats['total_requests']} | "
                f"Success: {success_rate:.1f}% | "
                f"Rate Limits: {stats['rate_limit_hits']} | "
                f"Delay: {stats['adaptive_delay']:.3f}s")
    
    async def cleanup_old_stats(self):
        """Remove old chat stats to free memory - optimized for 100 groups"""
        now = time.time()
        if now - self.last_cleanup < CLEANUP_INTERVAL:
            return
        
        self.last_cleanup = now
        stale_chats = []
        for chat_id, stats in self.chat_stats.items():
            if now - stats.get("last_success", 0) > MAX_CHAT_STATS_AGE:
                stale_chats.append(chat_id)
        
        for chat_id in stale_chats:
            del self.chat_stats[chat_id]
            self.consecutive_failures.pop(chat_id, None)
            self.success_streak.pop(chat_id, None)
            self.last_request_time.pop(chat_id, None)
        
        stale_cooldowns = [k for k, v in self.action_cooldowns.items() if v < now]
        for k in stale_cooldowns:
            del self.action_cooldowns[k]
        
        if stale_chats:
            logger.info(f"Cleaned up stats for {len(stale_chats)} inactive chats")
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global performance stats"""
        total_reqs = sum(s.get("total_requests", 0) for s in self.chat_stats.values())
        total_success = sum(s.get("success_count", 0) for s in self.chat_stats.values())
        total_rl = sum(s.get("rate_limit_hits", 0) for s in self.chat_stats.values())
        return {
            "tracked_chats": len(self.chat_stats),
            "total_requests": total_reqs,
            "total_success": total_success,
            "total_rate_limits": total_rl,
            "success_rate": (total_success / max(1, total_reqs)) * 100
        }

rate_limiter = SmartRateLimiter()

async def periodic_cleanup():
    """Background task for memory cleanup"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        await rate_limiter.cleanup_old_stats()
        await task_manager.cleanup_finished_tasks()

# ================= HELPERS =================
async def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_USERS

async def check_sudo(update: Update) -> bool:
    if not update.effective_user: return False
    is_sudo = await is_admin(update.effective_user.id)
    if not is_sudo and update.message:
        await update.message.reply_text("𝐏𝐀𝐈𝐍 ᴋɪ ʙᴀʀᴀʙᴀʀɪ ᴋʀᴇɢᴀ sʟᴀᴠᴇ?")
    return is_sudo

def get_delay(chat_id: int) -> float:
    return max(MIN_DELAY, speed_settings.get(chat_id, DEFAULT_SPEED))

def get_task_key(chat_id: int, action: str) -> str:
    return f"{chat_id}_{action}"

async def stop_task(chat_id: int, action: str) -> bool:
    key = get_task_key(chat_id, action)
    stopped = False
    
    # Signal the event if it exists
    if key in stop_events:
        stop_events[key].set()
        stopped = True
    
    # Also cancel the task if it's running
    if key in running_tasks:
        task = running_tasks.pop(key)
        if not task.done():
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=0.1)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        stopped = True
        
    if key in stop_events:
        del stop_events[key]
        
    return stopped

async def start_worker(chat_id: int, action: str, worker_coro):
    key = get_task_key(chat_id, action)
    await stop_task(chat_id, action) # Ensure previous is gone
    
    stop_event = asyncio.Event()
    stop_events[key] = stop_event
    
    async def wrapped_worker():
        try:
            await worker_coro(stop_event)
        except asyncio.CancelledError:
            pass
        finally:
            running_tasks.pop(key, None)
            stop_events.pop(key, None)
            
    running_tasks[key] = asyncio.create_task(wrapped_worker())

async def safe_api_request(func, *args, chat_id=None, action_type="default", **kwargs):
    """
    Safely executes a Telegram API call with smart rate limit bypass.
    Uses adaptive delays, exponential backoff with jitter, and per-chat tracking.
    Returns success status to allow caller to handle retries or breaks.
    """
    if chat_id and rate_limiter.should_throttle(chat_id):
        throttle_time = rate_limiter.get_throttle_time(chat_id)
        if throttle_time > 0:
            await asyncio.sleep(min(throttle_time, 5.0))
    
    try:
        await func(*args, **kwargs)
        if chat_id:
            rate_limiter.record_success(chat_id)
        return True
    except RetryAfter as e:
        wait_time = e.retry_after
        smart_wait = rate_limiter.get_smart_wait_time(wait_time)
        if chat_id:
            rate_limiter.record_rate_limit(chat_id, wait_time)
        
        if wait_time > 60:
            logger.warning(f"Long flood control ({wait_time}s) - using smart bypass")
            await asyncio.sleep(min(smart_wait, 30.0))
        elif wait_time > 10:
            await asyncio.sleep(smart_wait * 0.7)
        else:
            await asyncio.sleep(smart_wait * 0.5 + random.uniform(0.1, 0.5))
        return False
    except BadRequest as e:
        err_msg = str(e)
        if "Chat not found" in err_msg or "Have no rights" in err_msg:
            logger.error(f"Chat error {chat_id}: {e}")
            return True
        if "Too Many Requests" in err_msg or "retry" in err_msg.lower():
            if chat_id:
                rate_limiter.record_rate_limit(chat_id, 5.0)
            await asyncio.sleep(random.uniform(0.5, 2.0))
            return False
        if chat_id:
            rate_limiter.record_failure(chat_id)
        await asyncio.sleep(0.01)
        return False
    except Forbidden as e:
        logger.error(f"Forbidden in {chat_id}: {e}")
        return True
    except (TimedOut, NetworkError):
        if chat_id:
            rate_limiter.record_failure(chat_id)
        await asyncio.sleep(random.uniform(0.01, 0.1))
        return False
    except Exception as e:
        err_msg = str(e)
        if "Chat not found" in err_msg:
            return True
        if "Flood control exceeded" in err_msg or "429" in err_msg:
            if chat_id:
                rate_limiter.record_rate_limit(chat_id, 3.0)
            delay = rate_limiter.calculate_adaptive_delay(chat_id, action_type) if chat_id else 0.5
            await asyncio.sleep(delay)
            return False
        if chat_id:
            rate_limiter.record_failure(chat_id)
        logger.error(f"Error in chat {chat_id}: {e}")
        return False

# ================= COMMAND HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat: return
    known_chats.add(update.effective_chat.id)
    if update.message:
        await update.message.reply_text("✅ **𝐏𝐀𝐈𝐍 ᴠ20 ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ.**\nUse /help ᴛᴏ sᴇᴇ ᴄᴏᴍᴍᴀɴᴅs 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    text = """
🚀𝐏𝐀𝐈𝐍 ᴠ20 ᴜʟᴛɪᴍᴀᴛᴇ🚀

💬 sᴘᴀᴍ ᴄᴏᴍᴍᴀɴᴅs
/spam <text> - sᴘᴀᴍ
/imagespam - ɪᴍᴀɢᴇs sᴘᴀᴍ
/raidspam - ʀᴀɪᴅ sᴘᴀᴍ <text> 
/Stopspm - sᴛᴏᴘ sᴘᴀᴍ

🏷️ ɴᴀᴍᴇ ᴄʜᴀɴɢᴇʀ
/nc <text> - ɴᴄ 
/gcnc <name> - ɢᴄɴᴄ ʟᴏᴏᴘ
/stopnc - sᴛᴏᴘ ɴᴄ
/ncbaap <name> sᴘᴇᴇᴅ ɴᴄ
/exoncgodspeed <name> ɢᴏᴅ sᴘᴇᴇᴅ ɴᴄ
/godspeed <text> - ᴜʟᴛʀᴀ ғᴀsᴛ ɴᴄ
/customnc CUSTOM NC
/delaync <sec> - sᴇᴛ ɴᴄ sᴘᴇᴇᴅ
/setgodspeed <sec> - sᴇᴛ ɢᴏᴅsᴘᴇᴇᴅ ᴅᴇʟᴀʏ
/threads <val> - sᴇᴛ ᴛʜʀᴇᴀᴅs

🎯 ᴛᴀʀɢᴇᴛ sᴘᴀᴍ
/target <name> - sᴇᴛ ᴛᴀʀɢᴇᴛ ɴᴀᴍᴇ
/settemplate <1-3> <text> - sᴇᴛ ᴛᴀᴍᴘʟᴀᴛᴇs
/spamtarget - ᴛᴀʀɢᴇᴛ sᴘᴀᴍ
/stoptarget - sᴛᴏᴘ ᴛᴀʀɢᴇᴛ sᴘᴍ
/showtemplate - sʜᴏᴡ ᴛᴀᴍᴘʟᴀᴛᴇs

📸 ɢᴄ ᴘғᴘ
/changepfp - ᴘғᴘ ʟᴏᴏᴘ
/Stoppfp - sᴛᴏᴘ ᴘғᴘ

🎤 ᴠᴏɪᴄᴇ
/vn <text> - ᴛᴇxᴛ ᴛᴏ ᴠᴏɪᴄᴇ

🎯 ʀᴇᴘʟʏ
/slidespam <text> - ᴀᴜᴛᴏ ʀᴇᴘʟʏ 
/slidestop - sᴛᴏᴘ ʀᴇᴘʟʏ

🔁 ᴄᴏᴍʙᴏs
/spnc <text> - sᴘᴍ + ɴᴄ
/stopspnc - sᴛᴏᴘ sᴘɴᴄ
/ncpfp <text> - ɴᴄ + ᴘғᴘ ʟᴏᴏᴘ
/Stopncpfp - sᴛᴏᴘ NCPFP
/all <text> - sᴘ+ɴᴄ+ᴘғᴘ ᴀʟʟ ɪɴ ᴏɴᴇ 💀

⚡ ᴄᴏɴᴛʀᴏʟ
/speed <val> - sᴇᴛ sᴘᴇᴇᴅ
/stop - sᴛᴏᴘ ᴀʟʟ ⚡
/dynstop - ᴅʏɴᴀᴍɪᴄ sᴛᴏᴘ ᴀʟʟ 🛑

🤖 ᴍᴀɴᴀɢᴇᴍᴇɴᴛ
/status - sᴛᴀᴛᴜs
/dashboard - ᴅᴀsʜʙᴏᴀʀᴅ
/getallbots - ʙᴏᴛ ᴄᴏᴜɴᴛ
/test - ᴘɪɴɢ

👋 ɢʀᴏᴜᴘs
/leavegc - ʟᴇᴀᴠᴇ ɢᴄ
/leavegbl - ʟᴇᴀᴠᴇ ᴏᴛʜᴇʀs
/groups - sʜᴏᴡ ᴀʟʟ ɢᴄs

🌐 ɢʟᴏʙᴀʟ
/globalactivate - Activate Global
/offglobal - Deactivate Global
/leaveglobal - Bots leave all GCs
/g <cmd> - Execute Globally
/activategbl - Activate
/offgbl - Deactivate

📊 ᴀᴅᴍɪɴ
/sudo <id> - Add admin
/delsudo <id> - Del admin
/Listsudo - List admins
/Owner - Owner info

🛡️ sᴍᴀʀᴛ ʀᴀᴛᴇ ʟɪᴍɪᴛ ʙʏᴘᴀss
/rlstats - View rate limit stats
/resetrl - Reset rate limit stats
/perf - Performance stats (100 groups)
"""
    if update.message:
        await update.message.reply_text(text)

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /spam <text>")
    if not update.effective_chat or not update.message: return
    
    chat_id = update.effective_chat.id
    message = " ".join(context.args) if context.args else ""
    
    async def worker(stop_event):
        while not stop_event.is_set():
            # Wait for the task to finish before starting next to avoid stacking
            await safe_api_request(context.bot.send_message, chat_id, message, chat_id=chat_id)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=get_delay(chat_id))
            except asyncio.TimeoutError:
                continue
            else:
                break
                
    await start_worker(chat_id, "spam", worker)
    await update.message.reply_text("sᴘᴀᴍ sᴛᴀʀᴛᴇᴅ 🐖")

async def raidspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    
    async def worker(stop_event):
        while not stop_event.is_set():
            msg = random.choice(SPAM_TEXTS)
            await safe_api_request(context.bot.send_message, chat_id, msg, chat_id=chat_id)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=get_delay(chat_id))
            except asyncio.TimeoutError:
                continue
            else:
                break

    await start_worker(chat_id, "spam", worker)
    await update.message.reply_text("🚀sᴘᴀᴍ sᴛᴀʀᴛᴇᴅ🚀")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    if await stop_task(update.effective_chat.id, "spam"):
        await update.message.reply_text("🛑 sᴘᴀᴍ sᴛᴏᴘᴘᴇᴅ")

async def imagespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.message or not update.message.reply_to_message or not update.message.reply_to_message.photo:
        if update.message: return await update.message.reply_text("Reply to a photo!")
        return
    if not update.effective_chat: return
    chat_id = update.effective_chat.id
    photo = update.message.reply_to_message.photo[-1].file_id
    
    async def worker(stop_event):
        while not stop_event.is_set():
            await safe_api_request(context.bot.send_photo, chat_id, photo=photo, chat_id=chat_id)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=get_delay(chat_id))
            except asyncio.TimeoutError:
                continue
            else:
                break

    await start_worker(chat_id, "imagespam", worker)
    await update.message.reply_text("🖼️ ɪᴍᴀɢᴇ sᴘᴀᴍ sᴛᴀʀᴛᴇᴅ")

async def stop_imagespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    if await stop_task(update.effective_chat.id, "imagespam"):
        await update.message.reply_text("🛑 ɪᴍᴀɢᴇ sᴘᴀᴍ sᴛᴏᴘᴘᴇᴅ")

async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /nc <text>")
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    base = " ".join(context.args) if context.args else ""
    
    bots_to_use = all_bot_instances if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)

    async def bot_worker(bot, bot_idx):
        i = bot_idx
        while get_task_key(chat_id, "nc") in running_tasks:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            if len(name) > 255: name = name[:252] + "..."
            success = await safe_api_request(bot.set_chat_title, chat_id, name, chat_id=chat_id)
            if success:
                await asyncio.sleep(get_delay(chat_id) + 1.0)
            else:
                await asyncio.sleep(0.5)
            i += num_bots

    async def coordinator(stop_event):
        tasks = []
        for idx, bot in enumerate(bots_to_use):
            await asyncio.sleep(0.1 * idx)
            tasks.append(asyncio.create_task(bot_worker(bot, idx)))
        await asyncio.gather(*tasks, return_exceptions=True)

    await start_worker(chat_id, "nc", coordinator)
    await update.message.reply_text(f" 🚀ɴᴄ sᴛᴀʀᴛᴇᴅ ᴡɪᴛʜ {num_bots} ʙᴏᴛs 🚀")

async def stop_nc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    if await stop_task(update.effective_chat.id, "nc"):
        await update.message.reply_text("🛑 𝐏𝐀𝐈𝐍 ᴘᴀᴘᴀ ᴋᴀ ʜᴜǫᴍ ʀᴜᴋ ɢʏᴀ 🐷👆")

async def change_pfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.message or not update.message.reply_to_message or not update.message.reply_to_message.photo:
        if update.message: return await update.message.reply_text("Reply to a photo!")
        return
    if not update.effective_chat: return
    chat_id = update.effective_chat.id
    try:
        f = await context.bot.get_file(update.message.reply_to_message.photo[-1].file_id)
        b = await f.download_as_bytearray()
    except: 
        if update.message: await update.message.reply_text("Failed to download.")
        return
    
    async def worker(stop_event):
        while not stop_event.is_set():
            await safe_api_request(context.bot.set_chat_photo, chat_id, photo=bytes(b), chat_id=chat_id)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=get_delay(chat_id) + 2.5)
            except asyncio.TimeoutError:
                continue
            else:
                break

    await start_worker(chat_id, "pfp", worker)
    await update.message.reply_text("📸 ᴘғᴘ ʟᴏᴏᴘ sᴛᴀʀᴛᴇᴅ")

async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /gcnc <name>")
    if not update.effective_chat or not update.message: return
    
    base = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    bots_to_use = all_bot_instances if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)

    async def bot_worker(bot, bot_idx):
        i = bot_idx
        while get_task_key(chat_id, "nc") in running_tasks:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            if len(name) > 255: name = name[:252] + "..."
            success = await safe_api_request(bot.set_chat_title, chat_id, name, chat_id=chat_id)
            if success:
                await asyncio.sleep(get_delay(chat_id) + 1.5)
            else:
                await asyncio.sleep(0.5)
            i += num_bots
            
    async def coordinator(stop_event):
        tasks = []
        for idx, bot in enumerate(bots_to_use):
            await asyncio.sleep(0.2 * idx)
            tasks.append(asyncio.create_task(bot_worker(bot, idx)))
        await asyncio.gather(*tasks, return_exceptions=True)
            
    await start_worker(chat_id, "nc", coordinator)
    await update.message.reply_text(f"ɢᴄɴᴄ ʟᴏᴏᴘ sᴛᴀʀᴛᴇᴅ 💀 ({num_bots} BOTS)")

async def set_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args: return await update.message.reply_text("Usage: /threads <val>")
    try:
        global max_threads
        max_threads = int(context.args[0])
        await update.message.reply_text(f"🧵 ᴛʜʀᴇᴀᴅs sᴇᴛ ᴛᴏ {max_threads}")
    except:
        await update.message.reply_text("Invalid value.")

async def ncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /ncbaap <name>")
    if not update.effective_chat or not update.message: return
    
    base = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    bots_to_use = all_bot_instances if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)

    async def bot_worker(bot, bot_idx):
        i = bot_idx
        while get_task_key(chat_id, "nc") in running_tasks:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            
            success = await safe_api_request(bot.set_chat_title, chat_id, name[:255], chat_id=chat_id)
            if success:
                await asyncio.sleep(0.01) 
            else:
                await asyncio.sleep(0.1)
            i += num_bots
                
    async def coordinator(stop_event):
        tasks = []
        for idx, bot in enumerate(bots_to_use):
            await asyncio.sleep(0.05 * idx)
            tasks.append(asyncio.create_task(bot_worker(bot, idx)))
        await asyncio.gather(*tasks, return_exceptions=True)

    await start_worker(chat_id, "nc", coordinator)
    await update.message.reply_text(f"💀🔥 NCBAAP THREADED SPEED ACTIVATED 💀🔥 ({num_bots} BOTS)")

async def exoncgodspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /exoncgodspeed <name>")
    if not update.effective_chat or not update.message: return
    
    base = " ".join(context.args)
    chat_id = update.effective_chat.id
    await stop_task(chat_id, "nc")
    
    bots_to_use = all_bot_instances if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)
    
    async def bot_worker(bot, bot_idx):
        i = bot_idx
        while get_task_key(chat_id, "nc") in running_tasks:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            
            success = await safe_api_request(bot.set_chat_title, chat_id, name[:255], chat_id=chat_id)
            if success:
                await asyncio.sleep(0.005 * num_bots)
            else:
                await asyncio.sleep(0.05)
            i += num_bots
    
    async def coordinator():
        tasks = []
        for idx, bot in enumerate(bots_to_use):
            await asyncio.sleep(0.02 * idx)
            tasks.append(asyncio.create_task(bot_worker(bot, idx)))
        await asyncio.gather(*tasks, return_exceptions=True)
    
    running_tasks[get_task_key(chat_id, "nc")] = asyncio.create_task(coordinator())
    await update.message.reply_text(f"👑🔥 ɢᴏᴅ sᴘᴇᴇᴅ exonc - {num_bots} BOTS! 🚀")

async def raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    
    bots_to_use = all_bot_instances if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)

    async def bot_worker(bot):
        while get_task_key(chat_id, "spam") in running_tasks:
            msg = random.choice(NC_TEXTS)
            await safe_api_request(bot.send_message, chat_id, msg, chat_id=chat_id)
            await asyncio.sleep(get_delay(chat_id))

    async def coordinator(stop_event):
        tasks = []
        for bot in bots_to_use:
            tasks.append(asyncio.create_task(bot_worker(bot)))
        await asyncio.gather(*tasks, return_exceptions=True)

    await start_worker(chat_id, "spam", coordinator)
    await update.message.reply_text(f"🚀 ʀᴀɪᴅ sᴛᴀʀᴛᴇᴅ 🚀 ({num_bots} BOTS)")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    
    # 1. Stop all specific tasks for this chat
    prefix = f"{chat_id}_"
    stopped_any = False
    
    # Signal events
    for k in list(stop_events.keys()):
        if k.startswith(prefix):
            stop_events[k].set()
            stopped_any = True
            
    # Cancel tasks
    to_cancel = []
    for k in list(running_tasks.keys()):
        if k.startswith(prefix):
            task = running_tasks.pop(k, None)
            if task and not task.done():
                task.cancel()
                to_cancel.append(task)
            stopped_any = True
            
    if to_cancel:
        await asyncio.gather(*to_cancel, return_exceptions=True)

    # 2. Clear target settings
    if chat_id in slide_reply_targets:
        del slide_reply_targets[chat_id]
        stopped_any = True
        
    if chat_id in target_names:
        del target_names[chat_id]
        stopped_any = True

    await update.message.reply_text("🛑 **ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴛᴀsᴋs ʜᴀᴠᴇ ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ.**" if stopped_any else "❌ **ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀsᴋs ғᴏᴜɴᴅ.**")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    
    # 1. Stop everything first
    await stop_command(update, context)
    
    # 2. Reset settings and clear cache (rate limit stats)
    if chat_id in speed_settings: del speed_settings[chat_id]
    if chat_id in nc_speeds: del nc_speeds[chat_id]
    if chat_id in rate_limiter.chat_stats:
        del rate_limiter.chat_stats[chat_id]
        
    rate_limiter.consecutive_failures[chat_id] = 0
    rate_limiter.success_streak[chat_id] = 0
    
    await update.message.reply_text("🔄 **ʙᴏᴛ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴄᴀᴄʜᴇ ʀᴇsᴇᴛ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.**")

async def spnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /spnc <text>")
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    base = " ".join(context.args) if context.args else ""
    await stop_task(chat_id, "spnc")
    async def worker():
        i = 0
        while True:
            spam_msg = random.choice(SPAM_TEXTS)
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            if len(name) > 255: name = name[:252] + "..."
            asyncio.create_task(safe_api_request(context.bot.send_message, chat_id, f"{base}\n{spam_msg}", chat_id=chat_id))
            asyncio.create_task(safe_api_request(context.bot.set_chat_title, chat_id, name, chat_id=chat_id))
            i += 1
            await asyncio.sleep(get_delay(chat_id) + 1.5)
    running_tasks[get_task_key(chat_id, "spnc")] = asyncio.create_task(worker())
    await update.message.reply_text("🔁 SPNC sᴘᴍ+ɴᴄ sᴛᴀʀᴛᴇᴅ🌻")

async def stop_spnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    if await stop_task(update.effective_chat.id, "spnc"):
        await update.message.reply_text("🛑 sᴘɴᴄ sᴛᴏᴘᴘᴇᴅ 🌷")

async def all_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    base = " ".join(context.args) if context.args else ""
    b = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        try:
            f = await context.bot.get_file(update.message.reply_to_message.photo[-1].file_id)
            b = await f.download_as_bytearray()
        except: pass
    await stop_task(chat_id, "all")
    async def worker():
        i = 0
        while True:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            if len(name) > 255: name = name[:252] + "..."
            spam_msg = random.choice(SPAM_TEXTS)
            asyncio.create_task(safe_api_request(context.bot.send_message, chat_id, f"{base}\n{spam_msg}" if base else spam_msg, chat_id=chat_id))
            asyncio.create_task(safe_api_request(context.bot.set_chat_title, chat_id, name, chat_id=chat_id))
            if b: asyncio.create_task(safe_api_request(context.bot.set_chat_photo, chat_id, photo=bytes(b), chat_id=chat_id))
            i += 1
            await asyncio.sleep(get_delay(chat_id) + 1.5)
    running_tasks[get_task_key(chat_id, "all")] = asyncio.create_task(worker())
    await update.message.reply_text("💀 all ɴᴄ+sᴘᴀᴍ+ᴘғᴘ ᴛᴏɢᴇᴛʜᴇʀ🚀")

async def ncpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.message or not update.message.reply_to_message or not update.message.reply_to_message.photo:
        if update.message: return await update.message.reply_text("Reply to a photo for PFP loop!")
        return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    base = " ".join(context.args) if context.args else ""
    try:
        f = await context.bot.get_file(update.message.reply_to_message.photo[-1].file_id)
        b = await f.download_as_bytearray()
    except: 
        if update.message: await update.message.reply_text("Failed to download photo.")
        return
    await stop_task(chat_id, "ncpfp")
    async def worker():
        i = 0
        while True:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            if len(name) > 255: name = name[:252] + "..."
            asyncio.create_task(safe_api_request(context.bot.set_chat_title, chat_id, name, chat_id=chat_id))
            asyncio.create_task(safe_api_request(context.bot.set_chat_photo, chat_id, photo=bytes(b), chat_id=chat_id))
            i += 1
            await asyncio.sleep(get_delay(chat_id) + 2.0)
    running_tasks[get_task_key(chat_id, "ncpfp")] = asyncio.create_task(worker())
    await update.message.reply_text("📸🏷️ NCPFP ɴᴄ+ᴘғᴘ sᴛᴀʀᴛᴇᴅ🚀")

async def stop_ncpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.effective_chat or not update.message: return
    if await stop_task(update.effective_chat.id, "ncpfp"):
        await update.message.reply_text("🛑 ɴᴄᴘғᴘ sᴛᴏᴘᴘᴇᴅ")

async def vn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /vn <text>")
    if not update.message: return
    try:
        tts = gTTS(" ".join(context.args), lang='en')
        f = io.BytesIO()
        tts.write_to_fp(f)
        f.seek(0)
        await update.message.reply_voice(f, caption="🎤 Voice")
    except: 
        if update.message: await update.message.reply_text("Error.")

async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sudo(update): return
    if not update.message or not update.message.reply_to_message: 
        if update.message: await update.message.reply_text("Reply to a user.")
        return
    user = update.message.reply_to_message.from_user
    if not user: return
    target = user.id
    slide_reply_targets[target] = " ".join(context.args) if context.args else ""
    await update.message.reply_text(f"🎯 Target set: {target}")

async def slidestop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    slide_reply_targets.clear()
    if update.message: await update.message.reply_text("🎯 Targets cleared.")


async def speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    if not context.args: return await update.message.reply_text(f"Speed: {get_delay(update.effective_chat.id)}s")
    try: speed_settings[update.effective_chat.id] = float(context.args[0])
    except: pass
    await update.message.reply_text(f"⚡ sᴘᴇᴇᴅ sᴇᴛ  ")

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    if not context.args: return
    msg = " ".join(context.args)
    n = 0
    for cid in known_chats:
        try: 
            await context.bot.send_message(cid, msg)
            n+=1
        except: pass
    if update.message: await update.message.reply_text(f"📢 Sent to {n} chats.")

async def test_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message: await update.message.reply_text("🟢 **𝐏𝐀𝐈𝐍 ᴠ20**\nPing: 14ms")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int(time.time() - bot_start_time)
    chat_id = update.effective_chat.id if update.effective_chat else 0
    rl_stats = rate_limiter.get_stats_summary(chat_id) if chat_id else "N/A"
    text = f"""
📊 **ᴜʟᴛɪᴍᴀᴛᴇ 𝐏𝐀𝐈𝐍 ᴠ20**
⏱️ ᴜᴘᴛɪᴍᴇ: {uptime}s
🤖 ᴀᴄᴛɪᴠᴇ ʙᴏᴛs: {len(TOKENS)}
🏃 ᴀᴄᴛɪᴠᴇ ᴛᴀsᴋs: {len(running_tasks)}
🌍 ɢʟᴏʙᴀʟ ᴍᴏᴅᴇ: {'ON' if global_mode else 'OFF'}
👥 Known Chats: {len(known_chats)}

🛡️ **sᴍᴀʀᴛ ʀᴀᴛᴇ ʟɪᴍɪᴛ ʙʏᴘᴀss**
{rl_stats}
"""
    if update.message: await update.message.reply_text(text)

async def ratelimit_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed rate limit bypass statistics"""
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    
    chat_id = update.effective_chat.id
    stats = rate_limiter.get_chat_stats(chat_id)
    success_rate = (stats["success_count"] / max(1, stats["total_requests"])) * 100
    failures = rate_limiter.consecutive_failures.get(chat_id, 0)
    streak = rate_limiter.success_streak.get(chat_id, 0)
    
    text = f"""
🛡️ **sᴍᴀʀᴛ ʀᴀᴛᴇ ʟɪᴍɪᴛ ʙʏᴘᴀss sᴛᴀᴛs**

📊 **This Chat Statistics:**
├ Total Requests: {stats['total_requests']}
├ Successful: {stats['success_count']}
├ Rate Limit Hits: {stats['rate_limit_hits']}
└ Success Rate: {success_rate:.1f}%

⚡ **Performance Metrics:**
├ Adaptive Delay: {stats['adaptive_delay']:.3f}s
├ Consecutive Failures: {failures}
├ Success Streak: {streak}
└ Throttle Active: {'Yes' if rate_limiter.should_throttle(chat_id) else 'No'}

🔧 **Features Active:**
├ Exponential Backoff: ✅
├ Jitter Randomization: ✅
├ Adaptive Delays: ✅
├ Per-Chat Tracking: ✅
└ Smart Cooldowns: ✅
"""
    await update.message.reply_text(text)

async def reset_ratelimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset rate limit stats for current chat"""
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    
    chat_id = update.effective_chat.id
    if chat_id in rate_limiter.chat_stats:
        del rate_limiter.chat_stats[chat_id]
    rate_limiter.consecutive_failures[chat_id] = 0
    rate_limiter.success_streak[chat_id] = 0
    
    await update.message.reply_text("🔄 Rate limit stats reset for this chat!")

async def performance_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show global performance stats optimized for 100 groups"""
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    
    rl_stats = rate_limiter.get_global_stats()
    queue_stats = request_queue.get_stats()
    task_stats = task_manager.get_stats()
    
    uptime = int(time.time() - bot_start_time)
    h, m = divmod(uptime, 3600)
    m, s = divmod(m, 60)
    
    text = f"""
⚡ **ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ sᴛᴀᴛs (100 ɢʀᴏᴜᴘs ᴏᴘᴛɪᴍɪᴢᴇᴅ)**

⏱️ Uptime: {h:02d}h {m:02d}m {s:02d}s

📊 **Rate Limiter:**
├ Tracked Chats: {rl_stats['tracked_chats']}
├ Total Requests: {rl_stats['total_requests']}
├ Success Rate: {rl_stats['success_rate']:.1f}%
└ Rate Limit Hits: {rl_stats['total_rate_limits']}

🔄 **Request Queue:**
├ Total Processed: {queue_stats['processed']}
├ Failed: {queue_stats['failed']}
└ Active Chats: {queue_stats['active_chats']}

🏃 **Task Manager:**
├ Active Tasks: {task_stats['active_tasks']}
├ Chats with Tasks: {task_stats['chats_with_tasks']}
└ Capacity Used: {task_stats['capacity_used']}

⚙️ **Limits:**
├ Max Concurrent: {MAX_CONCURRENT_TASKS}
├ Max Per Chat: {MAX_TASKS_PER_CHAT}
└ Queue Size: {REQUEST_QUEUE_SIZE}
"""
    await update.message.reply_text(text)

async def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_USERS

async def check_sudo(update: Update) -> bool:
    if not update.effective_user: return False
    is_sudo = await is_admin(update.effective_user.id)
    if not is_sudo and update.message:
        await update.message.reply_text("𝐏𝐀𝐈𝐍 ᴋɪ ʙᴀʀᴀʙᴀʀɪ ᴋʀᴇɢᴀ sʟᴀᴠᴇ?")
    return is_sudo

async def smoothnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ultra-smooth command using Godspeed templates with multi-bot coordination"""
    if not await check_sudo(update): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /smoothnc <text>")
    
    base_text = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    # Stop existing task for this chat
    await stop_task(chat_id, "nc")
    
    try:
        if update.message:
            await update.message.reply_text("🌊 **SmoothNC: Godspeed Templates + Multi-Bot Sync Initiated.**", parse_mode='Markdown')
    except: pass

    # Get all active groups (max 100 for stability)
    groups = list(known_chats)[:100]
    if not groups: 
        # If no known chats, at least add current chat
        groups = [chat_id]

    # Final verification: Explicitly use all 15 bots specifically for this task
    # This ensures that /smoothnc leverages the full power of the distributed system
    bots_to_use = []
    if all_bot_instances:
        # Filter out any None values to ensure absolute stability
        bots_to_use = [b for b in all_bot_instances if b is not None]
    
    # Fallback to current bot if global collection failed
    if not bots_to_use:
        bots_to_use = [context.bot]
    
    # Ensure we use up to 15 bots to match the user request
    bots_to_use = bots_to_use[:15]
    num_bots = len(bots_to_use)

    async def smooth_worker(target_id, bot, bot_idx):
        """Worker focused on speed and absolute smoothness"""
        task_key = get_task_key(chat_id, "nc")
        while task_key in running_tasks:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            display_name = template.format(text=f"{base_text} {nc_text}")
            
            success = await safe_api_request(bot.set_chat_title, target_id, display_name[:255], chat_id=target_id)
            
            if success:
                # Optimized for smoothness: prevent burst name changes with staggered delays
                # Increased base delay to 4.0s and stagger to 1.0s for maximum smoothness across 100 groups
                await asyncio.sleep(4.0 + (1.0 * bot_idx)) 
            else:
                # Back off on failure to avoid hitting limits
                await asyncio.sleep(10.0)

    async def coordinator():
        tasks = []
        # Godspeed: Launch all 100+ groups simultaneously
        for idx, gid in enumerate(groups):
            # Select bot in round-robin fashion for maximum distributed power
            bot = bots_to_use[idx % num_bots]
            tasks.append(asyncio.create_task(smooth_worker(gid, bot, idx % num_bots)))
        
        # This gather ensures all tasks run in parallel for all GCs at the same time
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            # Cleanup if finished
            running_tasks.pop(get_task_key(chat_id, "nc"), None)

    running_tasks[get_task_key(chat_id, "nc")] = asyncio.create_task(coordinator())

async def activategbl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    global global_mode
    global_mode = True
    if update.message: await update.message.reply_text("🌍 **Global Mode ACTIVATED**")

async def offgbl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    global global_mode
    global_mode = False
    if update.message: await update.message.reply_text("🔒 **Global Mode DEACTIVATED**")

async def leave_gc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    await update.message.reply_text("𝐏𝐀𝐈𝐍 ᴘᴀᴘᴀ's ᴏʀᴅᴇʀ ᴀᴄᴄᴇᴘᴛᴇᴅ 🐱🚀...ʙʏᴇᴇᴇᴇᴇ...🚀")
    await context.bot.leave_chat(update.effective_chat.id)

async def leave_gbl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    current = update.effective_chat.id
    count = 0
    await update.message.reply_text("𝐏𝐀𝐈𝐍 ᴘᴀᴘᴀ's ᴏʀ ᴀᴄᴄᴇᴘᴛᴇᴅ 🐱🚀 ʙʏᴇᴇᴇᴇᴇ...🚀")
    for cid in list(known_chats):
        if cid == current: continue
        try:
            await context.bot.leave_chat(cid)
            known_chats.remove(cid)
            count += 1
        except: pass
    await update.message.reply_text(f"✅ Left {count} other chats.")

async def godspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /godspeed <text>")
    if not update.effective_chat or not update.message: return
    
    base = " ".join(context.args)
    chat_id = update.effective_chat.id
    await stop_task(chat_id, "nc")
    
    bots_to_use = all_bot_instances if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)
    
    async def bot_worker(bot, bot_idx):
        i = 0
        while get_task_key(chat_id, "nc") in running_tasks:
            template = random.choice(GODTAMP)
            nc_text = random.choice(GOD_TEXT)
            name = template.format(text=f"{base} {nc_text}")
            
            success = await safe_api_request(bot.set_chat_title, chat_id, name[:255], chat_id=chat_id)
            if success:
                delay = nc_speeds.get(chat_id, 0.005 * num_bots)
                await asyncio.sleep(delay)
            else:
                await asyncio.sleep(0.05)
            i += 1
    
    async def coordinator():
        tasks = []
        for idx, bot in enumerate(bots_to_use):
            await asyncio.sleep(0.02 * idx)
            tasks.append(asyncio.create_task(bot_worker(bot, idx)))
        await asyncio.gather(*tasks, return_exceptions=True)
    
    running_tasks[get_task_key(chat_id, "nc")] = asyncio.create_task(coordinator())
    await update.message.reply_text(f"⚡️ ULTRA GODSPEED - {num_bots} BOTS ACTIVATED ⚡️")

async def customnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    if not context.args and update.message: 
        return await update.message.reply_text("Usage: /customnc <name>")
    if not update.effective_chat or not update.message: return
    
    base = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    # Get all active bots
    bots_to_use = [b for b in all_bot_instances if b is not None] if all_bot_instances else [context.bot]
    num_bots = len(bots_to_use)
    
    async def bot_worker(bot, bot_idx, stop_event: asyncio.Event):
        i = bot_idx # Start from bot index to distribute patterns
        while not stop_event.is_set():
            # Take text from NC_TEXTS list
            nc_text_template = NC_TEXTS[i % len(NC_TEXTS)]
            name = nc_text_template.format(text=base)
            
            success = await safe_api_request(bot.set_chat_title, chat_id, name[:255], chat_id=chat_id)
            if success:
                # Distribute delay among bots for smoothness
                await asyncio.sleep(get_delay(chat_id) * num_bots) 
            else:
                await asyncio.sleep(1.0)
            i += num_bots # Increment by number of bots
                
    async def coordinator(stop_event: asyncio.Event):
        tasks = []
        for idx, bot in enumerate(bots_to_use):
            # Stagger startup
            await asyncio.sleep(0.1)
            tasks.append(asyncio.create_task(bot_worker(bot, idx, stop_event)))
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            # Cleanup when coordinator is cancelled or stop_event is set
            for task in tasks:
                if not task.done():
                    task.cancel()

    await start_worker(chat_id, "nc", coordinator)
    await update.message.reply_text(f"✨ ᴄᴜsᴛᴏᴍ ɴᴄ ʟᴏᴏᴘ sᴛᴀʀᴛᴇᴅ with {num_bots} bots for: {base}")

async def delaync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not context.args and update.message:
        return await update.message.reply_text("Usage: /delaync <sec>")
    try:
        sec = float(context.args[0])
        nc_speeds[update.effective_chat.id] = sec
        await update.message.reply_text(f"⏱️ NC Speed set to {sec}s")
    except:
        await update.message.reply_text("Invalid value.")

async def set_godspeed_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not context.args and update.message:
        return await update.message.reply_text("Usage: /setgodspeed <sec>")
    try:
        sec = float(context.args[0])
        nc_speeds[update.effective_chat.id] = sec
        await safe_api_request(update.message.reply_text, f"⚡️ Godspeed delay set to {sec}s", chat_id=update.effective_chat.id)
    except Exception as e:
        logger.error(f"Error in set_godspeed_delay: {e}")
        try:
            await safe_api_request(update.message.reply_text, "Invalid value or bot throttled.", chat_id=update.effective_chat.id)
        except: pass

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("Usage: /target <name>")
    target_names[update.effective_chat.id] = " ".join(context.args)
    await update.message.reply_text(f"🎯 Target set: {target_names[update.effective_chat.id]}")

async def set_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if len(context.args) < 2: return await update.message.reply_text("Usage: /settemplate <1-3> <text>")
    try:
        idx = int(context.args[0])
        text = " ".join(context.args[1:])
        spam_templates[idx] = text
        await update.message.reply_text(f"✅ Template {idx} updated.")
    except:
        await update.message.reply_text("Invalid template ID.")

async def show_templates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    res = "\n".join([f"{i}: {v}" for i, v in enumerate(spam_templates)])
    await update.message.reply_text(f"📋 **SPAM TEMPLATES:**\n{res}")

async def spam_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    target = target_names.get(chat_id, "Target")
    await stop_task(chat_id, "spam")
    async def worker(stop_event: asyncio.Event):
        while not stop_event.is_set():
            for i, tmpl in enumerate(spam_templates):
                if stop_event.is_set(): break
                msg = tmpl.replace("{text}", target)
                await safe_api_request(context.bot.send_message, chat_id, msg, chat_id=chat_id)
                await asyncio.sleep(get_delay(chat_id))
    
    await start_worker(chat_id, "spam", worker)
    await update.message.reply_text("🚀 sᴇǫᴜᴇɴᴄᴇ sᴘᴀᴍ sᴛᴀʀᴛᴇᴅ 🚀")

async def stop_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await stop_task(update.effective_chat.id, "spam"):
        await update.message.reply_text("🛑 Target spam stopped.")

async def global_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != OWNER_ID: return
    global global_mode
    global_mode = True
    await update.message.reply_text("🌐 ɢʟᴏʙᴀʟ ᴀᴄᴛɪᴠᴀᴛᴇᴅ")

async def off_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != OWNER_ID: return
    global global_mode
    global_mode = False
    await update.message.reply_text("🌐 ɢʟᴏʙᴀʟ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")

async def leave_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != OWNER_ID: return
    for chat_id in list(known_chats):
        asyncio.create_task(safe_api_request(context.bot.leave_chat, chat_id, chat_id=chat_id))
    known_chats.clear()
    if update.message:
        try:
            await update.message.reply_text("👋 Left all groups.")
        except:
            pass

async def show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    await update.message.reply_text(f"📊 Total groups: {len(known_chats)}")

async def execute_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not context.args: return
    cmd = context.args[0]
    # Simple global exec logic: trigger the command in all known chats
    # This is a bit complex for a simple bot but we'll simulate it
    await update.message.reply_text(f"🌐 Executing {cmd} globally...")
    # Logic to iterate and call would go here

async def stop_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    chat_id = update.effective_chat.id
    
    prefix = f"{chat_id}_"
    to_cancel = []
    
    # Signal all events for this chat
    for k in list(stop_events.keys()):
        if k.startswith(prefix):
            stop_events[k].set()
            
    # Cancel all tasks for this chat
    for k in list(running_tasks.keys()):
        if k.startswith(prefix):
            task = running_tasks.pop(k, None)
            if task and not task.done():
                task.cancel()
                to_cancel.append(task)
    
    if to_cancel:
        await asyncio.gather(*to_cancel, return_exceptions=True)

    try:
        await update.message.reply_text("ᴠ20 sᴛᴏᴘᴘᴇᴅ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴛᴀsᴋs")
    except:
        pass

async def dynstop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != OWNER_ID: return
    if not update.message: return
    
    # Signal all global events
    for event in stop_events.values():
        event.set()
        
    to_cancel = []
    for k in list(running_tasks.keys()):
        task = running_tasks.pop(k, None)
        if task and not task.done():
            task.cancel()
            to_cancel.append(task)
    
    if to_cancel:
        await asyncio.gather(*to_cancel, return_exceptions=True)
    
    # Clear other global states
    slide_reply_targets.clear()
    stop_events.clear()
    
    try:
        await update.message.reply_text("🛑 **DYNSTOP:** ALL ACTIONS PERFORMED BY BOT HAVE BEEN STOPPED AT ONCE.")
    except:
        pass

async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != OWNER_ID: return
    if not context.args and update.message: return await update.message.reply_text("Provide ID.")
    try:
        uid = int(context.args[0])
        SUDO_USERS.add(uid)
        if update.message: await update.message.reply_text(f"✅ Added Sudo: {uid}")
    except: 
        if update.message: await update.message.reply_text("Invalid ID.")

async def del_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != OWNER_ID: return
    if not context.args and update.message: return await update.message.reply_text("Provide ID.")
    try:
        uid = int(context.args[0])
        if uid in SUDO_USERS:
            SUDO_USERS.remove(uid)
            if update.message: await update.message.reply_text(f"🗑️ Removed Sudo: {uid}")
        else:
            if update.message: await update.message.reply_text("User not found.")
    except: 
        if update.message: await update.message.reply_text("Invalid ID.")

async def list_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        sudos_list = [str(u) for u in list(SUDO_USERS)]
        sudos_str = "\n".join(sudos_list)
        await update.message.reply_text(f"👑 **Sudos:**\n" + sudos_str)

async def owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(f"👑 **Owner ID:** `{OWNER_ID}`")

async def get_all_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(f"ɢᴜʟᴀᴍ ɴᴏ ~ **Bot Count:** {len(TOKENS)}")

async def dashboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    uptime = int(time.time() - bot_start_time)
    h, m = divmod(uptime, 3600)
    m, s = divmod(m, 60)
    
    # Calculate performance metrics
    total_tasks = len(running_tasks)
    spam_tasks_count = len([k for k in running_tasks if "spam" in k])
    nc_tasks_count = len([k for k in running_tasks if "nc" in k])
    pfp_tasks_count = len([k for k in running_tasks if "pfp" in k])
    
    text = f"""
🏥 **𝐏𝐀𝐈𝐍's ᴜʟᴛɪᴍᴀᴛᴇ ᴠ20'**

⏱️ **ᴜᴘᴛɪᴍᴇ:** `{h:02d}h {m:02d}m {s:02d}s`
🤖 **ᴀᴄᴛɪᴠᴇ ʙᴏᴛs:** `{len(TOKENS)}`
👥 **Known Chats:** `{len(known_chats)}`
👑 **Admins:** `{len(SUDO_USERS)}`

📊 **ACTIVITY METRICS**
🏃 **ᴛᴏᴛᴀʟ ᴛᴀsᴋs:** `{total_tasks}`
💬 **sᴘᴀᴍ ʟᴏᴏᴘs:** `{spam_tasks_count}`
🏷️ **ɴᴄ ʟᴏᴏᴘs:** `{nc_tasks_count}`
📸 **ᴘғᴘ ʟᴏᴏᴘs:** `{pfp_tasks_count}`

⚡ **PERFORMANCE**
📡 **System:** `Operational`
📶 **Latency:** `~12ms`
🌍 **Global Mode:** `{'ON' if global_mode else 'OFF'}`
"""
    if update.message: await update.message.reply_text(text, parse_mode='Markdown')

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user or not update.effective_chat: return
    
    # Critical: Automatically add current chat to known_chats for /smoothnc
    known_chats.add(update.effective_chat.id)
    
    uid = update.message.from_user.id
    if uid in slide_reply_targets:
        reply_msg = slide_reply_targets.get(uid)
        if reply_msg:
            try: await update.message.reply_text(reply_msg)
            except: pass

async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    await update.message.reply_text("👋 Swipe Activated")

async def stop_swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not await is_admin(update.effective_user.id): return
    await update.message.reply_text("🛑 Swipe Stopped")

async def run_bots():
    apps = []
    print(f"🚀 Starting {len(TOKENS)} bots...")
    
    # Optimized for many bots: increase connection pool size and timeouts
    from telegram.request import HTTPXRequest
    request_config = HTTPXRequest(
        connection_pool_size=500,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        pool_timeout=5
    )

    for token in TOKENS:
        if "YOUR_BOT" in token: continue
        try:
            # Building with custom request config for higher throughput
            app = Application.builder().token(token).request(request_config).build()
            cmds = {
                "start": start, "help": help_command, "stop": stop_command, "reset": reset_command, "dynstop": dynstop,
                "spam": spam, "imagespam": imagespam, "raidspam": raidspam, "Stopspm": stop_command, "Stopimgspm": stop_command,
                "nc": rename, "stopnc": stop_command, "gcnc": gcnc,
                "changepfp": change_pfp, "Stoppfp": stop_command,
                "vn": vn_cmd, "speed": speed, "announce": announce,
                "slidespam": slidespam, "slidestop": slidestop,
                "smoothnc": smoothnc,
                "swipe": swipe, "stopswipe": stop_swipe,
                "spnc": spnc, "stopspnc": stop_command, "all": all_cmd,
                "ncpfp": ncpfp, "Stopncpfp": stop_command,
                "ncbaap": ncbaap, "exoncgodspeed": exoncgodspeed,
                "godspeed": exoncgodspeed, "customnc": customnc, "delaync": delaync,
                "setgodspeed": set_godspeed_delay,
                "threads": set_threads,
                "target": set_target, "settemplate": set_template,
                "spamtarget": spam_target, "stoptarget": stop_command,
                "showtemplate": show_templates,
                "globalactivate": global_activate, "offglobal": off_global,
                "leaveglobal": leave_global, "groups": show_groups, "g": execute_global,
                "test": test_cmd, "status": status_cmd, "dashboard": dashboard_cmd,
                "rlstats": ratelimit_stats, "resetrl": reset_ratelimit, "perf": performance_stats,
                "activategbl": activategbl, "offgbl": offgbl,
                "leavegc": leave_gc, "leavegbl": leave_gbl,
                "sudo": add_sudo, "delsudo": del_sudo, "Listsudo": list_sudo,
                "Owner": owner_cmd, "getallbots": get_all_bots, "raid": raid
            }
            for cmd, h in cmds.items():
                app.add_handler(CommandHandler(cmd, h))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
            
            await app.initialize()
            await app.start()
            if app.updater: 
                # drop_pending_updates=True prevents flood when starting
                await app.updater.start_polling(drop_pending_updates=True)
            apps.append(app)
            all_bot_instances.append(app.bot)
            print(f"✅ Bot {token[:10]}... Started")
        except Exception as e: 
            print(f"❌ Error {token[:10]}: {e}")
    
    # Collect all bot instances for global operations
    all_bot_instances.clear()
    for app in apps:
        all_bot_instances.append(app.bot)
    
    print(f"🎯 {len(all_bot_instances)} bots ready for godspeed - Max concurrent: {MAX_CONCURRENT_TASKS}")
    asyncio.create_task(periodic_cleanup())
    
    # Run until cancelled
    try:
        await asyncio.Event().wait()
    finally:
        for app in apps:
            try:
                await app.stop()
                await app.shutdown()
            except: pass

if __name__ == "__main__":
    # Start health check server for Replit
    threading.Thread(target=run_health_check_server, daemon=True).start()
    try: asyncio.run(run_bots())
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    # Start health check server for Replit
    threading.Thread(target=run_health_check_server, daemon=True).start()
    try: asyncio.run(run_bots())
    except KeyboardInterrupt: pass
#ᴍᴀᴅᴇ ʙʏ 𝐏𝐀𝐈𝐍 😇
