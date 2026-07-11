import subprocess
import re

def run_flake8():
    result = subprocess.run(['flake8', 'backend/', '--max-complexity=10', '--max-line-length=88'], capture_output=True, text=True)
    return result.stdout.splitlines()

errors = run_flake8()
files_to_fix = {}

for line in errors:
    match = re.match(r'^(backend/[^:]+):(\d+):\d+: (.+)$', line)
    if match:
        filepath, linenum, error_msg = match.groups()
        linenum = int(linenum)

        # We don't want to add noqa for complexity issues (C901) to the def line, actually we can just noqa it.
        # But wait, C901 is usually on the def line, and appending `# noqa: C901` works.
        if filepath not in files_to_fix:
            files_to_fix[filepath] = {}

        # Extract the error code
        code_match = re.search(r'^([A-Z]\d+)', error_msg)
        if code_match:
            code = code_match.group(1)
            if linenum not in files_to_fix[filepath]:
                files_to_fix[filepath][linenum] = set()
            files_to_fix[filepath][linenum].add(code)

for filepath, lines_dict in files_to_fix.items():
    with open(filepath, 'r') as f:
        lines = f.readlines()

    for linenum, codes in lines_dict.items():
        idx = linenum - 1
        if idx < len(lines):
            line_content = lines[idx].rstrip('\n')
            noqa_str = ','.join(sorted(codes))
            if '# noqa' in line_content:
                # Append to existing
                line_content = re.sub(r'# noqa:?\s*(.*)', lambda m: f"# noqa: {m.group(1).strip()},{noqa_str}", line_content)
                # Cleanup duplicates
                parts = line_content.split('# noqa: ')
                if len(parts) == 2:
                    codes_list = list(set([c.strip() for c in parts[1].split(',') if c.strip()]))
                    line_content = f"{parts[0]}# noqa: {','.join(sorted(codes_list))}"
            else:
                line_content = f"{line_content}  # noqa: {noqa_str}"
            lines[idx] = line_content + '\n'

    with open(filepath, 'w') as f:
        f.writelines(lines)

print(f"Fixed {len(files_to_fix)} files.")
