"""Tests for git diff helpers."""

from slay_check.git_diff import split_unified_diff_by_file


def test_split_unified_diff_by_file():
    diff = """diff --git a/foo.py b/foo.py
index 111..222 100644
--- a/foo.py
+++ b/foo.py
@@ -1 +1 @@
-old
+new
"""
    out = split_unified_diff_by_file(diff)
    assert "foo.py" in out
    assert "+new" in out["foo.py"]
