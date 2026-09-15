from flask import Flask,render_template,request,redirect,session,url_for
from datetime import datetime

from models import (
    db,
    User,
    LostFound,
    Notice,
    Expense,
    Note,
    Assignments,
    OldPaper,
    TeacherCode,
    NewsEvent,
    StudentRequest,
    Payment,
    Attendance,
    Gallery
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
import secrets

app = Flask(__name__)

# Upload Folders

NOTES_UPLOAD_FOLDER = "static/uploads/notes"

PAPERS_UPLOAD_FOLDER = "static/uploads/papers"

ASSIGNMENT_UPLOAD_FOLDER = "static/uploads/assignments"

GALLERY_UPLOAD_FOLDER = "static/uploads/gallery"

app.config['NOTES_UPLOAD_FOLDER'] = NOTES_UPLOAD_FOLDER

app.config['PAPERS_UPLOAD_FOLDER'] = PAPERS_UPLOAD_FOLDER

app.config['ASSIGNMENT_UPLOAD_FOLDER'] = ASSIGNMENT_UPLOAD_FOLDER

app.config['GALLERY_UPLOAD_FOLDER'] = GALLERY_UPLOAD_FOLDER

os.makedirs(GALLERY_UPLOAD_FOLDER, exist_ok=True)

print("Current Folder:", os.getcwd())

app.config['SECRET_KEY'] = 'campusCloudsecret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

with app.app_context():
    db.create_all()

    try:
        db.session.execute(
            db.text(
                "ALTER TABLE note ADD COLUMN status VARCHAR(20) DEFAULT 'Pending'"
            )
        )
        db.session.commit()
        print("Note status column added successfully.")

    except Exception:
        db.session.rollback()

    try:
        db.session.execute(
            db.text(
                "ALTER TABLE notice ADD COLUMN upload_date DATETIME"
            )
        )
        db.session.commit()
        print("Notice upload_date column added successfully.")

    except Exception:
        db.session.rollback()

# =========================================================
# AUTO COMPLETE STUDENT REQUEST
# =========================================================

def complete_matching_request(
    request_type,
    subject,
    semester,
    course=None,
    institution=None
):

    pending_requests = StudentRequest.query.filter_by(
        status='Pending',
        request_type=request_type
    ).all()

    for req in pending_requests:

        # Subject aur semester match hona zaroori hai
        if req.subject.strip().lower() != subject.strip().lower():
            continue

        if req.semester.strip().lower() != semester.strip().lower():
            continue

        # Question Paper ke liye Course bhi match karo
        if request_type == "Question Paper":

            if course:
                if req.course.strip().lower() != course.strip().lower():
                    continue

            # Institution optional matching
            if institution:
                if req.institution.strip().lower() != institution.strip().lower():
                    continue

        req.status = "Completed"

    db.session.commit()

@app.route('/')
def home():

    gallery_images = Gallery.query.order_by(
        Gallery.id.desc()
    ).all()

    requests = StudentRequest.query.filter_by(
        status='Pending'
    ).order_by(
        StudentRequest.id.desc()
    ).all()

    return render_template(
        'public/index.html',
        gallery_images=gallery_images,
        requests=requests
    )

@app.route('/online-admission')
def online_admission():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'public/online_admission.html'
    )

@app.route('/university-examination')
def university_examination():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'public/university_examination.html'
    )

@app.route('/university-recruitment')
def university_recruitment():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'public/university_recruitment.html'
    )

@app.route('/digital-e-content')
def digital_e_content():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'public/digital_e_content.html'
    )

@app.route('/nep-old-syllabus')
def nep_old_syllabus():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'public/nep_old_syllabus.html'
    )

