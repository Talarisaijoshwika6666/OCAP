import subprocess
import tempfile
import os


def _compile_and_run(compile_cmd, run_cmd, input_data, timeout):
    """Helper: run a compile step (if given) then a run step, in a temp dir."""
    if compile_cmd:
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if compile_result.returncode != 0:
            return '', compile_result.stderr
    result = subprocess.run(
        run_cmd, input=input_data, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip()


def run_code(code, language, input_data, timeout=8):
    """
    Runs `code` written in `language`, feeding it `input_data` on stdin.
    Returns (stdout, stderr) -- both stripped strings.

    Supported: python, javascript, java, ruby, cpp, c.
    Each needs its runtime/compiler installed on this machine
    (python, node, javac/java, ruby, g++, gcc respectively).
    """
    try:
        if language == 'python':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.py')
                with open(src, 'w') as f:
                    f.write(code)
                return _compile_and_run(None, ['python', src], input_data, timeout)

        elif language == 'javascript':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.js')
                with open(src, 'w') as f:
                    f.write(code)
                return _compile_and_run(None, ['node', src], input_data, timeout)

        elif language == 'java':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'Main.java')
                with open(src, 'w') as f:
                    f.write(code)
                return _compile_and_run(
                    ['javac', src],
                    ['java', '-cp', tmpdir, 'Main'],
                    input_data, timeout
                )

        elif language == 'ruby':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.rb')
                with open(src, 'w') as f:
                    f.write(code)
                return _compile_and_run(None, ['ruby', src], input_data, timeout)

        elif language == 'cpp':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.cpp')
                exe = os.path.join(tmpdir, 'main.exe')
                with open(src, 'w') as f:
                    f.write(code)
                return _compile_and_run(
                    ['g++', src, '-O2', '-o', exe],
                    [exe],
                    input_data, timeout
                )

        elif language == 'c':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.c')
                exe = os.path.join(tmpdir, 'main.exe')
                with open(src, 'w') as f:
                    f.write(code)
                return _compile_and_run(
                    ['gcc', src, '-O2', '-o', exe],
                    [exe],
                    input_data,
                    timeout
                )

        else:
            return '', f'Language {language} not supported'

    except subprocess.TimeoutExpired:
        return '', 'Time Limit Exceeded'
    except Exception as e:
      import traceback
      return "", traceback.format_exc()
    except Exception as e:
        return '', str(e)