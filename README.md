# NoSQL MongoDB Scripts

This repository contains three Python scripts demonstrating various aspects of working with MongoDB, a popular NoSQL database. These scripts range from basic operations to advanced data modeling and analysis.

## Table of Contents

1. [Bookstore Management](#1-bookstore-management)
2. [Social Media Analytics](#2-social-media-analytics)
3. [University Management System](#3-university-management-system)
4. [Requirements](#requirements)
5. [Setup and Running](#setup-and-running)

## 1. Bookstore Management

**File:** `bookstore_management.py`

This script demonstrates basic MongoDB operations in a bookstore context.

### Key Features:

- Basic CRUD operations (Create, Read, Update, Delete)
- Simple data modeling for books
- Basic querying and updating

### Main Functions:

- `insert_book()`: Adds a new book to the collection
- `find_books_by_genre()`: Retrieves books of a specific genre
- `update_book_price()`: Updates the price of a book
- `delete_book()`: Removes a book from the collection

## 2. Social Media Analytics

**File:** `social_media_analytics.py`

This script showcases more advanced MongoDB operations in a social media context.

### Key Features:

- Advanced data modeling with nested documents (comments within posts)
- Use of aggregation pipelines for complex queries
- Indexing for query optimization
- Bulk write operations for efficiency
- Error handling and database cleanup

### Main Functions:

- `generate_sample_data()`: Creates a dataset of users and posts
- `add_random_comments()`: Adds comments randomly across posts
- `get_top_posts()`: Uses aggregation pipeline for advanced sorting and data shaping
- `get_post_distribution_by_tag()`: Uses aggregation for tag analysis
- `update_post_likes()`: Implements bulk write operations
- `cleanup_database()`: Ensures proper cleanup after script execution

## 3. University Management System

**File:** `university_management_system.py`

This script showcases advanced MongoDB usage in a complex domain: a university management system.

### Key Features:

- Complex data modeling with multiple related collections (students, professors, courses, grades)
- Advanced indexing, including compound and unique indexes
- Complex aggregation pipelines for data analysis
- Use of `$lookup` for joining data across collections
- Dynamic field creation using `$arrayToObject`
- Complex data generation with interrelated documents

### Main Functions:

- `generate_sample_data()`: Creates a comprehensive dataset for a university
- `get_student_transcript()`: Generates a student's transcript using complex aggregation
- `get_course_stats()`: Analyzes course performance using aggregation
- `get_department_performance()`: Computes department-level statistics
- `update_student_majors()`: Demonstrates bulk update operations
- `cleanup_database()`: Ensures proper cleanup of all collections

## Requirements

- Python 3.7+
- pymongo
- Docker and Docker Compose

## Setup and Running

1. Ensure Docker and Docker Compose are installed on your system.

2. Start MongoDB using Docker Compose:
   ```
   docker-compose up -d
   ```

   The `docker-compose.yml` file should contain:
   ```yaml
   version: '3.8'
   services:
     mongodb:
       image: mongo:latest
       container_name: mongodb
       ports:
         - "27017:27017"
       volumes:
         - mongodb_data:/data/db
       environment:
         - MONGO_INITDB_ROOT_USERNAME=admin
         - MONGO_INITDB_ROOT_PASSWORD=password

   volumes:
     mongodb_data:
   ```

3. Install required Python packages:
   ```
   pip install pymongo
   ```

4. Run any of the scripts:
   ```
   python bookstore_management.py
   python social_media_analytics.py
   python university_management_system.py
   ```

Each script will generate its own data, perform operations, and clean up after execution.

**Note:** These scripts are designed for educational purposes and demonstrate various MongoDB operations. In a production environment, you would need to implement proper error handling, security measures, and optimize for performance based on your specific use case.