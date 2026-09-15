from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    college = db.Column(
        db.String(150),
        nullable=True
    )

    course = db.Column(
        db.String(100),
        nullable=True
    )

    branch = db.Column(
        db.String(100),
        nullable=True
    )

    semester = db.Column(
        db.String(20),
        nullable=True
    )

    enrollment_no = db.Column(
        db.String(50),
        nullable=True
    )

    profile_photo = db.Column(
        db.String(255),
        nullable=True
    )

    mobile = db.Column(
        db.String(15),
        nullable=True
    )

    parent_name = db.Column(
        db.String(100),
        nullable=True
    )

    address = db.Column(
        db.Text,
        nullable=True
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default='student'
    )

    expenses = db.relationship(
        'Expense',
        backref='user',
        lazy=True
    )

    lost_items = db.relationship(
        'LostFound',
        backref='user',
        lazy=True
    )

    notes = db.relationship(
        'Note',
        backref='user',
        lazy=True
    )

    notices = db.relationship(
        'Notice',
        backref='user',
        lazy=True
    )

    def __repr__(self):
        return f'<User {self.name}>'


class LostFound(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    contact = db.Column(
        db.String(100),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )


class Expense(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    description = db.Column(
        db.String(200),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )


class Notice(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    upload_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

class Note(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    semester = db.Column(
        db.String(20),
        nullable=False
    )

    branch = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    upload_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Approved"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )


class OldPaper(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    university = db.Column(
        db.String(100),
        nullable=False
    )

    course = db.Column(
        db.String(100),
        nullable=False
    )

    branch = db.Column(
        db.String(100),
        nullable=False
    )

    semester = db.Column(
        db.String(20),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    exam_year = db.Column(
        db.String(10),
        nullable=False
    )

    exam_type = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    reward_token = db.Column(
        db.Integer,
        default=0
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )


class Assignments(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    semester = db.Column(
        db.String(20),
        nullable=False
    )

    branch = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    due_date = db.Column(
        db.String(50),
        nullable=False
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    upload_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    user = db.relationship(
        'User',
        backref='assignments',
        lazy=True
    )

class TeacherCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(50), unique=True, nullable=False)

    is_used = db.Column(db.Boolean, default=False, nullable=False)

    used_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class NewsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    upload_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class StudentRequest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    institution = db.Column(
        db.String(150),
        nullable=False
    )

    course = db.Column(
        db.String(100),
        nullable=False
    )

    semester = db.Column(
        db.String(20),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    request_type = db.Column(
        db.String(50),
        nullable=False
    )

    requirement = db.Column(
        db.Text,
        nullable=False
    )

    request_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default='Pending'
    )


class Payment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    payment_for = db.Column(
        db.String(100),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    transaction_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    payment_method = db.Column(
        db.String(50),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=False
    )

    payment_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    user = db.relationship(
        'User',
        backref='payments',
        lazy=True
    )
class Attendance(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Present"
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    student = db.relationship(
        'User',
        foreign_keys=[student_id],
        backref='attendance_records'
    )

    teacher = db.relationship(
        'User',
        foreign_keys=[teacher_id],
        backref='marked_attendance'
    )
class Gallery(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    image_name = db.Column(
        db.String(255),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=True
    )

    upload_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    user = db.relationship(
        'User',
        backref='gallery_images',
        lazy=True
    )