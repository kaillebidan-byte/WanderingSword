#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""互換入口。実装はcheck_next_task_packet_v2へ移行済み。"""
from check_next_task_packet_v2 import *  # noqa: F401,F403


if __name__ == "__main__":
    import sys

    sys.exit(main())
