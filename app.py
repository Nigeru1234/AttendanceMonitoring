import os
from datetime import datetime
from flask import Flask, render_template, request, session, jsonify, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# List of students to track
STUDENTS = ["Francine Alboroto", "Calvin Canoy", "Bd Gaspar"]

@app.before_request
def before_request():
    # Initialize session data if not exists
    if 'attendance' not in session:
        session['attendance'] = {}
    if 'current_date' not in session:
        session['current_date'] = datetime.now().strftime('%Y-%m-%d')

@app.route('/')
def index():
    current_date = session.get('current_date', datetime.now().strftime('%Y-%m-%d'))
    attendance = session.get('attendance', {}).get(current_date, [])

    # Calculate absent students
    absent_students = [student for student in STUDENTS if student not in attendance]

    return render_template('index.html', 
                         students=STUDENTS,
                         current_date=current_date,
                         attendance=attendance,
                         absent_students=absent_students,
                         perfect_attendance=len(absent_students) == 0)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_name = request.form.get('student_name')
    current_date = session.get('current_date')

    if not student_name or student_name not in STUDENTS:
        flash('Invalid student name!', 'danger')
        return redirect(url_for('index'))

    # Initialize date in attendance if not exists
    if current_date not in session['attendance']:
        session['attendance'][current_date] = []

    # Check if student already marked
    if student_name in session['attendance'][current_date]:
        flash('Student already marked present!', 'warning')
    else:
        session['attendance'][current_date].append(student_name)
        session.modified = True
        flash('Attendance marked successfully!', 'success')

    return redirect(url_for('index'))

@app.route('/set_date', methods=['POST'])
def set_date():
    new_date = request.form.get('date')
    try:
        # Validate date format
        datetime.strptime(new_date, '%Y-%m-%d')
        session['current_date'] = new_date
        flash('Date updated successfully!', 'success')
    except ValueError:
        flash('Invalid date format!', 'danger')

    return redirect(url_for('index'))

@app.route('/reset_attendance', methods=['POST'])
def reset_attendance():
    current_date = session.get('current_date')
    if current_date in session['attendance']:
        session['attendance'][current_date] = []
        session.modified = True
        flash('Attendance reset for the current date!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
