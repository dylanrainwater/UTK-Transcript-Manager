from collections import OrderedDict
import os

from models import Profile
from models import Course
from models import db

from peewee import *

def initialize():
    """Create database and tables"""
    db.connect()
    db.create_tables([Profile, Course], safe=True)

def clear():
    """Clear screen"""
    cmd = 'cls' if os.name == 'nt' else 'clear'
    os.system(cmd)

def show_menu():
    """"Display main menu and options"""
    choice = None

    while choice != 'q':
        clear()
        print('='*20)
        print('UTK GPA Calculator')
        print('='*20)
        for key, value in main_menu.items():
            print("{} - {}".format(key, value.__doc__))
        print('q - Quit')

        choice = input('> ').lower().strip()
        if choice in main_menu:
            clear()
            main_menu[choice]()
    clear()

def get_or_create_profile(msg):
    """Prompt `msg`, then create the profile if it doesn't exist and return it
    """
    profile_name = input(msg).lower().strip()
    profile, created = Profile.get_or_create(name=profile_name)

    if created:
        print("Profile was created for {}.".format(profile.name))

    calculate_gpa(profile)

    clear()
    return profile

def get_courses_for(profile):
    """Retrun list of courses that belong to a profile"""
    return Course.select().where(Course.profile == profile)

def list_courses_for(profile):
    """Print a list of all courses that belong to a profile"""
    print("Showing: {}'s profile".format(profile.name))
    print("GPA: {0:.2f}".format(profile.GPA))
    print("All courses and grades:")
    courses = get_courses_for(profile)
    print('='*75)
    courses = get_courses_for(profile)
    if courses:
        for i, course in enumerate(courses):
            # 1. [A]    EXAMPLE 101    3 hours
            print("{}. {:10}{:10}{:10} hours".format(i + 1,
                                                course.grade,
                                                 course.name,
                                                 course.hours))
    else:
        print("No courses to show at this time.")
    print('='*75)

def show_profile(profile=None):
    """Show the GPA and courses / grades for a specific profile"""
    if not profile:
        profile = get_or_create_profile("Profile to show: ")

    calculate_gpa(profile)
    list_courses_for(profile)
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
    """Edit profile to create, change, or delete courses"""
    if not profile:
        profile = get_or_create_profile("Profile to edit: ")

    first = True
    while True:
        list_courses_for(profile)
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
    """Delete a course from a user's profile"""
    courses = get_courses_for(profile)
    while courses:
        list_courses_for(profile)
        m = "Enter 'q' to quit or enter the number before the course to delete:"
        to_delete = input(m)
        if to_delete == 'q':
            return
        to_delete = int(to_delete)
        courses[to_delete - 1].delete_instance()

        next_action = input("Delete a course? [y/n]: ").lower().strip()

        courses = get_courses_for(profile)
        if next_action == 'n' and courses:
            return

def calculate_gpa(profile):
    """Calculate GPA using UTK's scale:
        Add all attempted hours together
        Add all quality points
            A = 4
            A- = 3.7
            B+ = 3.3
            B = 3
            B- = 2.7
            ...
        GPA = quality points / attempted hours
    """
    courses = get_courses_for(profile)
    if len(courses) == 0:
        profile.GPA = 0.0
        profile.save()
        return
    total_hours = 0
    total_quality_points = 0
    if courses:
        for course in courses:
            total_hours += course.hours
            quality_points = points[course.grade[0]]
            if len(course.grade) == 2:
                if course.grade[1] == '+':
                    quality_points += 0.3
                else:
                    quality_points -= 0.3

            total_quality_points += quality_points * course.hours
    total_gpa = total_quality_points / total_hours
    profile.GPA = total_gpa
    profile.save()

def list_profiles():
    """List all profiles saved"""
    for profile in Profile.select().order_by(Profile.GPA.desc()):
        print("Name:\t{}\tGPA:\t{}".format(profile.name, profile.GPA))
    input("Press Enter to return to menu.")

main_menu = OrderedDict([
    ('s', show_profile),
    ('r', edit_profile),
    ('p', list_profiles),
])

letter_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C',
                 'C-', 'D+', 'D', 'D-', 'F']

points = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}

if __name__ == '__main__':
    initialize()
    show_menu()
