# Back/docs/shoe_tree.py
import os
import argparse

def print_tree(root, ignore_dirs, allowed_exts, depth=0, max_depth=3):
    """
    지정된 디렉토리(root)에서 파일 트리를 출력하되,
    - ignore_dirs에 포함된 폴더는 무시
    - allowed_exts에 포함된 확장자만 출력
    - max_depth까지만 출력
    """
    if depth > max_depth:
        return

    try:
        entries = sorted(os.listdir(root))
    except PermissionError:
        return

    for item in entries:
        path = os.path.join(root, item)
        if os.path.isdir(path):
            if item in ignore_dirs:
                continue
            print('│   ' * depth + '├── ' + item + '/')
            print_tree(path, ignore_dirs, allowed_exts, depth + 1, max_depth)
        elif os.path.isfile(path):
            ext = os.path.splitext(item)[1]
            if not allowed_exts or ext in allowed_exts:
                print('│   ' * depth + '├── ' + item)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SSAFY 프로젝트 구조 트리 출력기')
    parser.add_argument('--path', default='.', help='탐색 시작 경로 (기본값: 현재 디렉토리)')
    parser.add_argument('--ext', nargs='*', default=['.py', '.vue', '.js', '.html', '.md'],
                        help='출력할 확장자 목록 (기본: .py .vue .js .html .md)')
    parser.add_argument('--ignore', nargs='*', default=['venv', '__pycache__', '.git', 'node_modules', 'dist', 'build'],
                        help='무시할 디렉토리 이름 목록')
    parser.add_argument('--max-depth', type=int, default=3, help='최대 탐색 깊이 (기본값: 3)')

    args = parser.parse_args()

    print(f'📁 시작 경로: {args.path}')
    print(f'📄 포함 확장자: {args.ext}')
    print(f'🚫 제외 디렉토리: {args.ignore}')
    print(f'⏬ 최대 깊이: {args.max_depth}\n')

    print_tree(args.path, set(args.ignore), set(args.ext), depth=0, max_depth=args.max_depth)
