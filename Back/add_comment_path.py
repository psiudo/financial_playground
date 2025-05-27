# add_comment_path.py
# add_comment_path.py
# add_path_comment.py
# add_path_comment.py
# add_path_comment.py

import os

COMMENT_SYNTAX = {
    '.py': lambda path: f"# {path}",
    '.js': lambda path: f"// {path}",
    '.vue': lambda path: f"<!-- {path} -->",
    '.html': lambda path: f"<!-- {path} -->",
    '.md': lambda path: f"<!-- {path} -->",
}

EXCLUDE_DIRS = {'venv', '__pycache__', '.git', 'node_modules', 'dist', 'build', '.venv'}

def is_path_comment(line):
    line = line.strip()
    if not line: return False
    return (
        (line.startswith('#') or line.startswith('//') or line.startswith('<!--')) and
        any(part in line for part in ['.py', '.js', '.vue', '.html', '.md']) and
        ('/' in line or '\\' in line)
    )

def clean_and_add_path_comment(filepath, relpath, comment_line):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"읽기 오류: {filepath} → {e}")
        return

    # 1. 앞부분의 경로 주석을 전부 제거
    cleaned_lines = []
    i = 0
    while i < len(lines) and is_path_comment(lines[i]):
        i += 1
    cleaned_lines = lines[i:]

    # 2. 정확한 주석만 삽입
    final_lines = [comment_line + "\n"] + cleaned_lines

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
        print(f"정리 완료: {relpath}")
    except Exception as e:
        print(f"쓰기 오류: {filepath} → {e}")

def process_all_files(root_dir):
    for foldername, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            relpath = os.path.relpath(filepath, root_dir).replace('\\', '/')
            ext = os.path.splitext(filename)[1]

            if ext in COMMENT_SYNTAX:
                comment_line = COMMENT_SYNTAX[ext](relpath)
                clean_and_add_path_comment(filepath, relpath, comment_line)

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    process_all_files(base_dir)
