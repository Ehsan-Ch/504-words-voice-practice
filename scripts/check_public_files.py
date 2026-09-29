"""Audit tracked publication files without inspecting private input directories."""
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DENIED = {'.wav', '.mp3', '.mp4', '.m4a', '.ogg', '.opus', '.flac', '.aac',
          '.wma', '.mkv', '.webm', '.mov', '.avi', '.pdf', '.zip', '.rar', '.7z',
          '.bin', '.exe', '.dll', '.log', '.jsonl', '.pem', '.key', '.gguf',
          '.pt', '.safetensors', '.onnx'}


def main():
    names = subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    problems = []
    for name in filter(None, names):
        path = ROOT / name
        if path.suffix.lower() in DENIED or path.stat().st_size > 300_000:
            problems.append(f'{name}: disallowed type or unexpectedly large file')
        if any(part.lower() in {'private', 'data', 'models', 'output', 'work'}
               for part in path.relative_to(ROOT).parts):
            problems.append(f'{name}: private output directory')
        if path.suffix.lower() not in DENIED:
            text = path.read_text(encoding='utf-8-sig')
            if re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|'
                         r'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----', text):
                problems.append(f'{name}: possible credential')
            if re.search(r'[CD]:[\\/]+Users[\\/]+ehsan|D:[\\/]+Ehsan[\\/]+Ehsan',
                         text, re.I):
                problems.append(f'{name}: personal machine path')
            if path.suffix == '.md':
                for link in re.findall(r'\]\(([^)]+)\)', text):
                    target = link.split('#', 1)[0]
                    if target and not re.match(r'[a-z]+:', target, re.I):
                        if not (path.parent / unquote(target)).is_file():
                            problems.append(f'{name}: missing local link {target}')
    if problems:
        raise SystemExit('\n'.join(problems))
    print(f'Public-file checks passed for {len(list(filter(None, names)))} tracked files.')
    print('This targeted check complements manual review; it is not a secret scanner.')


if __name__ == '__main__':
    main()
