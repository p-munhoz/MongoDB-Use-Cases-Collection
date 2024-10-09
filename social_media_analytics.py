from pymongo import MongoClient, UpdateOne
import datetime
import random

# Connect to MongoDB (Docker version)
client = MongoClient('mongodb://admin:password@localhost:27017/')
db = client['social_media']
posts = db['posts']
users = db['users']

# Create indexes for better query performance
posts.create_index([("author", 1), ("created_at", -1)])
posts.create_index([("tags", 1)])

def generate_sample_data(num_users=50, num_posts=1000):
    # Generate users

    user_ids = []
    for i in range(num_users):
        user = {
            "username": f"user_{i}",
            "email": f"user_{i}@example.com",
            "created_at": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365))
        }
        result = users.insert_one(user)
        user_ids.append(result.inserted_id)

    # Generate posts
    bulk_posts = []
    for i in range(num_posts):
        post = {
            "author": random.choice(user_ids),
            "content": f"This is post number {i}",
            "tags": random.sample(["tech", "sports", "politics", "entertainment", "science"], k=random.randint(1, 3)),
            "likes": random.randint(0, 1000),
            "comments": [],
            "created_at": datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
        }
        bulk_posts.append(post)
    
    posts.insert_many(bulk_posts)
    print(f"Generated {num_users} users and {num_posts} posts.")

def add_comment(post_id, user_id, content):
    """
    Add a comment to a post.

    Args:
        post_id (ObjectId): The id of the post to add the comment to.
        user_id (ObjectId): The id of the user posting the comment.
        content (str): The content of the comment.

    Returns:
        int: The number of documents modified.
    """
    
    comment = {
        "user": user_id,
        "content": content,
        "created_at": datetime.datetime.now()
    }
    result = posts.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment}}
    )
    return result.modified_count

def get_top_posts(limit=10, sort_by="likes"):
    """
    Get a list of the top posts sorted by the given criteria.

    Parameters:
    limit (int): The number of posts to return. Defaults to 10.
    sort_by (str): The field to sort by. Defaults to "likes".

    Returns:
        A list of dictionaries, each containing the post content, number of likes,
        author's username, and the number of comments.
    """
    pipeline = [
        {"$sort": {sort_by: -1}},
        {"$limit": limit},
        {"$lookup": {
            "from": "users",
            "localField": "author",
            "foreignField": "_id",
            "as": "author_info"
        }},
        {"$unwind": "$author_info"},
        {"$project": { # equivalent of select
            "content": 1,
            "likes": 1,
            "author": "$author_info.username",
            "comment_count": {"$size": "$comments"}
        }}
    ]
    return list(posts.aggregate(pipeline))

def get_post_distribution_by_tag():
    """
    Get a list of tag names and the number of posts each tag is associated with,
    sorted in descending order of the number of posts.

    Returns:
        A list of dictionaries, each containing a tag name and its count.
    """
    
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {
            "_id": "$tags",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    return list(posts.aggregate(pipeline))

def update_post_likes(num_updates=100):
    """
    Update a specified number of posts with a random like count change.

    Selects a specified number of posts and applies a random like count change to each.
    The like count change is between -5 and 10, inclusive.

    Parameters:
    num_updates (int): The number of posts to update. Defaults to 100.

    Returns:
    None
    """
    bulk_ops = []
    for post in posts.find().limit(num_updates):
        bulk_ops.append(
            UpdateOne(
                {"_id": post["_id"]},
                {"$inc": {"likes": random.randint(-5, 10)}}
            )
        )
    result = posts.bulk_write(bulk_ops)
    print(f"Updated {result.modified_count} posts.")

def add_random_comments(num_comments=500):
    """
    Add random comments to posts.

    Randomly selects a post and a user, then adds a comment to the post from the user.
    The comment content is just a generic string indicating the comment number.

    Args:
        num_comments (int): The number of comments to add. Defaults to 500.

    Returns:
        int: The number of comments added.
    """
    all_posts = list(posts.find({}, {"_id": 1}))
    all_users = list(users.find({}, {"_id": 1}))
    
    comment_count = 0
    for _ in range(num_comments):
        post = random.choice(all_posts)
        user = random.choice(all_users)
        if add_comment(post["_id"], user["_id"], f"Random comment {_}"):
            comment_count += 1
    
    return comment_count

def cleanup_database():
    db.posts.drop()
    db.users.drop()
    print("Database cleaned up. Collections 'posts' and 'users' have been dropped.")

if __name__ == "__main__":
    try:
        # Generate sample data
        generate_sample_data()

        # Add random comments
        comment_count = add_random_comments(500)
        print(f"Added {comment_count} comments randomly.")

        # Get top posts by likes
        print("\nTop 5 posts by likes:")
        for post in get_top_posts(5, "likes"):
            print(f"{post['content']} by {post['author']} - {post['likes']} likes, {post['comment_count']} comments")

        # Get top posts by comments
        print("\nTop 5 posts by number of comments:")
        for post in get_top_posts(5, "comment_count"):
            print(f"{post['content']} by {post['author']} - {post['likes']} likes, {post['comment_count']} comments")

        # Get post distribution by tag
        print("\nPost distribution by tag:")
        for tag_info in get_post_distribution_by_tag():
            print(f"{tag_info['_id']}: {tag_info['count']} posts")

        # Update post likes
        update_post_likes()

    finally:
        # Clean up the database
        cleanup_database()

        # Close the connection
        client.close()