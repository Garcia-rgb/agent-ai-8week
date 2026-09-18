"""支持 ``python -m support_agent``，等价于 ``smartpv-agent``。"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
