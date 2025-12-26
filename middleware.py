<<<<<<< HEAD
class BehaviorEngineMiddleware:
    """
    Geçici (Mock) Middleware.
    """
    def __init__(self, app):
        self.app = app.wsgi_app
    
    def __call__(self, environ, start_response):
        # Gelen isteği aynen Flask'a ilet
        return self.app(environ, start_response)
=======
# middleware.py
from flask import Request
from security.logging_secure import secure_log
from security.bruteforce_protection import register_failed_attempt
from behavior_engine import BehaviorEngine


class BehaviorEngineMiddleware:
    """
    Production-friendly middleware:
    - extracts minimal request signals
    - runs BehaviorEngine scoring
    - blocks only at/over threshold
    - logs everything into DIM secure logs
    """
    def __init__(self, app):
        self.app = app
        self.wsgi_app = app.wsgi_app
        self.engine = BehaviorEngine()

    def __call__(self, environ, start_response):
        req = Request(environ)

        ip = req.remote_addr
        path = req.path or "/"
        ua = req.headers.get("User-Agent", "")
        qs = req.query_string.decode("utf-8", "ignore") if req.query_string else ""
        body = ""
        try:
            # request body (small) – don't overread
            body = req.get_data(cache=True, as_text=True)[:2000]
        except Exception:
            body = ""

        score, reasons = self.engine.evaluate(
            path=path,
            ip=ip,
            user_agent=ua,
            query=qs,
            body=body,
        )

        # log signal (always)
        secure_log(
            "behavior_engine_score",
            {"score": score, "reasons": reasons},
            level="INFO",
            ip=ip,
            path=path,
        )

        if score >= self.engine.threshold:
            secure_log(
                "behavior_engine_block",
                {"score": score, "reasons": reasons},
                level="WARN",
                ip=ip,
                path=path,
            )

            # Optional: feed brute-force tracker lightly (adaptive)
            identifier = f"{ip}:behavior"
            register_failed_attempt(identifier, ip=ip, email="__behavior__")

            res_body = b"Blocked by Behavior Engine"
            status = "403 FORBIDDEN"
            headers = [("Content-Type", "text/plain; charset=utf-8")]
            start_response(status, headers)
            return [res_body]

        return self.wsgi_app(environ, start_response)
>>>>>>> main
