#!/usr/bin/env python
import os
import sys
#使用redis来存储sessionid相关信息
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test6.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
