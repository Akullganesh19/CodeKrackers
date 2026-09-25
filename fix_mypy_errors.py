import os
import re

# Fix base_class.py DeclarativeTyping error
with open("backend/db/base_class.py", "r") as f:
    content = f.read()
content = content.replace('__name__: str', 'registry = None\n    __name__: str')
content = content.replace("class Base(DeclarativeBase):", "from sqlalchemy.ext.declarative import declarative_base\n\nBase = declarative_base()")
content = content.replace("""from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime

@as_declarative()
class Base:""", "from typing import Any\nfrom sqlalchemy.ext.declarative import declarative_base, declared_attr\nfrom sqlalchemy.sql import func\nfrom sqlalchemy import Column, DateTime\n\nBase = declarative_base()")
with open("backend/db/base_class.py", "w") as f:
    f.write(content)

# Fix orm.py invalid base class Base
with open("backend/models/orm.py", "r") as f:
    content = f.read()
# Replace from core.database import Base with from backend.db.base_class import Base
content = content.replace("from core.database import Base", "from backend.db.base_class import Base")
with open("backend/models/orm.py", "w") as f:
    f.write(content)

# Same for score_history
with open("backend/models/score_history.py", "r") as f:
    content = f.read()
content = content.replace("from core.database import Base", "from backend.db.base_class import Base")
with open("backend/models/score_history.py", "w") as f:
    f.write(content)
