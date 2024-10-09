from pymongo import MongoClient, InsertOne, ASCENDING
import random
import pprint

# Connect to MongoDB
client = MongoClient('mongodb://admin:password@localhost:27017/')
db = client['university']

# Collections
students = db['students']
professors = db['professors']
courses = db['courses']
grades = db['grades']

# Create indexes
students.create_index([("student_id", ASCENDING)], unique=True)
professors.create_index([("professor_id", ASCENDING)], unique=True)
courses.create_index([("course_code", ASCENDING)], unique=True)
grades.create_index([("student_id", ASCENDING), ("course_code", ASCENDING)], unique=True)

def generate_sample_data(num_students=1000, num_professors=50, num_courses=100):
    # Generate students
    """
    Generate sample data for the university database.

    Generate a specified number of students, professors, courses, and grades.

    Parameters:
    num_students (int): The number of students to generate. Defaults to 1000.
    num_professors (int): The number of professors to generate. Defaults to 50.
    num_courses (int): The number of courses to generate. Defaults to 100.

    Returns:
    None
    """
    student_ids = []
    for i in range(num_students):
        student = {
            "student_id": f"S{i:04d}",
            "name": f"Student {i}",
            "major": random.choice(["Computer Science", "Mathematics", "Physics", "Biology", "Chemistry"]),
            "year": random.randint(1, 4),
            "gpa": round(random.uniform(2.0, 4.0), 2),
            "enrolled_courses": []
        }
        result = students.insert_one(student)
        student_ids.append(result.inserted_id)

    # Generate professors
    professor_ids = []
    for i in range(num_professors):
        professor = {
            "professor_id": f"P{i:03d}",
            "name": f"Professor {i}",
            "department": random.choice(["Computer Science", "Mathematics", "Physics", "Biology", "Chemistry"]),
            "courses_taught": []
        }
        result = professors.insert_one(professor)
        professor_ids.append(result.inserted_id)

    # Generate courses
    course_codes = []
    for i in range(num_courses):
        course = {
            "course_code": f"C{i:03d}",
            "title": f"Course {i}",
            "department": random.choice(["Computer Science", "Mathematics", "Physics", "Biology", "Chemistry"]),
            "credits": random.choice([3, 4]),
            "professor": random.choice(professor_ids),
            "students": random.sample(student_ids, random.randint(5, 50))
        }
        result = courses.insert_one(course)
        course_codes.append(course['course_code'])

        # Update professor's courses_taught
        professors.update_one({"_id": course['professor']}, {"$push": {"courses_taught": course['course_code']}})

        # Update students' enrolled_courses
        students.update_many({"_id": {"$in": course['students']}}, {"$push": {"enrolled_courses": course['course_code']}})

    # Generate grades
    grade_ops = []
    for course in courses.find():
        for student_id in course['students']:
            grade = {
                "student_id": students.find_one({"_id": student_id})['student_id'],
                "course_code": course['course_code'],
                "grade": random.choice(['A', 'B', 'C', 'D', 'F']),
                "semester": random.choice(["Fall 2023", "Spring 2024"])
            }
            grade_ops.append(InsertOne(grade))

    if grade_ops:
        grades.bulk_write(grade_ops)

    print(f"Generated {num_students} students, {num_professors} professors, {num_courses} courses, and {len(grade_ops)} grades.")

def get_student_transcript(student_id):
    """
    Get a student's transcript.

    Given a student ID, this function will return a dictionary containing the student's
    name, major, year, a list of courses with their grades, the total number of credits,
    and the GPA.

    The courses list will contain dictionaries with the following keys:
    - course_code
    - title
    - credits
    - grade
    - semester

    The GPA is calculated by averaging the grades of all the courses.

    Args:
        student_id (str): The ID of the student.

    Returns:
        dict: A dictionary containing the student's transcript information.
    """
    pipeline = [
        {"$match": {"student_id": student_id}},
        {"$lookup": {
            "from": "courses",
            "localField": "course_code",
            "foreignField": "course_code",
            "as": "course_info"
        }},
        {"$unwind": "$course_info"},
        {"$group": {
            "_id": "$student_id",
            "courses": {"$push": {
                "course_code": "$course_code",
                "title": "$course_info.title",
                "credits": "$course_info.credits",
                "grade": "$grade",
                "semester": "$semester"
            }},
            "total_credits": {"$sum": "$course_info.credits"},
            "gpa": {"$avg": {"$switch": {
                "branches": [
                    {"case": {"$eq": ["$grade", "A"]}, "then": 4.0},
                    {"case": {"$eq": ["$grade", "B"]}, "then": 3.0},
                    {"case": {"$eq": ["$grade", "C"]}, "then": 2.0},
                    {"case": {"$eq": ["$grade", "D"]}, "then": 1.0},
                ],
                "default": 0
            }}}
        }},
        {"$lookup": {
            "from": "students",
            "localField": "_id",
            "foreignField": "student_id",
            "as": "student_info"
        }},
        {"$unwind": "$student_info"},
        {"$project": {
            "name": "$student_info.name",
            "major": "$student_info.major",
            "year": "$student_info.year",
            "courses": 1,
            "total_credits": 1,
            "gpa": {"$round": ["$gpa", 2]}
        }}
    ]
    
    result = list(grades.aggregate(pipeline))
    return result[0] if result else None

