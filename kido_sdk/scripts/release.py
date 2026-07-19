#!/usr/bin/env python3
"""
KIDO Release Pipeline — Builds SDK bundles, creates GitHub Release, uploads assets.

Usage:
    python scripts/release.py --token GITHUB_TOKEN [--version 1.1.0] [--dry-run]
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
import tarfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SDK_ROOT = Path(__file__).resolve().parent.parent
GITHUB_API = "https://api.github.com/repos/animeshdindapersonal-jpg/kido"


def run(cmd, cwd=None):
    print(f"  $ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd or SDK_ROOT, check=True)


def build_sdk(system_name, version):
    """Build a platform-specific SDK bundle."""
    print(f"\n🔨 Building SDK bundle for {system_name}...")

    dist_dir = SDK_ROOT / "_dist" / system_name
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    # Core source
    for src in [
        "kido_core",
        "kido_cli",
        "setup.py",
        "setup.cfg",
        "MANIFEST.in",
        "requirements.txt",
    ]:
        src_path = SDK_ROOT / src
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, dist_dir / src)
            else:
                shutil.copy2(src_path, dist_dir / src)

    # Examples
    examples_src = SDK_ROOT / "examples"
    if examples_src.exists():
        shutil.copytree(examples_src, dist_dir / "examples")

    # Docs
    for doc in ["README.md", "INSTALL.md", "QUICKSTART.md", "LICENSE", "SECURITY.md"]:
        doc_path = SDK_ROOT / doc
        if doc_path.exists():
            shutil.copy2(doc_path, dist_dir / doc)

    # Build the launcher script
    if system_name == "windows":
        _build_launcher_exe(dist_dir)
    else:
        _build_unix_launcher(dist_dir, system_name)

    # Create version file
    (dist_dir / "VERSION").write_text(f"{version}\n")

    # Package
    if system_name == "windows":
        archive_name = f"kido-sdk-windows"
        archive_path = SDK_ROOT / "_dist" / f"{archive_name}.zip"
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in dist_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(dist_dir))
    else:
        ext = "tar.gz"
        archive_name = f"kido-sdk-{system_name}"
        archive_path = SDK_ROOT / "_dist" / f"{archive_name}.{ext}"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(dist_dir, arcname=archive_name)

    # Checksum
    sha256 = hashlib.sha256()
    sha256.update(archive_path.read_bytes())
    checksum_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    checksum_path.write_text(f"{sha256.hexdigest()}  {archive_path.name}\n")

    print(f"  ✅  Created: {archive_path.name}")
    print(f"  ✅  Checksum: {sha256.hexdigest()[:16]}...")

    return archive_path, checksum_path


def _build_launcher_exe(dist_dir):
    """Build kido.exe using PyInstaller."""
    print("  🔨 Building kido.exe (PyInstaller)...")

    try:
        import PyInstaller
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )

    spec_path = SDK_ROOT / "kido.spec"
    if spec_path.exists():
        subprocess.run(
            [
                "pyinstaller",
                "kido.spec",
                "--distpath",
                str(dist_dir / "bin"),
                "--workpath",
                str(SDK_ROOT / "_build"),
            ],
            cwd=SDK_ROOT,
            check=True,
        )
    else:
        subprocess.run(
            [
                "pyinstaller",
                "--onefile",
                "--name",
                "kido",
                "--distpath",
                str(dist_dir / "bin"),
                "--workpath",
                str(SDK_ROOT / "_build"),
                str(SDK_ROOT / "kido_cli" / "cli.py"),
            ],
            cwd=SDK_ROOT,
            check=True,
        )

    # Copy examples/bin to dist
    bin_src = SDK_ROOT / "dist" / "kido.exe"
    if bin_src.exists():
        shutil.copy2(bin_src, dist_dir / "bin" / "kido.exe")


def _build_unix_launcher(dist_dir, system_name):
    """Create a shell launcher that uses venv python."""
    bin_dir = dist_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    launcher = bin_dir / "kido"
    launcher.write_text(f"""#!/usr/bin/env bash
# KIDO Launcher
SDK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$SDK_DIR/.kido-venv/bin/python" ]; then
    exec "$SDK_DIR/.kido-venv/bin/python" -m kido_cli.cli "$@"
else
    exec python3 -m kido_cli.cli "$@"
fi
""")
    launcher.chmod(0o755)

    # Also include a direct python entry
    (dist_dir / "run.py").write_text("""#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from kido_cli.cli import main
main()
""")


def create_github_release(token, version, assets, dry_run=False):
    """Create a GitHub Release and upload assets."""
    print(f"\n🚀 Creating GitHub Release v{version}...")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

    body = f"""## 🧒 KIDO v{version}

### What's New
- See [CHANGELOG](https://github.com/kido-lang/kido/blob/main/CHANGELOG.md) for details

### Installation
```bash
# Unix (Linux/macOS)
curl -fsSL https://kido.dev/install.sh | sh

# Windows (PowerShell)
iwr https://kido.dev/install.ps1 | iex

# Windows (cmd)
curl -L https://kido.dev/install.bat | cmd
```

### Assets
| File | Description |
|------|-------------|
| `kido-sdk-linux.tar.gz` | Linux SDK bundle |
| `kido-sdk-macos.tar.gz` | macOS SDK bundle |
| `kido-sdk-windows.zip` | Windows SDK bundle |
"""

    data = json.dumps(
        {
            "tag_name": f"v{version}",
            "name": f"KIDO v{version}",
            "body": body,
            "draft": False,
            "prerelease": False,
        }
    ).encode()

    if dry_run:
        print(f"  [DRY-RUN] Would create release v{version}")
        for asset in assets:
            print(f"  [DRY-RUN] Would upload: {asset.name}")
        return

    # Create release
    req = Request(f"{GITHUB_API}/releases", data=data, headers=headers, method="POST")
    try:
        resp = urlopen(req)
        release = json.loads(resp.read())
        release_id = release["id"]
        print(f"  ✅  Release created: {release['html_url']}")
    except HTTPError as e:
        err_body = e.read().decode()
        print(f"  ❌  Failed to create release: {err_body}")
        return

    # Upload each asset
    upload_url = release["upload_url"].replace("{?name,label}", "")
    for asset_path in assets:
        asset_name = asset_path.name
        print(f"  📤  Uploading {asset_name}...")
        try:
            with open(asset_path, "rb") as f:
                data = f.read()
            upload_headers = {
                **headers,
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(data)),
            }
            req = Request(
                f"{upload_url}?name={asset_name}",
                data=data,
                headers=upload_headers,
                method="POST",
            )
            urlopen(req)
            print(f"      ✅  Uploaded")
        except HTTPError as e:
            print(f"      ❌  Upload failed: {e.read().decode()}")


def main():
    parser = argparse.ArgumentParser(description="KIDO Release Pipeline")
    parser.add_argument("--token", required=True, help="GitHub token")
    parser.add_argument("--version", default="1.1.0", help="Release version")
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't create release, just build"
    )
    args = parser.parse_args()

    version = args.version

    # Determine which platforms to build for
    current_system = platform.system().lower()
    if current_system == "windows":
        systems = ["windows"]
    elif current_system == "darwin":
        systems = ["macos"]
    else:
        systems = ["linux"]

    # Build bundles
    assets = []
    for system_name in systems:
        archive, checksum = build_sdk(system_name, version)
        assets.append(archive)
        assets.append(checksum)

    # Create release
    create_github_release(args.token, version, assets, dry_run=args.dry_run)

    print("\n✅  Release pipeline complete!")


if __name__ == "__main__":
    main()
