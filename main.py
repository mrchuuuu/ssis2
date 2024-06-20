import tkinter as tk
from ttkbootstrap import ttk 
from ttkbootstrap.constants import *
import sqlite3

connection = sqlite3.connect('./data/data.db')
cursor = connection.cursor()

def add_tables():
    cursor.execute("CREATE TABLE IF NOT EXISTS students (id TEXT NOT NULL, name TEXT, gender TEXT, year TEXT NOT NULL, course TEXT NOT NULL)")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS courses (code TEXT NOT NULL, name TEXT NOT NULL)")
    connection.commit()
    
add_tables()
        
def populate_course_table(rows):
    if not len(rows):
        return
    course_table.delete(*course_table.get_children())
    for idx, row in enumerate(rows):
        course_table.insert('', values = (row[0], row[1]), index = idx)

def get_all_courses():
    
    cursor.execute("SELECT * FROM courses")
    result = cursor.fetchall()
    if result is None:
        return []
    else:
        rows = []
        for res in result:
            rows.append(list(res))
        return rows
        

def get_courses_by_text(search):
    rows = get_all_courses()
    final_rows = []
    for row in rows:
        
        if search.lower() in " ".join(row).lower():
            final_rows.append(row)
        else:
            continue
    return final_rows

window = tk.Tk()
window.title("Simple Student Information System SQL")

course_buttons = ttk.Frame(window)

def message_box(text):
    message_window = tk.Toplevel(window)
    text_label = ttk.Label(message_window, text = text, bootstyle = INFO)
    text_label.pack(side = TOP)
    ok_button = ttk.Button(message_window, text="OK", width=30, bootstyle=(SUCCESS, OUTLINE), command=message_window.destroy)
    ok_button.pack(side=TOP, padx=20, pady=20, fill=X, expand=True)

def new_course_window():
    
    def add_command():
        if not len(course_id_entry.get()) or not len(course_name_entry.get()):
            message_box("There are some missing fields milord.")
            return
        cursor.execute("SELECT * FROM courses WHERE code = ?", (course_id_entry.get(),))
        result = cursor.fetchone()
        if result is not None:
            message_box("Course already exists!")
            return
        
        cursor.execute("INSERT INTO courses (code, name) VALUES (?, ?)", (course_id_entry.get().upper(), course_name_entry.get()))
        connection.commit()
        
        course_window.destroy()
        populate_course_table(get_all_courses())
        populate_student_table(get_all_students())
        message_box("Successfully added a course!")
    
    course_window = tk.Toplevel(window)
    course_window.title("Add a Course")
    
    course_id_label = ttk.Label(course_window, text = "Course ID")
    course_id_label.pack(side = TOP)
    
    course_id_entry = ttk.Entry(course_window, bootstyle = PRIMARY)
    course_id_entry.pack(side = TOP, fill = X, expand = True, pady = 10, padx = 10)
    
    course_name_label = ttk.Label(course_window, text = "Course Name")
    course_name_label.pack(side = TOP)
    
    course_name_entry = ttk.Entry(course_window, bootstyle = PRIMARY)
    course_name_entry.pack(side = TOP, fill = X, expand = True, pady = 10, padx = 10)
    
    add_course = ttk.Button(course_window,
                            bootstyle = (SUCCESS, OUTLINE),
                            text = "Add Course",
                            width = 20,
                            command = add_command)
    add_course.pack(side = LEFT, padx = 10, pady = 10)
    
    cancel = ttk.Button(course_window,
                        bootstyle = (DANGER, OUTLINE),
                        text = "Cancel",
                        width = 20,
                        command = course_window.destroy)
    cancel.pack(side = LEFT, padx = 10, pady = 10)
    
new_course = ttk.Button(course_buttons,
                        width = 20,
                        bootstyle = (PRIMARY, OUTLINE),
                        text = "New Course",
                        command = new_course_window)
new_course.pack(side = LEFT, padx = 10)

