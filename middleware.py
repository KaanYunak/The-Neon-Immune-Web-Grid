class BehaviorEngineMiddleware:
    """
    Geçici (Mock) Middleware.
    """
    def __init__(self, app):
        self.app = app.wsgi_app
    
    def __call__(self, environ, start_response):
        # Gelen isteği aynen Flask'a ilet
        return self.app(environ, start_response)