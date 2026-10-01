"""외부 연결 없이 파일·구문·링크와 제한된 비밀정보 패턴을 검사한다."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "provider-token": r"(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,}|sk-[A-Za-z0-9]{24,}|AKIA[A-Z0-9]{16})",
    "credential-literal": r"(?i)(?:password|api_key|access_token|secret_key)\s*[:=]\s*[\"'][^\"'\n]{8,}[\"']",
    "private-address": r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b",
}
EXCLUDED = {".git", "__pycache__", ".venv", "outputs"}
ALLOWED = {".py", ".md", ".json", ".svg", ".mmd", ".html", ".css", ".js", ".yml", ".cff"}


def secret_rules(text):
    return [name for name, pattern in RULES.items() if re.search(pattern, text)]


def png_rules(data):
    """승인된 캡처의 PNG 구조를 검사하고 숨은 텍스트 metadata를 거부한다."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ["invalid-png"]
    offset, kinds = 8, []
    while offset + 12 <= len(data):
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + size + 12
        if end > len(data) or kind not in {b"IHDR", b"IDAT", b"IEND", b"sRGB", b"gAMA", b"cHRM", b"pHYs"}:
            return ["unexpected-png-chunk"]
        expected = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(data[offset + 4:end - 4]) & 0xffffffff != expected:
            return ["png-crc"]
        kinds.append(kind)
        offset = end
        if kind == b"IEND":
            break
    if not kinds or kinds[0] != b"IHDR" or kinds[-1] != b"IEND" or b"IDAT" not in kinds or offset != len(data):
        return ["invalid-png-structure"]
    return []


def inspect_file(root, path):
    if path.is_symlink():
        return ["symlink"]
    if path.suffix == ".png":
        raw = path.read_bytes()
        issues = png_rules(raw)
        try:
            manifest = json.loads((root / "docs/screenshots/manifest.json").read_text())
            approved = manifest["files"][path.relative_to(root).as_posix()]
            if hashlib.sha256(raw).hexdigest() != approved:
                issues.append("unreviewed-screenshot")
        except (OSError, ValueError, KeyError):
            issues.append("unreviewed-screenshot")
        return issues
    if path.suffix not in ALLOWED and path.name != ".gitignore":
        return ["unexpected-file-type"]
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        return ["unreadable-text"]
    issues = secret_rules(text)
    if any(line.rstrip() != line for line in text.splitlines()):
        issues.append("trailing-whitespace")
    if path.suffix == ".py":
        try:
            ast.parse(text)
        except SyntaxError:
            issues.append("python-syntax")
    if path.suffix == ".json":
        try:
            json.loads(text)
        except ValueError:
            issues.append("json-syntax")
    if path.suffix == ".md":
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            local = (path.parent / target.split("#")[0]).resolve()
            if not local.is_relative_to(root.resolve()) or not local.exists():
                issues.append("broken-local-link")
    return issues


def history_issues():
    # 커밋 이력의 모든 고유 blob도 검사하고 탐지 문자열은 출력하지 않는다.
    result = subprocess.run(["git", "rev-list", "--objects", "--all"],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    issues = []
    for row in result.stdout.splitlines():
        oid = row.split(" ", 1)[0]
        kind = subprocess.check_output(["git", "cat-file", "-t", oid], cwd=ROOT, text=True).strip()
        if kind != "blob":
            continue
        data = subprocess.check_output(["git", "cat-file", "-p", oid], cwd=ROOT)
        try:
            matches = secret_rules(data.decode("utf-8"))
        except UnicodeError:
            matches = png_rules(data) if data.startswith(b"\x89PNG\r\n\x1a\n") else ["non-text-history-blob"]
        issues.extend("history:" + oid + ":" + rule for rule in matches)
    return issues


def main():
    issues = []
    count = 0
    for path in sorted(ROOT.rglob("*")):
        if any(part in EXCLUDED for part in path.relative_to(ROOT).parts):
            continue
        if not (path.is_file() or path.is_symlink()):
            continue
        count += 1
        issues.extend(str(path.relative_to(ROOT)) + ":" + rule
                      for rule in inspect_file(ROOT, path))
    issues.extend(history_issues())
    print(json.dumps({"checked_files": count, "issues": issues,
                      "scope": "syntax, local link targets, JSON, heuristic secrets incl. history"}))
    return bool(issues)


if __name__ == "__main__":
    sys.exit(main())
