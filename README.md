# AI Resume Builder

A Django-based web application to create, manage and download professional resumes and cover letters. The project supports user accounts, profile editing, resume templates, portfolio generation, Cloudinary media storage, email delivery via SMTP, and PDF export (WeasyPrint preferred; ReportLab fallback for Windows).

**Key Links**
- Manage script: [manage.py](manage.py)
- Requirements: [requirements.txt](requirements.txt)
- Settings: [core/settings.py](core/settings.py)
- Resume utilities (PDF generation): [resume/utils.py](resume/utils.py)
- Countries & phone codes: [resume/countries_data.py](resume/countries_data.py)
- Profile edit template: [templates/resume/profile_edit.html](templates/resume/profile_edit.html)

**Project Structure (high level)**
- `manage.py` — Django management entry
- `core/` — Django project settings, urls, WSGI/ASGI
- `resume/` — Main app: models, views, forms, utilities (PDF, countries, templates)
- `users/` — Custom user, auth, forms and views
- `templates/` — HTML templates
- `static/`, `staticfiles/` — CSS/JS and collected static bundles
- `media/` — local media folder (project uses Cloudinary in production)
- `requirements.txt` — pinned Python dependencies

---

**Features**
- User signup/login/logout, profile management
- Resume creation from templates (modern, classic, creative, minimal, executive, technical)
- Cover letter generation and management
- Portfolio generation
- PDF download for resumes, portfolios, cover letters
  - Uses WeasyPrint when GTK dependencies are present (Linux/macOS); falls back to ReportLab on Windows
- Cloudinary integration for media storage (images, thumbnails)
- Email sending via SMTP (account verification, notifications)
- Admin panel customizations and management commands

---

Getting Started (Windows-focused)

1. Prerequisites
   - Python 3.12 (project tested with 3.12)
   - Git (optional)
   - For full WeasyPrint support (optional): GTK and its dependencies (hard to install on Windows) — see Troubleshooting below. ReportLab fallback is available.

2. Clone repository (if applicable)

```bash
git clone <repo-url>
cd ai-resume-builder
```

3. Create and activate a virtual environment (recommended)

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Notes:
- The project includes `django-cloudinary-storage`, `django-crispy-forms`, `weasyprint`, and `reportlab` in `requirements.txt`.
- On Windows, `weasyprint` installs but requires external GTK libraries for full functionality; the app falls back to ReportLab.

5. Environment variables / `.env`
Create a `.env` file or set environment variables for local development. Example `.env` entries used by `core/settings.py`:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
CLOUDINARY_URL=cloudinary://<key>:<secret>@<cloud_name>  # optional in development
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=yourpassword
EMAIL_USE_TLS=True
```

6. Database migrations

```bash
python manage.py migrate
```

7. Create a superuser

```bash
python manage.py createsuperuser
```

8. Run development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ and test features.

---

Configuration Details

- Settings file: [core/settings.py](core/settings.py)
  - Database: default is SQLite (`db.sqlite3`) via `DATABASES` or can be configured with `DATABASE_URL`.
  - Media storage: uses Cloudinary when `django-cloudinary-storage` is configured. In `core/settings.py` you will find Cloudinary related settings and instructions.
  - Email: SMTP settings are read from env vars.

- Cloudinary
  - If you want media stored in Cloudinary, add `CLOUDINARY_URL` or configure `CLOUDINARY_*` settings in the environment. See `settings.py` for required keys and `django-cloudinary-storage` docs.

- WeasyPrint vs ReportLab
  - `WeasyPrint` is the preferred renderer for HTML → PDF (better CSS support). On Windows it requires GTK and other system libraries (libgobject, pango, cairo). If these are missing, the project uses a ReportLab-based fallback implemented in `resume/utils.py`.
  - File: [resume/utils.py](resume/utils.py) — contains the fallback `generate_pdf_with_reportlab()` and main `generate_pdf_from_html()` logic.

---

Running tests

```bash
python manage.py test
```

Note: Some tests might require external dependencies or environment variables.

---

Static files & media

- Development: static files are served by Django's `runserver` when `DEBUG=True`.
- Production: run `python manage.py collectstatic` and serve static files via a web server or CDN.

```bash
python manage.py collectstatic --noinput
```

Media uploads:
- In development, `media/` is used
- In production, configure Cloudinary in env vars so uploaded media go to Cloudinary

---

Troubleshooting & Platform Notes

- WeasyPrint on Windows
  - WeasyPrint requires GTK libs: `gobject-2.0`, `pango`, `cairo` etc. Installing these on Windows can be complex; see WeasyPrint docs: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
  - The app has a ReportLab fallback. If you see errors mentioning `gobject-2.0-0` or `cannot load library 'gobject-2.0-0'`, PDF generation will still work via ReportLab.

- Missing Python package errors
  - Activate the virtualenv and run `pip install -r requirements.txt`.
  - If `pip` warns about user installs or PATH, ensure your virtualenv is activated and `python` resolves to the venv interpreter.

- Space in Windows path
  - If you run Python using an absolute path with spaces, wrap it in quotes or use PowerShell's call operator: `& 'C:/path with spaces/.venv/Scripts/python.exe' manage.py runserver`.

---

Developer Notes & Useful Files

- PDF logic and fallback: [resume/utils.py](resume/utils.py)
- Country list and phone codes (used in profile phone field and phone code dropdown): [resume/countries_data.py](resume/countries_data.py)
- Profile edit form & phone country code widget: [users/forms.py](users/forms.py) and [templates/resume/profile_edit.html](templates/resume/profile_edit.html)
- Where routes live: [core/urls.py](core/urls.py) and app `urls.py` files

---

Contributing

- Please open issues or PRs for improvements.
- Follow PEP8 and use existing code style.
- Run tests and ensure no failing tests before submitting PRs.

---

License

Add your license here (MIT, Apache 2.0, etc.) or remove this section if proprietary.

---

Contact

For questions about this codebase, include your contact details or open an issue in the originating repository.
