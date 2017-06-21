from collections import OrderedDict
import os

from peewee import *

db = SqliteDatabase('calculator.db')

class Profile(Model):
    name = CharField(max_length=255, unique=True)
    GPA = DecimalField(default=0.0)

    class Meta:
        database = db

class Course(Model):
    name = CharField(max_length=255)
    grade = CharField(max_length=2)
    hours = IntegerField()
    profile = ForeignKeyField(Profile)

    class Meta:
        database = db

def initialize():
    """Create database and tables"""
    db.connect()
    db.create_tables([Profile, Course], safe=True)

def clear():
    """Clear screen"""
    cmd = 'cls' if os.name == 'nt' else 'clear'
    os.system(cmd)

def show_menu():
    choice = None

    while choice != 'q':
        clear()
        print('='*20)
        print('UTK GPA Calculator')
        print('='*20)
        for key, value in menu.items():
            print("{} - {}".format(key, value.__doc__))
        print('q - Quit')
        choice = input('> ').lower().strip()

        if choice in menu:
            clear()
            menu[choice]()

def show_profile(profile=None):
    """Show the GPA and courses / grades for a specific profile"""
    if not profile:
        profile_name = input("Profile to show: ").lower().strip()
        try:
            profile = Profile.get(Profile.name == profile_name)
        except Profile.DoesNotExist:
            next = input("Profile for '{}' does not exist. Create? [y/n]".format(profile_name))
            if next == 'n':
                return
            else:
                profile = Profile.create(name=profile_name, GPA=0.0)
    calculate_gpa(profile)
    print("GPA: {}".format(profile.GPA))
    print("All courses and grades:")
    print('='*75)
    courses = Course.select().where(Course.profile == profile)
    if courses:
        for course in courses:
            print("{:10}{:10}{:10} hours".format(course.grade, course.name, course.hours))
    else:
        print("No courses to show at this time.")
    print('='*75)
    print('\n\n')
    print('s - Show another profile')
    print('e - Edit profile')
    print('q - Quit to menu')
    next_action = input("> ").lower().strip()

    if next_action == 's':
        clear()
        show_profile()
    if next_action == 'e':
        clear()
        edit_profile(profile)


def edit_profile(profile=None):
    """Remove, edit, or add new courses / grades to a profile"""
    if not profile:
        profile_name = input("Profile to edit: ").lower().strip()
        profile, created = Profile.get_or_create(name=profile_name)
        if created:
            print("Profile for {} was created".format(profile.name))

    first = True
    while True:
        if not first:
            print('Course added.')
        print("GPA: {}".format(profile.GPA))
        print('n - Add new course')
        print('s - Show summary')
        print('d - Delete course')
        print('q - Quit to menu')
        next_action = input("> ").lower().strip()
        if next_action == 's':
            clear()
            show_profile(profile)
            return
        if next_action == 'd':
            clear()
            delete_course(profile)
            return
        if next_action == 'q':
            return
        title = input('Title of course: ').strip()
        hours = int(input('How many credit hours? '))
        print('Possible letter grades for UTK: ')
        print(', '.join(letter_grades).upper())
        grade = input('Letter grade for course: ').upper().strip()
        if grade in letter_grades:
            Course.create(name=title, grade=grade, hours=hours, profile=profile)
            first = False
            calculate_gpa(profile)
        clear()

def delete_course(profile):
    while True:
        courses = Course.select().where(Course.profile == profile)
        for i, course in enumerate(courses):
            print("({})\t{}".format(i + 1, course.name))

        to_delete = int(input("Enter the number before the course to delete: "))
        courses[to_delete - 1].delete_instance()

        next_action = input("Delete another? [y/n]: ").lower().strip()
        if next_action == 'n':
            return

def calculate_gpa(profile):
    courses = Course.select().where(Course.profile == profile)
    if len(courses) == 0:
        profile.GPA = 0.0
        profile.save()
        return
    total_hours = 0
    total_quality_points = 0
    if courses:
        for course in courses:
            total_hours += course.hours
            quality_points = 0
            if course.grade == 'A':
                quality_points = 4
            if course.grade == 'A-':
                quality_points = 3.7
            if course.grade == 'B+':
                quality_points = 3.3
            if course.grade == 'B':
                quality_points = 3
            if course.grade == 'B-':
                quality_points = 2.7
            if course.grade == 'C+':
                quality_points = 2.3
            if course.grade == 'C':
                quality_points = 2
            if course.grade == 'C-':
                quality_points = 1.7
            if course.grade == 'D+':
                quality_points = 1.3
            if course.grade == 'D':
                quality_points = 1
            if course.grade == 'D-':
                quality_points = 0.7
            if course.grade == 'F':
                quality_points = 0
            total_quality_points += quality_points * course.hours
    total_gpa = total_quality_points / total_hours
    profile.GPA = total_gpa
    profile.save()

def list_profiles():
    """List all profiles saved"""
    for profile in Profile.select().order_by(Profile.GPA.desc()):
        print("Name:\t{}\tGPA:\t{}".format(profile.name, profile.GPA))
    input("Press Enter to return to menu.")
    
menu = OrderedDict([
    ('s', show_profile),
    ('r', edit_profile),
    ('p', list_profiles),
])

letter_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C',
                 'C-', 'D+', 'D', 'D-', 'F']

#  Read existing GPA, classes/grades for profile
#  Read new classes/grades
#  Calculate GPA
#  Save new GPA, classes/grades to profile
if __name__ == '__main__':
    initialize()
    show_menu()
