FROM python:3.10

# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app

COPY src src
COPY setup.py setup.py
COPY pyproject.toml pyproject.toml
RUN pip install --no-cache-dir ".[gradio]"

COPY model_licenses model_licenses
COPY LICENSE LICENSE

# Copy this last for quicker image builds
# when only modifying the Gradio UI
COPY stackhpc-app stackhpc-app

ENTRYPOINT ["fastapi", "run", "stackhpc-app/api_server.py"]