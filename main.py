import argparse
import os
import requests
import shutil
from distutils.core import setup
from setuptools import find_packages

LICENSE_TEMPLATES = {
    "mit": "https://raw.githubusercontent.com/OpenSourceInitiative/licenses/master/MIT",
    "apache-2.0": "https://raw.githubusercontent.com/apache/licenses/master/LICENSE-2.0",
    "gpl-3.0": "https://raw.githubusercontent.com/tldr-pages/tldr/master/licenses/gpl-3.0.md",
}


def create_package(project_dir, toml_content, license_type, readme_path):
    """
    Creates a Python package in the specified directory.

    Args:
        project_dir (str): The directory where the package will be created.
        toml_content (str): The content of the pyproject.toml file.
        license_type (str): The type of license to use (e.g., "mit", "apache-2.0", "gpl-3.0").
        readme_path (str): The path to the README.md file to copy, or None to create an empty one.
    """

    # Create pyproject.toml file
    with open(os.path.join(project_dir, "pyproject.toml"), "w") as f:
        f.write(toml_content)

    # Create LICENSE file
    if license_type:
        license_url = LICENSE_TEMPLATES.get(license_type.lower())
        if not license_url:
            raise ValueError(f"Invalid license type: {license_type}")
        response = requests.get(license_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch license template from {license_url}")
        with open(os.path.join(project_dir, "LICENSE"), "w") as f:
            f.write(response.text)

    # Create README.md file
    readme_file = os.path.join(project_dir, "README.md")
    if readme_path:
        shutil.copyfile(readme_path, readme_file)
    else:
        with open(readme_file, "w") as f:
            f.write(f"# {toml_content.splitlines()[0].split('=')[1].strip()}")

    # Ensure pip and setuptools are up-to-date (optional)
    try:
        import pip
        pip.main(["install", "-U", "pip", "setuptools"])
    except ImportError:
        print("Warning: pip or setuptools is not installed. Package creation might fail.")

    # Generate distribution files (optional)
    try:
        os.system("py -m pip install --upgrade build")
        setup(
            name=find_packages(where=project_dir)[0],  # Assuming single package structure
            packages=find_packages(where=project_dir),
            # ... other setup arguments based on your project structure
        )
    except Exception as e:
        print(f"Error generating distribution files: {e}")

    print(f"Package created successfully in: {project_dir}")


def main():
    parser = argparse.ArgumentParser(description="Create a Python package with options")
    parser.add_argument("project_dir", help="The directory where the package will be created")
    parser.add_argument(
        "--toml", help="Path to a pyproject.toml file or content as a string", required=True
    )
    parser.add_argument(
        "--license",
        help="Type of license to include (e.g., mit, apache-2.0, gpl-3.0)",
    )
    parser.add_argument(
        "--readme", help="Path to an existing README.md file (optional)", default=None
    )

    args = parser.parse_args()

    # Handle pyproject.toml content from file or argument
    toml_content = ""
    if os.path.isfile(args.toml):
        with open(args.toml, "r") as f:
            toml_content = f.read()
    else:
        toml_content = args.toml

    create_package(args.project_dir, toml_content)
