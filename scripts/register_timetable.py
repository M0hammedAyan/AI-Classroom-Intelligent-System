# Update routes/__init__.py
with open('vista/backend/app/routes/__init__.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'timetable' not in text:
    text += "\nfrom .timetable import router as timetable_router\n__all__.append('timetable_router')\n"
    with open('vista/backend/app/routes/__init__.py', 'w', encoding='utf-8') as f:
        f.write(text)

# Update main.py
with open('vista/backend/app/main.py', 'r', encoding='utf-8') as f:
    m_text = f.read()

if 'timetable' not in m_text:
    m_text = m_text.replace(
        'from .routes import auth, attendance, students, risk, export, enroll, lms, admin, dashboards, student_portal, notifications, reports, academics, coach',
        'from .routes import auth, attendance, students, risk, export, enroll, lms, admin, dashboards, student_portal, notifications, reports, academics, coach, timetable'
    )
    m_text = m_text.replace(
        'app.include_router(academics.router)',
        'app.include_router(academics.router)\napp.include_router(timetable.router)'
    )
    with open('vista/backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(m_text)

print("Registered timetable router in main.py and routes/__init__.py")