def edit_course_command():
    
    def save_course():
        course_id = course_id_entry.get()
        final_course_name = course_name_entry.get()
        cursor.execute("UPDATE courses SET name = ? WHERE code = ?", (final_course_name, course_id))
        connection.commit()
        populate_course_table(get_all_courses())
        message_box("Course Successfully updated!")
        course_window.destroy()
    
    selected_item = course_table.selection()
    if len(selected_item) == 0:
        message_box("You have not selected an item milord.")
        return
    else: 
        course_code, course_name = course_table.item(selected_item, 'values')
        course_window = tk.Toplevel(window)
        course_window.title("Edit Course")
        
        course_id_label = ttk.Label(course_window, text = "Course ID")
        course_id_label.pack(side = TOP)
        
        course_id_entry = ttk.Entry(course_window, bootstyle = PRIMARY)
        course_id_entry.pack(side = TOP, fill = X, expand = True, pady = 10, padx = 10)
        
        course_name_label = ttk.Label(course_window, text = "Course Name")
        course_name_label.pack(side = TOP)
        
        course_name_entry = ttk.Entry(course_window, bootstyle = PRIMARY)
        course_name_entry.pack(side = TOP, fill = X, expand = True, pady = 10, padx = 10)
        
        add_course = ttk.Button(course_window, bootstyle = (SUCCESS, OUTLINE), text = "Save Course", width = 20, command = save_course)
        add_course.pack(side = LEFT, padx = 10, pady = 10)
        
        cancel = ttk.Button(course_window, bootstyle = (DANGER, OUTLINE), text = "Cancel", width = 20, command = course_window.destroy)
        cancel.pack(side = LEFT, padx = 10, pady = 10)
        
        course_id_entry.insert(0, course_code)
        course_name_entry.insert(0, course_name)
        course_id_entry.config(state = DISABLED)

edit_course = ttk.Button(course_buttons,
                         width = 20,
                         bootstyle = (INFO, OUTLINE),
                         text = "Edit Course",
                         command = edit_course_command)
edit_course.pack(side = LEFT, padx = 10)


def course_delete_button():
    
    def delete_command():
        cursor.execute("DELETE FROM courses WHERE code = ?", (course_code,))
        populate_course_table(get_all_courses())
        populate_student_table(get_all_students())
        course_window.destroy()
    
    selected_item = course_table.selection()
    if len(selected_item) == 0:
        message_box("You have not selected an item milord.")
        return
    course_code, course_name = course_table.item(selected_item, 'values')
    
    course_window = tk.Toplevel(window)
    course_window.title("Delete Course")
    
    delete_label = ttk.Label(course_window,
                             text = f"Are you sure you want to delete {course_code}?",
                             bootstyle = DANGER)
    delete_label.pack(side = TOP)
    
    delete_course = ttk.Button(course_window,
                               bootstyle = (SUCCESS, OUTLINE),
                               text = "Yes",
                               width = 20,
                               command = delete_command)
    delete_course.pack(side = LEFT, padx = 10, pady = 10)
    
    cancel = ttk.Button(course_window,
                        bootstyle = (DANGER, OUTLINE),
                        text = "Cancel", width = 20,
                        command = course_window.destroy)
    cancel.pack(side = LEFT,
                padx = 10,
                pady = 10)
    
delete_course = ttk.Button(course_buttons,
                           width = 20,
                           bootstyle = (DANGER, OUTLINE),
                           text = "Delete Course",
                           command = course_delete_button)
delete_course.pack(side = LEFT, padx = 10)

course_buttons.pack(side = TOP, fill = X, padx = 20, pady = 20)

def on_course_search_enter(event):
    value = course_search.get()
    rows = get_courses_by_text(value)
    populate_course_table(rows)

course_search_frame = ttk.Frame(window)

course_search_label = ttk.Label(course_search_frame, text = "SEARCH")
course_search_label.pack(side = LEFT, padx = 10, pady = 5)
course_search = ttk.Entry(course_search_frame, bootstyle = INFO)
course_search.bind("<Return>", on_course_search_enter)
course_search.pack(side = RIGHT, fill = X, expand = True, padx = 30)
course_search_frame.pack(side = TOP, fill = X, expand = True)