@app.route('/student-request', methods=['POST'])
def student_request():

    name = request.form['name']
    institution = request.form['institution']
    course = request.form['course']
    semester = request.form['semester']
    subject = request.form['subject']
    request_type = request.form['request_type']
    requirement = request.form['requirement']

    user_id = session.get('user_id')

    new_request = StudentRequest(
        name=name,
        institution=institution,
        course=course,
        semester=semester,
        subject=subject,
        request_type=request_type,
        requirement=requirement,
        user_id=user_id,
        status='Pending'
    )

    db.session.add(new_request)
    db.session.commit()

    return redirect('/')

@app.route('/admin/student-requests')
def admin_student_requests():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    requests = StudentRequest.query.order_by(
        StudentRequest.id.desc()
    ).all()

    return render_template(
        'admin/student_requests.html',
        requests=requests
    )

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # Basic details
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Optional fields
        mobile = request.form.get('mobile', '')
        parent_name = request.form.get('parent_name', '')
        enrollment_no = request.form.get('enrollment_no', '')
        college = request.form.get('college', '')
        course = request.form.get('course', '')
        branch = request.form.get('branch', '')
        semester = request.form.get('semester', '')
        address = request.form.get('address', '')

        # Selected role
        role = request.form.get('role', 'student')

        # Teacher/Admin codes
        teacher_code_value = request.form.get('teacher_code', '').strip()

        admin_code = request.form.get('admin_code', '').strip()
        admin_code = admin_code.replace('"', "").replace("'", "")

        # ==============================
        # Password Validation
        # ==============================

        if password != confirm_password:
            return "Password and Confirm Password do not match."

        if len(password) < 8:
            return "Password must be at least 8 characters."

        if len(password) > 20:
            return "Password must not exceed 20 characters."

        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter."

        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter."

        if not re.search(r"\d", password):
            return "Password must contain at least one number."

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must contain at least one special character."

        # ==============================
        # Role Validation
        # ==============================

        if role not in ['student', 'teacher','staff', 'admin']:
            return "Invalid role selected."

        teacher_code = None

        # ==============================
        # Admin
        # ==============================

        if role == 'admin':

            if admin_code != "CAMPUSCLOUD2026":
                return "Invalid Admin Code"

            assigned_role = "admin"

        # ==============================
        # Teacher
        # ==============================

        elif role == 'teacher':

            teacher_code = TeacherCode.query.filter_by(
                code=teacher_code_value,
                is_used=False
            ).first()

            if not teacher_code:
                return "Invalid or already used Teacher Code"

            assigned_role = "teacher"

        # ==============================
        # Staff
        # ==============================

        elif role == 'staff':

            assigned_role = "staff"

        # ==============================
        # Student
        # ==============================

        else:

            assigned_role = "student"

        # ==============================
        # Check Existing Email
        # ==============================

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered"

        # ==============================
        # Create User
        # ==============================

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),

            mobile=mobile,
            parent_name=parent_name,
            enrollment_no=enrollment_no,
            college=college,
            course=course,
            branch=branch,
            semester=semester,
            address=address,

            role=assigned_role
        )

        db.session.add(user)

        # User ID generate karne ke liye
        db.session.flush()

        # ==============================
        # Mark Teacher Code as Used
        # ==============================

        if assigned_role == 'teacher':

            teacher_code.is_used = True
            teacher_code.used_by = user.id

        db.session.commit()

        return redirect('/')

    return render_template('public/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            print("Login role:", user.role)

            session['user_id'] = user.id
            session['user_name'] = user.name
            session['role'] = user.role

            if user.role == "admin":
                return redirect('/admin_dashboard')

            elif user.role == "teacher":
                return redirect('/teacher_dashboard')

            elif user.role == "staff":
                return redirect('/staff_dashboard')

            else:
                return redirect('/dashboard')
        return "Invalid Email or Password"

    return render_template('public/login.html')

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    total_expenses = Expense.query.filter_by(
        user_id=session['user_id']
    ).count()

    total_notices = Notice.query.filter_by(
        user_id=session['user_id']
    ).count()

    total_lost_items = LostFound.query.filter_by(
        user_id=session['user_id']
    ).count()

    return render_template(
        'student/dashboard.html',
        username=session['user_name'],
        total_expenses=total_expenses,
        total_notices=total_notices,
        total_lost_items=total_lost_items
    )

@app.route('/teacher_dashboard')
def teacher_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'teacher':
        return redirect('/dashboard')

    return render_template(
        'teacher/dashboard.html',
        username=session['user_name']
    )

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    total_students = User.query.filter_by(role="student").count()
    total_admins = User.query.filter_by(role="admin").count()
    total_notices = Notice.query.count()
    total_lost_items = LostFound.query.count()
    total_expenses = Expense.query.count()

    return render_template(
        'admin/admin_dashboard.html',
        total_students=total_students,
        total_admins=total_admins,
        total_notices=total_notices,
        total_lost_items=total_lost_items,
        total_expenses=total_expenses
    )
@app.route('/staff_dashboard')
def staff_dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'staff':
        return redirect('/dashboard')

    return render_template(
        'staff/staff_dashboard.html'
    )

@app.route('/admin/teachers')
def admin_teachers():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    teachers = User.query.filter_by(role='teacher').all()

    codes = TeacherCode.query.order_by(
        TeacherCode.id.desc()
    ).all()

    return render_template(
        'admin/teachers.html',
        teachers=teachers,
        codes=codes
    )

@app.route('/admin/teachers/generate', methods=['POST'])
def admin_generate_teacher_code():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    # Unique Teacher Code generate karo
    while True:

        code = "TEACHER-" + secrets.token_hex(4).upper()

        existing_code = TeacherCode.query.filter_by(
            code=code
        ).first()

        if not existing_code:
            break

    # Database me code save karo
    new_code = TeacherCode(
        code=code,
        is_used=False
    )

    db.session.add(new_code)
    db.session.commit()

    return redirect('/admin/teachers')

@app.route('/admin/teachers/add', methods=['POST'])
def admin_add_teacher():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered"

    # Password hash
    hashed_password = generate_password_hash(password)

    # Create teacher
    teacher = User(
        name=name,
        email=email,
        password=hashed_password,
        role='teacher'
    )

    db.session.add(teacher)
    db.session.commit()

    return redirect('/admin/teachers')


@app.route('/manage-users')
def manage_users():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    students = User.query.filter_by(role='student').all()

    return render_template(
        'admin/manage_users.html',
        students=students
    )

@app.route('/admin/notices', methods=['GET', 'POST'])
def admin_notices():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        new_notice = Notice(
            title=title,
            content=content,
            user_id=session['user_id']
        )

        db.session.add(new_notice)
        db.session.commit()

        return redirect('/admin/notices')

    notices = Notice.query.all()

    return render_template(
        'admin/notices.html',
        notices=notices,
        edit_notice=None
    )

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':

        user.name = request.form['name']
        user.email = request.form['email']
        user.mobile = request.form.get('mobile', '')
        user.address = request.form.get('address', '')

        db.session.commit()

        session['user_name'] = user.name

        return redirect('/profile')

    return render_template(
        'student/edit_profile.html',
        user=user
    )

@app.route('/delete-notice/<int:notice_id>')
def delete_notice(notice_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    notice = db.session.get(Notice, notice_id)

    if not notice:
        return redirect('/admin/notices')

    db.session.delete(notice)
    db.session.commit()

    return redirect('/admin/notices')

@app.route('/admin/papers', methods=['GET', 'POST'])
def admin_papers():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        university = request.form['university']
        course = request.form['course']
        branch = request.form['branch']
        semester = request.form['semester']
        subject = request.form['subject']
        exam_year = request.form['exam_year']
        exam_type = request.form['exam_type']
        description = request.form['description']

        file = request.files['paper_file']

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config['PAPERS_UPLOAD_FOLDER'],
                filename
            )
        )

        paper = OldPaper(
            title=title,
            university=university,
            course=course,
            branch=branch,
            semester=semester,
            subject=subject,
            exam_year=exam_year,
            exam_type=exam_type,
            description=description,
            file_name=filename,
            user_id=session['user_id']
        )

        db.session.add(paper)
        db.session.commit()

        # Matching student request automatically complete karo
        complete_matching_request(
            request_type="Question Paper",
            subject=subject,
            semester=semester,
            course=course,
            institution=university
        )

        return redirect('/admin/papers')

    papers = OldPaper.query.all()

    return render_template(
        'admin/papers.html',
        papers=papers
    )
