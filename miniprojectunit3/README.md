# Student Record & Academic Management Platform

Mini-project implementation aligned with the supplied DevOps assignment: student records, course names, marks/GPA-style academic tracking, API endpoint, automated tests, Dockerfile and Jenkins pipeline.

## Run locally

Requires Python 3.10+; no external package is needed for this offline demo.

```bash
python app.py
```
Open http://127.0.0.1:8000. The app seeds four sample student records into `students.db` on first run.

## Features
- Dashboard cards: student count, average marks, active courses and high performers.
- Search/filter student list.
- Add and delete student records.
- SQLite persistence, JSON endpoint at `/api/students`, health endpoint at `/health`, CSV export at `/export`.
- Duplicate roll-number validation and marks range validation.
- Unit/integration tests under `tests/`.
- Dockerfile and Jenkins pipeline example.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## DevOps assignment mapping
- Version control: commit this folder to Git and push to GitHub.
- CI: Jenkinsfile runs the test suite.
- Containerization: Dockerfile packages the app.
- Kubernetes/Minikube: create a Deployment and NodePort Service after building the image. This environment did not have Docker/Kubernetes or Flask installed and network access was unavailable, so screenshots show the real app running using Python's standard-library HTTP server. The core demo and tests were executed locally here; do not claim a Docker/Kubernetes deployment was executed.

For an environment with internet access, install dependencies with `pip install -r requirements.txt`; this demo itself intentionally uses the standard library to remain runnable offline.
