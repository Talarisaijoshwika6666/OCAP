import subprocess
import tempfile
import os


def _compile_and_run(compile_cmd, run_cmd, input_data, timeout):
    """Helper: compile (optional) then run, feeding input_data via stdin."""
    if compile_cmd:
        compile_result = subprocess.run(
            compile_cmd, capture_output=True, text=True, timeout=timeout
        )
        if compile_result.returncode != 0:
            return '', compile_result.stderr.strip()

    # Normalise input: each value on its own line, trailing newline
    if input_data:
        # If input has spaces but no newlines, split on spaces → one per line
        # This handles both "10 20" and "10\n20" formats
        lines = input_data.strip().replace('\r\n', '\n').split('\n')
        normalised = '\n'.join(line for line in lines) + '\n'
    else:
        normalised = ''

    result = subprocess.run(
        run_cmd,
        input=normalised,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    stdout = result.stdout.rstrip('\n') if result.stdout else ''
    stderr = result.stderr.strip() if result.stderr else ''
    return stdout, stderr


def run_code(code, language, input_data='', timeout=8):
    """
    Runs `code` in `language`, feeding `input_data` via stdin.
    Returns (stdout, stderr).
    Supported: python/python3, java, javascript, c, cpp, ruby.
    """
    try:
        if language in ('python', 'python3'):
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.py')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(code)
                return _compile_and_run(None, ['python', src], input_data, timeout)

        elif language == 'java':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'Main.java')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(code)
                return _compile_and_run(
                    ['javac', src],
                    ['java', '-cp', tmpdir, 'Main'],
                    input_data, timeout
                )

        elif language == 'javascript':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.js')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(code)
                return _compile_and_run(None, ['node', src], input_data, timeout)

        elif language == 'c':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.c')
                exe = os.path.join(tmpdir, 'main')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(code)
                return _compile_and_run(
                    ['gcc', src, '-O2', '-o', exe],
                    [exe],
                    input_data, timeout
                )

        elif language == 'cpp':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.cpp')
                exe = os.path.join(tmpdir, 'main')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(code)
                return _compile_and_run(
                    ['g++', src, '-O2', '-o', exe],
                    [exe],
                    input_data, timeout
                )

        elif language == 'ruby':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.rb')
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(code)
                return _compile_and_run(None, ['ruby', src], input_data, timeout)

        else:
            return '', f'Language "{language}" is not supported.'

    except subprocess.TimeoutExpired:
        return '', 'Time Limit Exceeded'
    except FileNotFoundError as e:
        tool = str(e).split("'")[1] if "'" in str(e) else str(e)
        return '', f'Compiler/runtime not found: {tool}. Please install it on the server.'
    except Exception:
        import traceback
        return '', traceback.format_exc()