@app.route('/papers')
def papers():

    if 'user_id' not in session:
        return redirect('/login')

    papers = OldPaper.query.filter_by(
        status="Approved"
    ).all()

    return render_template(
        'student/paper.html',
        papers=papers
    )
# =========================================================
# VIEW QUESTION PAPER
# =========================================================

@app.route('/view-paper/<int:paper_id>')
def view_paper(paper_id):

    if 'user_id' not in session:
        return redirect('/login')

    paper = OldPaper.query.get_or_404(paper_id)

    if paper.status != 'Approved':
        return "This paper is not available.", 403

    return redirect(
        url_for(
            'static',
            filename='uploads/papers/' + paper.file_name
        )
    )
@app.route('/result')
def result():

    if 'user_id' not in session:
        return redirect('/login')

    # Future me database se result aayega
    results = [

        {
            "subject": "Python Programming",
            "obtained_marks": 85,
            "total_marks": 100,
            "grade": "A",
            "status": "Pass"
        },

        {
            "subject": "Database Management System",
            "obtained_marks": 90,
            "total_marks": 100,
            "grade": "A+",
            "status": "Pass"
        },

        {
            "subject": "Computer Networks",
            "obtained_marks": 78,
            "total_marks": 100,
            "grade": "B+",
            "status": "Pass"
        }

    ]

    total = sum(item["obtained_marks"] for item in results)

    max_marks = sum(item["total_marks"] for item in results)

    percentage = round((total / max_marks) * 100, 2)

    return render_template(
        "student/result.html",
        results=results,
        percentage=percentage
    )