course_table = ttk.Treeview(columns = ("code", "name"), show = 'headings', selectmode = BROWSE, bootstyle = INFO)
course_table.heading("code", text = "Course code")
course_table.heading("name", text = "Course name")
course_table.pack(side = TOP, pady = 20, fill = X, expand = True)

if len(get_all_courses()) > 0:
    populate_course_table(get_all_courses())
    
ttk.Separator(window, bootstyle = DANGER).pack(side = TOP, padx = 20, pady = 5, fill = X, expand = True)

def populate_student_table(rows):   
    
    student_table.delete(*student_table.get_children())
    if not len(rows):
        return 
    cursor.execute("SELECT code FROM courses")
    courses = cursor.fetchall()
    courses = [course[0] for course in courses] # flatten the list
    for index, student in enumerate(rows):
        if not student[4] in courses:
            rows[index][4] = "N/A"
            rows[index].append("NOT ENROLLED")
        else:
            rows[index].append("ENROLLED")
    for idx, row in enumerate(rows):
        student_table.insert('', values = (row[0], row[1], row[2].upper(), row[3], row[4], row[5]), index = idx)
        
def get_all_students():
    cursor.execute("SELECT * FROM students")
    results = cursor.fetchall()
    if not len(results):
        return []
    listed_results = []
    for result in results:
        listed_results.append(list(result))
    return listed_results
    
        
def get_students_by_text(search):
    rows = get_all_students()
    final_rows = []
    for row in rows:
        if search.lower() in " ".join(row).lower():
            final_rows.append(row)
        else:
            continue
    return final_rows

def new_student():
    
    def add_student_command():
        id = id_entry.get()
        name = name_entry.get()
        gender = gender_entry.get()
        year_level = yearlevel_menu.get()
        course = course_entry.get()
        
        cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
        students = cursor.fetchall()
        if len(students):
            return message_box("Student already exists!")
        if not len(id):
            return message_box("You did not provide any ID")
        if not len(id) == 9:
            return message_box("The ID you provided must be XXXX-XXXX format")
        if not id.replace("-", "").isdigit():
            return message_box("The X in XXXX-XXXX must be an integer.")
        if not len(name):
            return message_box("Name is not provided.")
        if not len(gender) or gender.lower() in ["none", "prefer not to say"]:
            gender = "N/A"
        if not len(year_level):
            year_level = "N/A"
        if not len(course):
            course = "N/A"
        cursor.execute("INSERT INTO students (id, name, gender, year, course) VALUES (?, ?, ?, ?, ?)",
                       (id.upper(), name, gender.upper(), year_level, course.upper()))
        connection.commit()
        student_window.destroy()
        message_box("Successfully added a student!")
        populate_student_table(get_all_students())     
    
    student_window = tk.Toplevel(window)
    student_window.title("Add a Student")
    
    id_frame = ttk.Frame(student_window)
    id_label = ttk.Label(id_frame, text = "ID NUMBER: ")
    id_label.pack(side=LEFT)
    
    id_entry = ttk.Entry(id_frame, bootstyle = INFO, width = 30)
    id_entry.pack(side=RIGHT)
    id_frame.pack(side=TOP, fill = X, expand = True, padx = 20, pady = 5)
    
    name_frame = ttk.Frame(student_window)
    name_label = ttk.Label(name_frame, text="NAME: ")
    name_label.pack(side = LEFT)
    
    name_entry = ttk.Entry(name_frame, bootstyle = INFO, width = 30)
    name_entry.pack(side = RIGHT)
    name_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
    
    gender_frame = ttk.Frame(student_window)
    gender_label = ttk.Label(gender_frame, text = "GENDER: ")
    gender_label.pack(side = LEFT)
    
    gender_entry = ttk.Entry(gender_frame, bootstyle = INFO, width = 30)
    gender_entry.pack(side = RIGHT)
    gender_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
    
    yearlevel_frame = ttk.Frame(student_window)
    yearlevel_label = ttk.Label(yearlevel_frame, text = "YEAR LEVEL: ")
    yearlevel_label.pack(side = LEFT)
    
    yearlevel_menu = ttk.Combobox(yearlevel_frame,
                                  values = ("1st Year", "2nd Year", "3rd Year", "4th Year"),
                                  bootstyle = (INFO),
                                  width = 28,
                                  text = "Year Level",
                                  state = 'readonly')
    yearlevel_menu.pack(side = RIGHT)
    yearlevel_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
    
    
    course_frame = ttk.Frame(student_window)
    course_label = ttk.Label(course_frame, text = "COURSE: ")
    course_label.pack(side = LEFT)
    
    course_entry = ttk.Entry(course_frame, bootstyle = INFO, width = 30)
    course_entry.pack(side = RIGHT)
    course_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
    
    add_button = ttk.Button(student_window, text = "ADD STUDENT", width = 20, command = add_student_command)
    add_button.pack(side = LEFT, padx = 5, pady = 5)
    
    cancel_button = ttk.Button(student_window, text = "CANCEL", width = 20, command = student_window.destroy)
    cancel_button.pack(side=RIGHT, padx = 5, pady = 5)


