from flask import Flask, request, jsonify
from pathlib import Path
import subprocess

app = Flask(__name__)

APP_DIR = "/home/katrin/catty-reminders-app"
APP_SERVICE = "catty-reminders"
ENV_FILE = "/home/katrin/catty-reminders-app/.env"

@app.route('/', methods=['GET', 'POST'])
def handle():
    if request.method == 'GET':
        return jsonify({"message": "Webhook handler running"}), 200

    if request.headers.get('X-GitHub-Event') == 'push':
        data = request.get_json(silent=True) or {}
        commit_sha = data.get('after')
        branch_ref = data.get('ref', '')
        branch = branch_ref.replace('refs/heads/', '')

        if not commit_sha or commit_sha == '0000000000000000000000000000000000000000':
            return jsonify({"message": "No valid SHA"}), 200

        print("Starting deployment...")
        subprocess.run(["git", "-C", APP_DIR, "fetch", "origin"], check=True)
        if branch:
            subprocess.run(["git", "-C", APP_DIR, "checkout", branch], check=True)
        subprocess.run(["git", "-C", APP_DIR, "reset", "--hard", commit_sha], check=True)
        print("Code updated")

        env_path = Path(ENV_FILE)
        lines = []
        found = False

        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("DEPLOY_REF="):
                    lines.append(f"DEPLOY_REF={commit_sha}")
                    found = True
                else:
                    lines.append(line)

        if not found:
            lines.append(f"DEPLOY_REF={commit_sha}")

        env_path.write_text("\n".join(lines) + "\n")
        print(f"DEPLOY_REF written: {commit_sha}")

        subprocess.run(["sudo", "systemctl", "restart", APP_SERVICE], check=True)
        print("Service restarted")

        return jsonify({"message": "Deployment completed"}), 200

    return jsonify({"message": "Not a push event"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