@app.route('/timetable')
def timetable():

    if 'user_id' not in session:
        return redirect('/login')

    timetable = [

        {
            "day": "Monday",
            "period1": "Python",
            "period2": "DBMS",
            "period3": "Java",
            "period4": "Break",
            "period5": "CN",
            "period6": "Lab"
        },

        {
            "day": "Tuesday",
            "period1": "DBMS",
            "period2": "Python",
            "period3": "Math",
            "period4": "Break",
            "period5": "Java",
            "period6": "Lab"
        },

        {
            "day": "Wednesday",
            "period1": "CN",
            "period2": "Math",
            "period3": "Python",
            "period4": "Break",
            "period5": "DBMS",
            "period6": "Project"
        }

    ]

    return render_template(
        "student/timetable.html",
        timetable=timetable
    )
# =========================================================
# STUDENT ATTENDANCE
# =========================================================

@app.route('/attendance')
def attendance():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'student':
        return redirect('/dashboard')

    student_id = session['user_id']

    records = Attendance.query.filter_by(
        student_id=student_id
    ).order_by(
        Attendance.date.desc()
    ).all()

    attendance_data = {}

    for record in records:

        if record.subject not in attendance_data:
            attendance_data[record.subject] = {
                "total_classes": 0,
                "present_classes": 0,
                "medical_leave": 0
            }

        attendance_data[record.subject]["total_classes"] += 1

        if record.status == "Present":
            attendance_data[record.subject]["present_classes"] += 1

        elif record.status == "Medical Leave":
            attendance_data[record.subject]["medical_leave"] += 1

    attendance_list = []

    for subject, data in attendance_data.items():

        total = data["total_classes"]
        present = data["present_classes"]

        percentage = 0

        if total > 0:
            percentage = round(
                (present / total) * 100,
                2
            )

        attendance_list.append({
            "subject": subject,
            "total_classes": total,
            "present_classes": present,
            "medical_leave": data["medical_leave"],
            "percentage": percentage
        })

    total_classes = sum(
        item["total_classes"]
        for item in attendance_list
    )

    total_present = sum(
        item["present_classes"]
        for item in attendance_list
    )

    total_medical = sum(
        item["medical_leave"]
        for item in attendance_list
    )

    overall_attendance = 0

    if total_classes > 0:
        overall_attendance = round(
            (total_present / total_classes) * 100,
            2
        )

    return render_template(
        "student/attendance.html",
        attendance_list=attendance_list,
        overall_attendance=overall_attendance,
        total_classes=total_classes,
        total_present=total_present,
        total_medical=total_medical
    )

