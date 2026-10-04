from backend.models.orm import User
print("User properties:", [p for p in dir(User) if 'phone' in p])
