import sys
import os

# 添加应用目录到Python路径
project_home = os.path.expanduser('~/mysite')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 导入Flask应用
from app import app as application 