@app.route('/paper_practic')
def paper_practice():

    if 'user_id' not in session:
        return redirect('/login')

    questions = [

        {
            "question": "Explain DBMS Architecture."
        },

        {
            "question": "What is Normalization?"
        },

        {
            "question": "Explain Python Functions."
        },

        {
            "question": "Difference between TCP and UDP."
        },

        {
            "question": "Explain Operating System."
        }

    ]

    return render_template(
        "student/paper_practic.html",
        questions=questions
    )
@app.route('/teacher/papers', methods=['GET', 'POST'])
def teacher_papers():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'teacher':
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        university = request.form['university']
        course = request.form['course']
        branch = request.form['branch']
        semester = request.form['semester']
        subject = request.form['subject']
        exam_year = request.form['exam_year']
        exam_type = request.form['exam_type']
        description = request.form['description']

        file = request.files['paper_file']

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config['PAPERS_UPLOAD_FOLDER'],
                filename
            )
        )

        paper = OldPaper(
            title=title,
            university=university,
            course=course,
            branch=branch,
            semester=semester,
            subject=subject,
            exam_year=exam_year,
            exam_type=exam_type,
            description=description,
            file_name=filename,
            status="Pending",
            user_id=session['user_id']
        )

        db.session.add(paper)
        db.session.commit()

        # Matching student request automatically complete karo
        complete_matching_request(
            request_type="Question Paper",
            subject=subject,
            semester=semester,
            course=course,
            institution=university
        )

        return redirect('/teacher/papers')

    papers = OldPaper.query.filter_by(
        user_id=session['user_id']
    ).all()

    return render_template(
        'teacher/papers.html',
        papers=papers
    )

# =========================================================
# TEACHER NOTES
# =========================================================

@app.route('/teacher/notes', methods=['GET', 'POST'])
def teacher_notes():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'teacher':
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        subject = request.form['subject']
        semester = request.form['semester']
        branch = request.form['branch']
        description = request.form['description']

        file = request.files.get('file')

        if file and file.filename:

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config['NOTES_UPLOAD_FOLDER'],
                    filename
                )
            )

            note = Note(
                title=title,
                subject=subject,
                semester=semester,
                branch=branch,
                description=description,
                file_name=filename,
                status='Pending',
                user_id=session['user_id']
            )

            db.session.add(note)
            db.session.commit()

            # Matching student request automatically complete karo
            complete_matching_request(
                request_type="Notes",
                subject=subject,
                semester=semester
            )

    notes = Note.query.filter_by(
        user_id=session['user_id']
    ).all()

    return render_template(
        'teacher/notes.html',
        notes=notes
    )


# =========================================================
# TEACHER ASSIGNMENTS
# =========================================================

