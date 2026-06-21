import os
import subprocess
import sys
from pathlib import Path

from flask import Blueprint, Response, jsonify
from sqlalchemy import text

from app.models import db


health_blueprint = Blueprint('health', __name__)

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]


def get_git_info() -> tuple[str, bool | None]:
    commitish = os.environ.get('GIT_COMMITISH')
    dirty_value = os.environ.get('GIT_DIRTY')

    if commitish and dirty_value is not None:
        dirty = dirty_value.lower() in ('true', '1', 'yes')
        return commitish, dirty

    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT_DIRECTORY,
        )
        git_commitish = result.stdout.strip() if result.returncode == 0 else 'unknown'
    except FileNotFoundError:
        git_commitish = 'unknown'

    if dirty_value is not None:
        dirty = dirty_value.lower() in ('true', '1', 'yes')
    else:
        try:
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT_DIRECTORY,
            )
            dirty = bool(status_result.stdout.strip()) if status_result.returncode == 0 else None
        except FileNotFoundError:
            dirty = None

    return commitish or git_commitish, dirty


STARTUP_COMMITISH, STARTUP_DIRTY = get_git_info()
RELOAD_MODE = 'disabled' if ('--no-reload' in sys.argv or not os.environ.get('WERKZEUG_RUN_MAIN')) else 'enabled'


@health_blueprint.route('/health')
def health() -> tuple[Response, int]:
    try:
        db.session.execute(text('SELECT 1'))
        status = 'ok'
        status_code = 200
    except Exception:
        status = 'error'
        status_code = 503

    return jsonify({
        'status': status,
        'commitish': STARTUP_COMMITISH,
        'dirty': STARTUP_DIRTY,
        'reload': RELOAD_MODE,
    }), status_code
