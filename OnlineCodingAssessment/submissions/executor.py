import subprocess
import tempfile
import os

def run_code(code, language, input_data, timeout=5):
    try:
        if language == 'python':
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
                f.write(code)
                fname = f.name
            result = subprocess.run(
                ['python', fname],
                input=input_data, capture_output=True,
                text=True, timeout=timeout
            )
            os.unlink(fname)
            return result.stdout.strip(), result.stderr.strip()

        elif language == 'javascript':
            with tempfile.NamedTemporaryFile(suffix='.js', delete=False, mode='w') as f:
                f.write(code)
                fname = f.name
            result = subprocess.run(
                ['node', fname],
                input=input_data, capture_output=True,
                text=True, timeout=timeout
            )
            os.unlink(fname)
            return result.stdout.strip(), result.stderr.strip()

        elif language == 'java':
            with tempfile.TemporaryDirectory() as tmpdir:
                fpath = os.path.join(tmpdir, 'Main.java')
                with open(fpath, 'w') as f:
                    f.write(code)
                compile_result = subprocess.run(
                    ['javac', fpath],
                    capture_output=True, text=True
                )
                if compile_result.returncode != 0:
                    return '', compile_result.stderr
                result = subprocess.run(
                    ['java', '-cp', tmpdir, 'Main'],
                    input=input_data, capture_output=True,
                    text=True, timeout=timeout
                )
                return result.stdout.strip(), result.stderr.strip()

        elif language == 'cpp':
            with tempfile.TemporaryDirectory() as tmpdir:
                src = os.path.join(tmpdir, 'main.cpp')
                exe = os.path.join(tmpdir, 'main.exe')
                with open(src, 'w') as f:
                    f.write(code)
                compile_result = subprocess.run(
                    ['g++', src, '-o', exe],
                    capture_output=True, text=True
                )
                if compile_result.returncode != 0:
                    return '', compile_result.stderr
                result = subprocess.run(
                    [exe],
                    input=input_data, capture_output=True,
                    text=True, timeout=timeout
                )
                return result.stdout.strip(), result.stderr.strip()

        else:
            return '', f'Language {language} not supported'

    except subprocess.TimeoutExpired:
        return '', 'Time Limit Exceeded'
    except FileNotFoundError as e:
        return '', f'Runtime not found: {str(e)}'
    except Exception as e:
        return '', str(e)