@app.route('/teacher/assignments', methods=['GET', 'POST'])
def teacher_assignments():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'teacher':
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        subject = request.form['subject']
        semester = request.form['semester']
        branch = request.form['branch']
        description = request.form['description']
        due_date = request.form['due_date']

        file = request.files.get('file')

        filename = None

        if file and file.filename:

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config['ASSIGNMENT_UPLOAD_FOLDER'],
                    filename
                )
            )

        assignment = Assignments(
            title=title,
            subject=subject,
            semester=semester,
            branch=branch,
            description=description,
            due_date=due_date,
            file_name=filename,
            user_id=session['user_id']
        )

        db.session.add(assignment)
        db.session.commit()

        # Matching student request automatically complete karo
        complete_matching_request(
            request_type="Assignment",
            subject=subject,
            semester=semester
        )

        return redirect('/teacher/assignments')

    assignments = Assignments.query.filter_by(
        user_id=session['user_id']
    ).all()

    return render_template(
        'teacher/assignments.html',
        assignments=assignments
    )
# =========================================================
# TEACHER ATTENDANCE
# =========================================================

@app.route('/teacher/attendance', methods=['GET', 'POST'])
def teacher_attendance():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'teacher':
        return redirect('/dashboard')

    students = User.query.filter_by(
        role='student'
    ).order_by(
        User.name.asc()
    ).all()

    if request.method == 'POST':

        subject = request.form['subject']
        attendance_date = datetime.strptime(
            request.form['date'],
            '%Y-%m-%d'
        ).date()

        semester = request.form.get('semester')
        branch = request.form.get('branch')

        for student in students:

            status = request.form.get(
                f'status_{student.id}'
            )

            if not status:
                continue

            existing_record = Attendance.query.filter_by(
                student_id=student.id,
                subject=subject,
                date=attendance_date
            ).first()

            if existing_record:

                existing_record.status = status
                existing_record.teacher_id = session['user_id']

            else:

                attendance_record = Attendance(
                    student_id=student.id,
                    teacher_id=session['user_id'],
                    subject=subject,
                    date=attendance_date,
                    status=status,
                    remarks=None
                )

                db.session.add(attendance_record)

        db.session.commit()

        return redirect('/teacher/attendance')

    return render_template(
        'teacher/attendance.html',
        students=students,
        today=datetime.today().strftime('%Y-%m-%d')
    )
# =========================================================
# TEACHER NEWS & EVENTS
# =========================================================

@app.route('/teacher/news-events', methods=['GET', 'POST'])
def teacher_news_events():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] not in ['admin', 'teacher']:
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        news_type = request.form['type']
        description = request.form['description']
        event_date = request.form.get('event_date')
        location = request.form.get('location')

        news_event = NewsEvent(
            title=title,
            type=news_type,
            description=description,
            event_date=event_date,
            location=location,
            status='Pending',
            upload_date=None,
            user_id=session['user_id']
        )

        db.session.add(news_event)
        db.session.commit()

        return redirect('/teacher/news-events')

    if session['role'] == 'teacher':
        news_events = NewsEvent.query.filter_by(
            user_id=session['user_id']
        ).all()
    else:
        news_events = NewsEvent.query.all()

    return render_template(
        'teacher/news_events.html',
        news_events=news_events
    )

# =========================================================
# PUBLIC NEWS & EVENTS
# =========================================================

@app.route('/news-events')
def public_news_events():

    news_events = NewsEvent.query.filter_by(
        status='Approved'
    ).order_by(
        NewsEvent.id.desc()
    ).all()

    return render_template(
        'public/news_events.html',
        news_events=news_events
    )

