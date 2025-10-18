#!/usr/bin/env python3
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader
import subprocess
import sys
from pathlib import Path

def run_command(cmd, log_file, cwd="."):
    """Run a command quietly, sending stdout/stderr to a log file."""
    with open(log_file, "w", encoding="utf-8") as log:
        result = subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)} (see {log_file})")
        sys.exit(result.returncode)

def cleanup_intermediate_files(build_dir: Path):
    """Remove all non-PDF files from build directory."""
    print("🧹 Cleaning up intermediate files...")
    for file in build_dir.glob("*"):
        if file.suffix.lower() != ".pdf":
            try:
                file.unlink()
            except Exception as e:
                print(f"⚠️ Warning: could not delete {file}: {e}")

def render_resume(lang):
    data_file = Path(f"data/{lang}.yaml")
    build_dir = Path("build")
    logs_dir = Path("logs")
    output_tex = build_dir / f"{lang}.tex"
    output_pdf = build_dir / f"{lang}.pdf"

    # Load YAML data
    with data_file.open("r", encoding="utf-8") as f:
        context = yaml.safe_load(f)
    context["lang"] = lang

    # Configure Jinja2 (safe delimiters for LaTeX)
    env = Environment(
        loader=FileSystemLoader("templates"),
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((#",
        comment_end_string="#))",
        autoescape=False,
    )

    # Render main and sidebar templates
    main_tex = env.get_template("main.tex.j2").render(**context)
    sidebar_tex = env.get_template("sidebar.tex.j2").render(**context)

    # Ensure directories exist
    build_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    # Copy cls file and profile_picture to build dir
    cls_file = Path("altacv.cls")
    picture_file = Path("profile_picture.png")
    if cls_file.exists() and picture_file.exists():
        shutil.copy(cls_file, build_dir / cls_file.name)
        shutil.copy(picture_file, build_dir / picture_file.name)
    else:
        print("⚠️ Warning: altacv.cls or profile_picture.jpg not found in project root!")
        return
    
    # Write rendered .tex files
    sidebar_file = build_dir / "sidebar.tex"
    sidebar_file.write_text(sidebar_tex, encoding="utf-8")
    output_tex.write_text(main_tex, encoding="utf-8")

    print(f"🧩 Compiling {lang}.tex → PDF...")

    # Paths for log files
    log1 = logs_dir / f"{lang}_pdflatex1.log"
    log2 = logs_dir / f"{lang}_biber.log"
    log3 = logs_dir / f"{lang}_pdflatex2.log"
    log4 = logs_dir / f"{lang}_pdflatex3.log"

    # Run LaTeX toolchain quietly (logs in /logs)
    run_command(
        ["pdflatex", "-interaction=nonstopmode", f"{lang}.tex"],
        log_file=log1,
        cwd=build_dir,
    )
    run_command(
        ["biber", str(output_tex.with_suffix(""))],
        log_file=log2,
    )
    run_command(
        ["pdflatex", "-interaction=nonstopmode", f"{lang}.tex"],
        log_file=log3,
        cwd=build_dir,
    )
    run_command(
        ["pdflatex", "-interaction=nonstopmode", f"{lang}.tex"],
        log_file=log4,
        cwd=build_dir,
    )

    if output_pdf.exists():
        print(f"✅ Successfully generated {output_pdf}")
    else:
        print(f"❌ Failed to generate {output_pdf}. Check {logs_dir}/ for details.")

    cleanup_intermediate_files(build_dir)
    print("✨ Done.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate.py [english|french]")
        sys.exit(1)
    render_resume(sys.argv[1])
