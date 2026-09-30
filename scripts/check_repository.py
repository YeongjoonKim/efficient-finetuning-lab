"""외부 연결 없이 파일·구문·링크와 제한된 비밀정보 패턴을 검사한다."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

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


def inspect_file(root, path):
    if path.is_symlink():
        return ["symlink"]
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
            matches = ["non-text-history-blob"]
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
