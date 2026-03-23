"""Flask web app for README Studio."""

import os

import markdown
from flask import Flask, render_template, request, redirect, url_for

from generator import ProjectInfo, generate_readme, generate_readme_offline
from launch_kit import format_launch_kit_markdown

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "readme-studio-dev-key")


@app.route("/")
def index():
    """Landing page with the project form."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Process form input and generate README."""
    # Collect form data
    name = request.form.get("name", "").strip()
    one_liner = request.form.get("one_liner", "").strip()

    if not name or not one_liner:
        return render_template("index.html", error="Project name and one-liner are required.")

    project = ProjectInfo(
        name=name,
        one_liner=one_liner,
        language=request.form.get("language", "Python"),
        tech_stack=request.form.get("tech_stack", ""),
        commands=request.form.get("commands", ""),
        features=request.form.get("features", ""),
        install_steps=request.form.get("install_steps", ""),
        license_type=request.form.get("license_type", "MIT"),
        extra_notes=request.form.get("extra_notes", ""),
    )

    offline = request.form.get("offline") == "1"
    want_launch_kit = request.form.get("launch_kit") == "1"

    try:
        # Generate README
        if offline or not os.environ.get("OPENAI_API_KEY"):
            result = generate_readme_offline(project)
            if not offline and not os.environ.get("OPENAI_API_KEY"):
                # Soft warning: fell back to offline
                pass
        else:
            result = generate_readme(project)

        # Render markdown to HTML
        md_extensions = [
            "fenced_code",
            "tables",
            "codehilite",
            "toc",
            "nl2br",
        ]
        rendered_html = markdown.markdown(result.markdown, extensions=md_extensions)

        # Generate launch kit if requested
        launch_kit_data = None
        if want_launch_kit and not offline and os.environ.get("OPENAI_API_KEY"):
            try:
                from generator import generate_launch_kit
                launch_kit_data = generate_launch_kit(project)
            except Exception as e:
                launch_kit_data = {"error": str(e)}

        return render_template(
            "result.html",
            project_name=name,
            raw_markdown=result.markdown,
            rendered_html=rendered_html,
            launch_kit=launch_kit_data,
        )

    except Exception as e:
        return render_template("index.html", error=f"Generation failed: {str(e)}")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """JSON API endpoint for programmatic access."""
    import json
    from flask import jsonify

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    name = data.get("name", "").strip()
    one_liner = data.get("one_liner", "").strip()

    if not name or not one_liner:
        return jsonify({"error": "name and one_liner are required"}), 400

    project = ProjectInfo(
        name=name,
        one_liner=one_liner,
        language=data.get("language", "Python"),
        tech_stack=data.get("tech_stack", ""),
        commands=data.get("commands", ""),
        features=data.get("features", ""),
        install_steps=data.get("install_steps", ""),
        license_type=data.get("license_type", "MIT"),
        extra_notes=data.get("extra_notes", ""),
    )

    offline = data.get("offline", False)

    try:
        if offline or not os.environ.get("OPENAI_API_KEY"):
            result = generate_readme_offline(project)
        else:
            result = generate_readme(project)

        response = {
            "name": name,
            "markdown": result.markdown,
            "sections": result.sections,
        }

        if data.get("launch_kit") and not offline and os.environ.get("OPENAI_API_KEY"):
            try:
                from generator import generate_launch_kit
                response["launch_kit"] = generate_launch_kit(project)
            except Exception as e:
                response["launch_kit_error"] = str(e)

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