student_buttons = ttk.Frame(window)
new_student_button = ttk.Button(student_buttons,
                                text = "New Student",
                                width = 20,
                                bootstyle = (SUCCESS, OUTLINE),
                                command = new_student)
new_student_button.pack(side = LEFT, padx = 10, pady = 10)

def on_edit_student():
    def edit_student_command():
        id, name, gender, year, course = id_entry.get(), name_entry.get(), gender_entry.get(), yearlevel_menu.get(), course_entry.get()
        
        if not len(gender) or gender.lower() in ["none", "prefer not to say"]:
            gender = "N/A"
        if not len(year):
            year = "N/A"
        if not len(course.strip()):
            course = "N/A"
        cursor.execute("UPDATE students SET name = ?, gender = ?, year = ?, course = ? WHERE id = ?", (name, gender, year, course, id))
        connection.commit()
        populate_student_table(get_all_students())
        
        student_window.destroy()
        
    selected_item = student_table.selection()
    if len(selected_item) == 0:
        message_box("You have not selected an item milord.")
        return
    else: 
        student_window = tk.Toplevel(window)
        student_window.title("Edit a Student")
        
        id_frame = ttk.Frame(student_window)
        id_label = ttk.Label(id_frame, text="ID NUMBER: ")
        id_label.pack(side = LEFT)
        
        id_entry = ttk.Entry(id_frame, bootstyle = INFO, width = 30)
        id_entry.pack(side = RIGHT)
        id_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
        
        name_frame = ttk.Frame(student_window)
        name_label = ttk.Label(name_frame, text = "NAME: ")
        name_label.pack(side = LEFT)
        
        name_entry = ttk.Entry(name_frame, bootstyle = INFO, width = 30)
        name_entry.pack(side = RIGHT)
        name_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
        
        gender_frame = ttk.Frame(student_window)
        gender_label = ttk.Label(gender_frame, text = "GENDER: ")
        gender_label.pack(side = LEFT)
        
        gender_entry = ttk.Entry(gender_frame, bootstyle = INFO, width = 30)
        gender_entry.pack(side = RIGHT)
        gender_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
        
        yearlevel_frame = ttk.Frame(student_window)
        yearlevel_label = ttk.Label(yearlevel_frame, text = "YEAR LEVEL: ")
        yearlevel_label.pack(side = LEFT)
        
        yearlevel_menu = ttk.Combobox(yearlevel_frame,
                                      values = ("1st Year", "2nd Year", "3rd Year", "4th Year"),
                                      bootstyle = (INFO),
                                      width=28,
                                      text = "Year Level",
                                      state = 'readonly')
        yearlevel_menu.pack(side = RIGHT)
        yearlevel_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
        
        
        course_frame = ttk.Frame(student_window)
        course_label = ttk.Label(course_frame, text = "COURSE: ")
        course_label.pack(side = LEFT)
        
        course_entry = ttk.Entry(course_frame, bootstyle = INFO, width = 30)
        course_entry.pack(side = RIGHT)
        course_frame.pack(side = TOP, fill = X, expand = True, padx = 20, pady = 5)
        
        save_button = ttk.Button(student_window, text = "SAVE", width = 20, command = edit_student_command)
        save_button.pack(side = LEFT, padx = 5, pady = 5)
        
        cancel_button = ttk.Button(student_window, text = "CANCEL", width = 20, command = student_window.destroy)
        cancel_button.pack(side = RIGHT, padx = 5, pady = 5)
        
        id, name, gender, year, course, status = student_table.item(selected_item, 'values')
        id_entry.insert(0, id)
        id_entry.configure(state = DISABLED)
        name_entry.insert(0, name)
        gender_entry.insert(0, gender)
        yearlevel_menu.set(year.capitalize())
        course_entry.insert(0, course)
        
