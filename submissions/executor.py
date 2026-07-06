import subprocess
import tempfile
import os

def is_docker_available():
    # If explicitly disabled in env, return False
    if os.environ.get('DISABLE_DOCKER_SANDBOX', 'False').lower() in ('true', '1', 'yes'):
        return False
    try:
        # Check if docker service is running
        result = subprocess.run(['docker', 'info'], capture_output=True, timeout=2)
        return result.returncode == 0
    except Exception:
        return False

def run_code_docker(code, language, input_data, timeout=5):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Get absolute directory path for volume mapping
        abs_tmpdir = os.path.abspath(tmpdir)
        
        if language == 'python':
            fpath = os.path.join(tmpdir, 'script.py')
            with open(fpath, 'w') as f:
                f.write(code)
            
            result = subprocess.run([
                'docker', 'run', '--rm',
                '-i',
                '--network', 'none',
                '--memory', '128m',
                '--cpus', '0.5',
                '-v', f"{abs_tmpdir}:/app:ro",
                '-w', '/app',
                'python:3.10-slim',
                'python', 'script.py'
            ], input=input_data, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip()

        elif language == 'javascript':
            fpath = os.path.join(tmpdir, 'script.js')
            with open(fpath, 'w') as f:
                f.write(code)
            
            result = subprocess.run([
                'docker', 'run', '--rm',
                '-i',
                '--network', 'none',
                '--memory', '128m',
                '--cpus', '0.5',
                '-v', f"{abs_tmpdir}:/app:ro",
                '-w', '/app',
                'node:18-alpine',
                'node', 'script.js'
            ], input=input_data, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip()

        elif language == 'java':
            fpath = os.path.join(tmpdir, 'Main.java')
            with open(fpath, 'w') as f:
                f.write(code)
            
            result = subprocess.run([
                'docker', 'run', '--rm',
                '-i',
                '--network', 'none',
                '--memory', '256m',
                '--cpus', '0.5',
                '-v', f"{abs_tmpdir}:/app",
                '-w', '/app',
                'openjdk:17-slim',
                'sh', '-c', 'javac Main.java && java Main'
            ], input=input_data, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip()

        elif language == 'cpp':
            fpath = os.path.join(tmpdir, 'main.cpp')
            with open(fpath, 'w') as f:
                f.write(code)
            
            result = subprocess.run([
                'docker', 'run', '--rm',
                '-i',
                '--network', 'none',
                '--memory', '128m',
                '--cpus', '0.5',
                '-v', f"{abs_tmpdir}:/app",
                '-w', '/app',
                'gcc:12',
                'sh', '-c', 'g++ main.cpp -o main && ./main'
            ], input=input_data, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip()

        else:
            return '', f'Language {language} not supported'

def run_code(code, language, input_data, timeout=5):
    try:
        # Check if docker is available for sandboxing
        if is_docker_available():
            try:
                return run_code_docker(code, language, input_data, timeout)
            except Exception:
                # If docker run failed (e.g. image not pulled), fallback to host execution
                pass

        # Fallback to direct host execution if Docker is not available or failed
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