@app.route('/delete-paper/<int:paper_id>')
def delete_paper(paper_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    paper = db.session.get(OldPaper, paper_id)

    if not paper:
        return redirect('/admin/papers')

    file_path = os.path.join(
        app.config['PAPERS_UPLOAD_FOLDER'],
        paper.file_name
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(paper)
    db.session.commit()

    return redirect('/admin/papers')

@app.route('/approve-paper/<int:paper_id>')
def approve_paper(paper_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    paper = db.session.get(OldPaper, paper_id)

    if paper:

        paper.status = "Approved"

        db.session.commit()

    return redirect('/admin/papers')

@app.route('/reject-paper/<int:paper_id>')
def reject_paper(paper_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    paper = db.session.get(OldPaper, paper_id)

    if paper:

        paper.status = "Rejected"

        db.session.commit()

    return redirect('/admin/papers')

@app.route('/delete-user/<int:user_id>')
def delete_user(user_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    user = db.session.get(User, user_id)

    if not user:
        return redirect('/manage-users')

    # Admin apna account delete nahi kar sakta
    if user.id == session['user_id']:
        return "You cannot delete your own admin account."

    db.session.delete(user)
    db.session.commit()

    return redirect('/manage-users')

@app.route('/edit-student/<int:user_id>', methods=['GET', 'POST'])
def edit_student(user_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    student = db.session.get(User, user_id)

    if not student:
        return redirect('/manage-users')

    if request.method == 'POST':

        student.name = request.form['name']
        student.email = request.form['email']
        student.mobile = request.form['mobile']
        student.parent_name = request.form['parent_name']
        student.enrollment_no = request.form['enrollment_no']
        student.college = request.form['college']
        student.course = request.form['course']
        student.branch = request.form['branch']
        student.semester = request.form['semester']
        student.address = request.form['address']

        db.session.commit()

        return redirect('/manage-users')

    return render_template(
        'admin/edit_student.html',
        student=student
    )

@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')
    user = db.session.get(User, session['user_id'])

    return render_template(
        'student/profile.html',
        user=user
    )

@app.route('/lost-found', methods=['GET', 'POST'])
def lost_found():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        contact = request.form['contact']

        item = LostFound(
            title=title,
            description=description,
            contact=contact,
            user_id=session['user_id']
        )

        db.session.add(item)
        db.session.commit()

        return redirect('/lost-found')

    items = LostFound.query.filter_by(
        user_id=session['user_id']
        ).all()

    return render_template(
        'student/lost_found.html',
        items=items
    )
@app.route('/expense', methods=['GET', 'POST'])
def expense():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        amount = float(request.form['amount'])
        description = request.form['description']

        expense = Expense(
            amount=amount,
            description=description,
            user_id=session['user_id']
        )

        db.session.add(expense)
        db.session.commit()

        return redirect('/expense')

    expenses = Expense.query.filter_by(
        user_id=session['user_id']
    ).all()

    total = sum(expense.amount for expense in expenses)

    return render_template(
        'student/expense.html',
        expenses=expenses,
        total=total
    )
@app.route('/notice')
def notice():

    if 'user_id' not in session:
        return redirect('/login')

    notices = Notice.query.all()

    return render_template(
        'student/notice.html',
        notices=notices
    )
@app.route('/notes')
def notes():

    if 'user_id' not in session:
        return redirect('/login')

    notes = Note.query.filter_by(status="Approved").all()

    return render_template(
        'student/notes.html',
        notes=notes
    )


@app.route('/admin/notes', methods=['GET', 'POST'])
def admin_notes():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    if request.method == 'POST':

        title = request.form['title']
        subject = request.form['subject']
        semester = request.form['semester']
        branch = request.form['branch']
        description = request.form['description']

        file = request.files['file']

        if file and file.filename:

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config['NOTES_UPLOAD_FOLDER'],
                    filename
                )
            )

            note = Note(
                title=title,
                subject=subject,
                semester=semester,
                branch=branch,
                description=description,
                file_name=filename,
                status="Approved",
                user_id=session['user_id']
            )

            db.session.add(note)
            db.session.commit()

            # Matching student request automatically complete karo
            complete_matching_request(
                request_type="Notes",
                subject=subject,
                semester=semester
            )
        return redirect('/admin/notes')

    notes = Note.query.all()

    return render_template(
        'admin/notes.html',
        notes=notes
    )


@app.route('/approve-note/<int:note_id>')
def approve_note(note_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    note = db.session.get(Note, note_id)

    if not note:
        return redirect('/admin/notes')

    note.status = "Approved"

    db.session.commit()

    return redirect('/admin/notes')


@app.route('/reject-note/<int:note_id>')
def reject_note(note_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    note = db.session.get(Note, note_id)

    if not note:
        return redirect('/admin/notes')

    note.status = "Rejected"

    db.session.commit()

    return redirect('/admin/notes')


@app.route('/delete-note/<int:note_id>')
def delete_note(note_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    note = db.session.get(Note, note_id)

    if not note:
        return redirect('/admin/notes')

    file_path = os.path.join(
        app.config['NOTES_UPLOAD_FOLDER'],
        note.file_name
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(note)
    db.session.commit()

    return redirect('/admin/notes')


@app.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    note = db.session.get(Note, note_id)

    if not note:
        return redirect('/admin/notes')

    if request.method == 'POST':

        note.title = request.form['title']
        note.subject = request.form['subject']
        note.semester = request.form['semester']
        note.branch = request.form['branch']
        note.description = request.form['description']

        db.session.commit()

        return redirect('/admin/notes')

    notes = Note.query.all()

    return render_template(
        'admin/notes.html',
        notes=notes,
        edit_note=note
    )

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# =========================================================
# STUDENT PAYMENT
# =========================================================

@app.route('/payment', methods=['GET', 'POST'])
def payment():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        payment_for = request.form['payment_for']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']

        payment = Payment(
            user_id=session['user_id'],
            payment_for=payment_for,
            amount=amount,
            payment_method=payment_method,
            status="Pending"
        )

        db.session.add(payment)
        db.session.commit()

        return redirect('/payment-history')

    return render_template(
        'student/payment.html'
    )

# =========================================================
# STUDENT PAYMENT HISTORY
# =========================================================

@app.route('/payment-history')
def payment_history():

    if 'user_id' not in session:
        return redirect('/login')

    payments = Payment.query.filter_by(
        user_id=session['user_id']
    ).order_by(
        Payment.id.desc()
    ).all()

    return render_template(
        'student/payment_history.html',
        payments=payments
    )

# =========================================================
# ADMIN PAYMENT MANAGEMENT
# =========================================================

@app.route('/admin/payments')
def admin_payments():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    payments = Payment.query.order_by(
        Payment.id.desc()
    ).all()

    return render_template(
        'admin/payments.html',
        payments=payments
    )

@app.route('/admin/payment-status/<int:payment_id>', methods=['POST'])
def admin_payment_status(payment_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    payment = db.session.get(Payment, payment_id)

    if not payment:
        return redirect('/admin/payments')

    status = request.form['status']

    if status not in ['Pending', 'Success', 'Failed']:
        return redirect('/admin/payments')

    payment.status = status

    db.session.commit()

    return redirect('/admin/payments')

# =========================================================
# GALLERY MANAGEMENT
# =========================================================

@app.route('/admin/gallery', methods=['GET', 'POST'])
def admin_gallery():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] not in ['admin', 'teacher']:
        return redirect('/dashboard')

    if request.method == 'POST':

        image = request.files.get('image')
        title = request.form.get('title')

        if not image or image.filename == '':
            return redirect('/admin/gallery')

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config['GALLERY_UPLOAD_FOLDER'],
                filename
            )
        )

        gallery = Gallery(
            image_name=filename,
            title=title,
            user_id=session['user_id']
        )

        db.session.add(gallery)
        db.session.commit()

        return redirect('/admin/gallery')

    images = Gallery.query.order_by(
        Gallery.id.desc()
    ).all()

    return render_template(
        'admin/gallery.html',
        images=images
    )


@app.route('/admin/gallery/delete/<int:image_id>', methods=['POST'])
def delete_gallery_image(image_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return redirect('/dashboard')

    image = db.session.get(Gallery, image_id)

    if not image:
        return redirect('/admin/gallery')

    file_path = os.path.join(
        app.config['GALLERY_UPLOAD_FOLDER'],
        image.image_name
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(image)
    db.session.commit()

    return redirect('/admin/gallery')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

