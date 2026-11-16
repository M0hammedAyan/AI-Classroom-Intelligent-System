# Update timetable.py
with open('vista/backend/app/models/timetable.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_slot = '''class TimetableSlot(Base):
    """One period/slot in the weekly timetable."""
    __tablename__ = "timetable_slots"

    id = Column(Text, primary_key=True)
    class_section_id = Column(Text, ForeignKey("class_sections.id"), nullable=False)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Text, ForeignKey("users.id"), nullable=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 1=Tuesday ... 4=Friday
    start_time = Column(Text, nullable=False)       # "09:00"
    end_time = Column(Text, nullable=False)         # "10:00"
    room = Column(Text, nullable=True)              # "Room 301"
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)'''

new_slot = '''class TimetableSlot(Base):
    """One period/slot in the weekly timetable."""
    __tablename__ = "timetable_slots"

    id = Column(Text, primary_key=True)
    class_section_id = Column(Text, ForeignKey("class_sections.id"), nullable=False)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=True)
    teacher_id = Column(Text, ForeignKey("users.id"), nullable=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday ... 5=Saturday
    start_time = Column(Text, nullable=False)       # "09:00"
    end_time = Column(Text, nullable=False)         # "09:55"
    room = Column(Text, nullable=True)              # "Room A-302"
    period_label = Column(Text, nullable=True)      # "S1", "S2", "TEA BREAK", "LUNCH"
    slot_type = Column(Text, nullable=False, default="teaching")  # teaching | lab | free | break | non_teaching
    batch = Column(Text, nullable=True)             # "B1", "B2", "B3" or None
    is_unconfirmed = Column(Boolean, default=False)
    effective_from = Column(Text, nullable=True)    # "2026-08-03"
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)'''

text = text.replace(old_slot.replace('\r\n', '\n'), new_slot.replace('\r\n', '\n'))
text = text.replace(old_slot, new_slot)
with open('vista/backend/app/models/timetable.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Update student.py
with open('vista/backend/app/models/student.py', 'r', encoding='utf-8') as f:
    st_text = f.read()

old_st = '    extracurricular = Column(Text, nullable=True)      # JSON array of activities'
new_st = '    extracurricular = Column(Text, nullable=True)      # JSON array of activities\n    batch = Column(Text, nullable=True)                # Lab batch (e.g. B1, B2, B3)'

st_text = st_text.replace(old_st, new_st)
with open('vista/backend/app/models/student.py', 'w', encoding='utf-8') as f:
    f.write(st_text)

# Update attendance.py
with open('vista/backend/app/models/attendance.py', 'r', encoding='utf-8') as f:
    att_text = f.read()

old_att = '    source = Column(Text, nullable=False, default="face")  # face | manual | seed\n    created_at = Column(Text, nullable=False)'
new_att = '''    source = Column(Text, nullable=False, default="face")  # face | manual | seed
    slot_id = Column(Text, ForeignKey("timetable_slots.id"), nullable=True)
    period_label = Column(Text, nullable=True)
    is_extra_class = Column(Boolean, nullable=False, default=False)
    extra_class_reason = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)'''

att_text = att_text.replace(old_att.replace('\r\n', '\n'), new_att.replace('\r\n', '\n'))
att_text = att_text.replace(old_att, new_att)
with open('vista/backend/app/models/attendance.py', 'w', encoding='utf-8') as f:
    f.write(att_text)

print('Models updated successfully')