edit_student_button = ttk.Button(student_buttons, text="Edit Student", width=20, bootstyle=(WARNING, OUTLINE), command=on_edit_student)
edit_student_button.pack(side = LEFT, padx = 10, pady = 10)


def student_delete_button():
    
    def delete_command():
        cursor.execute("DELETE FROM students WHERE id = ?", (id,))
        connection.commit()
        populate_student_table(get_all_students())
        student_window.destroy()
    
    selected_item = student_table.selection()
    if len(selected_item) == 0:
        message_box("You have not selected an item milord.")
        return
    id, name, gender, year, course, status = student_table.item(selected_item, 'values')
    
    student_window = tk.Toplevel(window)
    student_window.title("Edit Course")
    
    delete_label = ttk.Label(student_window,
                             text = f"Are you sure you want to delete '{id}'?",
                             bootstyle = DANGER)
    delete_label.pack(side = TOP)
    
    delete_course = ttk.Button(student_window,
                               bootstyle = (SUCCESS, OUTLINE),
                               text = "Yes",
                               width = 20,
                               command = delete_command)
    delete_course.pack(side = LEFT, padx = 10, pady = 10)
    
    cancel = ttk.Button(student_window,
                        bootstyle = (DANGER, OUTLINE),
                        text = "Cancel",
                        width = 20,
                        command = student_window.destroy)
    cancel.pack(side=LEFT, padx=10, pady=10)
    
delete_student_button = ttk.Button(student_buttons,
                                   text = "Delete Student",
                                   width = 20,
                                   bootstyle = (DANGER, OUTLINE),
                                   command = student_delete_button)
delete_student_button.pack(side = LEFT, padx = 10, pady = 10)

student_search_frame = ttk.Frame(window)
student_buttons.pack(side = TOP, pady = 10)

student_search_label = ttk.Label(student_search_frame, text = "SEARCH")
student_search_label.pack(side = LEFT, padx = 10, pady = 10)

def on_student_search_enter(event):
    value = student_search.get()
    rows = get_students_by_text(value)
    populate_student_table(rows)

student_search = ttk.Entry(student_search_frame, bootstyle = INFO)
student_search.pack(side = RIGHT, fill = X, expand = True, pady = 10, padx = 30)

student_search.bind("<Return>", on_student_search_enter)
student_search_frame.pack(side = TOP, fill = X, expand = True)

student_table = ttk.Treeview(columns = ("id", "name", "gender", "year_level", "course", "status"),
                             show = 'headings',
                             selectmode = BROWSE,
                             bootstyle = SUCCESS)
student_table.pack(side = TOP, fill = X, expand = True)

student_table.heading("id", text = "Student ID")
student_table.heading("name", text = "Name")
student_table.heading("gender", text = "Gender")
student_table.heading("year_level", text = "Year Level")
student_table.heading("course", text = "Course")
student_table.heading("status", text = "Status")
student_table.column("id", width = 100)
student_table.column("name", width = 250)
student_table.column("gender", width = 100)
student_table.column("year_level", width = 100)
student_table.column("status", width = 100)


if len(get_all_students()) > 0:
    populate_student_table(get_all_students())

window.mainloop()