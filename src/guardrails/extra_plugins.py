"""
Assignment 11 — Extra Plugins for Production Pipeline
- RateLimitPlugin: Blocks excessive requests (Sliding window)
- AuditLogPlugin: Records all interactions to JSON
"""
import time
import json
from datetime import datetime
from collections import defaultdict, deque
from google.adk.plugins import base_plugin
from google.genai import types

# ============================================================
# 1. Rate Limiter Plugin
# Blocks users who send too many requests in a time window.
# ============================================================

class RateLimitPlugin(base_plugin.BasePlugin):
    def __init__(self, max_requests=10, window_seconds=60):
        super().__init__(name="rate_limiter")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Stores unix timestamps of requests per user_id
        self.user_windows = defaultdict(deque)
        self.blocked_count = 0

    async def on_user_message_callback(self, *, invocation_context, user_message):
        # In a real app, user_id would come from context. Defaulting to 'default_user'.
        user_id = "default_user" 
        now = time.time()
        window = self.user_windows[user_id]

        # 1. Clean up expired timestamps
        while window and window[0] < now - self.window_seconds:
            window.popleft()

        # 2. Check limit
        if len(window) >= self.max_requests:
            self.blocked_count += 1
            wait_time = int((window[0] + self.window_seconds) - now)
            print(f"  [RATE LIMIT] Blocked user {user_id}. Wait {wait_time}s.")
            
            # Return a polite block message
            return types.Content(
                parts=[types.Part(text=f"Rate limit exceeded. Please wait {wait_time} seconds before trying again.")],
                role="model"
            )

        # 3. Record current request
        window.append(now)
        return None  # Allow request


# ============================================================
# 2. Audit Log Plugin
# Records every interaction (input, output, layer, latency).
# ============================================================

class AuditLogPlugin(base_plugin.BasePlugin):
    def __init__(self):
        super().__init__(name="audit_log")
        self.logs = []
        self.start_times = {}

    async def on_user_message_callback(self, *, invocation_context, user_message):
        # Record start time based on session_id
        session_id = getattr(invocation_context, "session_id", "default")
        self.start_times[session_id] = time.time()
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        # Calculate latency
        session_id = getattr(callback_context.invocation_context, "session_id", "default")
        start_time = self.start_times.get(session_id, time.time())
        latency = time.time() - start_time
        
        # Get input text
        input_text = ""
        for part in callback_context.invocation_context.user_message.parts:
            if part.text:
                input_text += part.text

        # Get output text
        output_text = ""
        if isinstance(llm_response, types.Content):
            for part in llm_response.parts:
                if part.text:
                    output_text += part.text
        else:
            output_text = str(llm_response)

        # Log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "output": output_text[:200] + "..." if len(output_text) > 200 else output_text,
            "latency_seconds": round(latency, 3),
            "status": "success" if "blocked" not in output_text.lower() else "blocked"
        }
        self.logs.append(log_entry)
        return llm_response

    def export_json(self, filepath="audit_log.json"):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
        print(f"  [AUDIT] Exported {len(self.logs)} logs to {filepath}")
