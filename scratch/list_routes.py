from backend.main import app
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"Path: {route.path} | Methods: {route.methods}")
    else:
        print(f"Path: {getattr(route, 'prefix', str(route))} | Nested router")
