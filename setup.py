from setuptools import setup, find_packages

setup(
    name="youtube-shorts-automation",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-api-python-client",
        "google-auth-oauthlib",
        "requests",
        "python-dotenv",
    ],
) 