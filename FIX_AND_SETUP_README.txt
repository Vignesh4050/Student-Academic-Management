STUDENT ACADEMIC MANAGEMENT - ROLE AND DASHBOARD FIX

Changes in this package
-----------------------
1. Academic and People list pages are available to authenticated users.
2. ADMIN/superuser accounts can create, edit and delete programmes, courses,
   semesters, students, faculty profiles and subjects.
3. FACULTY accounts get read-only academic views limited to assigned subjects
   and students enrolled in those subjects' course/semester.
4. STUDENT accounts get read-only views limited to their own student profile,
   their course/semester, their relevant subjects and associated faculty.
5. Create User is shown only to ADMIN/superuser accounts, and the view itself
   rejects non-admin requests with HTTP 403.
6. Dashboard calculations are role-scoped and include the context fields used
   by the template. The dashboard uses a responsive custom CSS grid.
7. Dashboard Chart.js code now renders in the base template's extra_scripts
   block (the previous template used a mismatched block name).
8. Project-level static CSS directory is registered in settings.py.

Install / run on Windows PowerShell
-----------------------------------
Open PowerShell in the folder that contains manage.py, then run:

  py -3.11 -m venv venv
  .\venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  python manage.py check
  python manage.py migrate
  python manage.py runserver

The database settings in config/settings.py still point to the project's
local MariaDB database. Make sure MariaDB is running and the database/user
configured there exist before running migrations.

Role permissions
----------------
- ADMIN: full academic/people CRUD access.
- FACULTY: read-only academic/people directory access scoped to assigned
  subjects and the students taking those subjects.
- STUDENT: read-only access to their own profile, programme/course/semester,
  relevant subjects, and the faculty assigned to their course/semester.
- All role checks are enforced server-side; hiding buttons is not the only
  protection. Direct create/edit/delete URLs are protected as well.

Validation note
---------------
The files were syntax-checked with Python. A complete Django system check and
DB-backed runtime test must be run on the target Windows PC with its installed
Django dependencies and MariaDB database.