def get_course_stats(course_code):
    """
    Get a course's statistics.

    Given a course code, this function will return a dictionary containing the
    course's title, department, credits, grade distribution, total number of
    students, and average grade.

    The grade distribution is a dictionary with the grades as keys and the
    number of students with that grade as values.

    The average grade is calculated by averaging the grades of all the
    students.

    Args:
        course_code (str): The code of the course.

    Returns:
        dict: A dictionary containing the course's statistics.
    """
    pipeline = [
        {"$match": {"course_code": course_code}},
        {"$group": {
            "_id": "$course_code",
            "grade_distribution": {
                "$push": {
                    "k": "$grade",
                    "v": {"$sum": 1}
                }
            },
            "total_students": {"$sum": 1},
            "average_grade": {"$avg": {"$switch": {
                "branches": [
                    {"case": {"$eq": ["$grade", "A"]}, "then": 4.0},
                    {"case": {"$eq": ["$grade", "B"]}, "then": 3.0},
                    {"case": {"$eq": ["$grade", "C"]}, "then": 2.0},
                    {"case": {"$eq": ["$grade", "D"]}, "then": 1.0},
                ],
                "default": 0
            }}}
        }},
        {"$project": {
            "grade_distribution": {"$arrayToObject": "$grade_distribution"},
            "total_students": 1,
            "average_grade": {"$round": ["$average_grade", 2]}
        }},
        {"$lookup": {
            "from": "courses",
            "localField": "_id",
            "foreignField": "course_code",
            "as": "course_info"
        }},
        {"$unwind": "$course_info"},
        {"$project": {
            "title": "$course_info.title",
            "department": "$course_info.department",
            "credits": "$course_info.credits",
            "grade_distribution": 1,
            "total_students": 1,
            "average_grade": 1
        }}
    ]
    
    result = list(grades.aggregate(pipeline))
    return result[0] if result else None

def get_department_performance():
    """
    Get the performance of each department in terms of average student grades.

    Returns a list of dictionaries, each containing the department name,
    total number of students, and average grade of all students in that
    department. The list is sorted in descending order of average grade.

    Returns:
        list: A list of dictionaries containing department performance information.
    """
    pipeline = [
        {"$lookup": {
            "from": "courses",
            "localField": "course_code",
            "foreignField": "course_code",
            "as": "course_info"
        }},
        {"$unwind": "$course_info"},
        {"$group": {
            "_id": "$course_info.department",
            "total_students": {"$sum": 1},
            "average_grade": {"$avg": {"$switch": {
                "branches": [
                    {"case": {"$eq": ["$grade", "A"]}, "then": 4.0},
                    {"case": {"$eq": ["$grade", "B"]}, "then": 3.0},
                    {"case": {"$eq": ["$grade", "C"]}, "then": 2.0},
                    {"case": {"$eq": ["$grade", "D"]}, "then": 1.0},
                ],
                "default": 0
            }}}
        }},
        {"$project": {
            "department": "$_id",
            "total_students": 1,
            "average_grade": {"$round": ["$average_grade", 2]}
        }},
        {"$sort": {"average_grade": -1}}
    ]
    
    return list(grades.aggregate(pipeline))

def update_student_majors(department, new_major):
    """
    Update student majors from the given department to the new major.

    Args:
        department (str): The department to update.
        new_major (str): The new major to set.

    Returns:
        None
    """
    result = students.update_many(
        {"major": department},
        {"$set": {"major": new_major}}
    )
    print(f"Updated {result.modified_count} student majors from {department} to {new_major}")

def cleanup_database():
    """
    Clean up the database by dropping all collections.

    This function is used to clean up the database after the script is run.
    It will drop all collections in the database, including students,
    professors, courses, and grades.

    The database is cleaned up by calling the drop() method on each
    collection.

    The function prints a message indicating that the database has been
    cleaned up and that all collections have been dropped.

    Returns:
        None
    """
    db.students.drop()
    db.professors.drop()
    db.courses.drop()
    db.grades.drop()
    print("Database cleaned up. All collections have been dropped.")

if __name__ == "__main__":
    try:
        # Generate sample data
        generate_sample_data()

        # Get a student's transcript
        student_transcript = get_student_transcript("S0001")
        print("\nStudent Transcript:")
        pprint.pprint(student_transcript)

        # Get course statistics
        course_stats = get_course_stats("C001")
        print("\nCourse Statistics:")
        pprint.pprint(course_stats)

        # Get department performance
        dept_performance = get_department_performance()
        print("\nDepartment Performance:")
        pprint.pprint(dept_performance)

        # Update student majors
        update_student_majors("Physics", "Applied Physics")

    finally:
        # Clean up the database
        cleanup_database()

        # Close the connection
        client.close()