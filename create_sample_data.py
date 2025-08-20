#!/usr/bin/env python3
"""
Demo script for MongoDB Visualizer
Creates sample data for testing the application
"""

from pymongo import MongoClient
import random
from datetime import datetime, timedelta
import json


def create_sample_data():
    """Create sample data in MongoDB for testing the visualizer"""
    
    # Connect to MongoDB (assumes MongoDB is running locally)
    try:
        client = MongoClient('mongodb://localhost:27017/')
        
        # Create a sample database
        db = client['sample_app_db']
        
        # Create sample collections with different types of data
        create_users_collection(db)
        create_products_collection(db)
        create_orders_collection(db)
        
        print("Sample data created successfully!")
        print("You can now connect to 'localhost:27017' and explore the 'sample_app_db' database")
        
        client.close()
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        print("Make sure MongoDB is running on localhost:27017")


def create_users_collection(db):
    """Create a users collection with sample data"""
    users = db['users']
    
    # Clear existing data
    users.drop()
    
    # Sample user data
    sample_users = []
    first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa', 'Tom', 'Anna']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
    statuses = ['active', 'inactive', 'pending']
    
    for i in range(50):
        user = {
            'user_id': f"user_{i+1:03d}",
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f"user{i+1}@company.com",
            'age': random.randint(22, 65),
            'department': random.choice(departments),
            'salary': random.randint(40000, 120000),
            'status': random.choice(statuses),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
            'profile': {
                'bio': f"Bio for user {i+1}",
                'skills': random.sample(['Python', 'JavaScript', 'SQL', 'MongoDB', 'React', 'Node.js', 'Docker', 'AWS'], 
                                      random.randint(2, 5)),
                'experience_years': random.randint(1, 20)
            },
            'preferences': {
                'theme': random.choice(['light', 'dark']),
                'notifications': random.choice([True, False]),
                'language': random.choice(['en', 'es', 'fr', 'de'])
            }
        }
        sample_users.append(user)
    
    users.insert_many(sample_users)
    print(f"Created {len(sample_users)} users")


def create_products_collection(db):
    """Create a products collection with sample data"""
    products = db['products']
    
    # Clear existing data
    products.drop()
    
    # Sample product data
    sample_products = []
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']
    conditions = ['new', 'used', 'refurbished']
    
    for i in range(100):
        product = {
            'product_id': f"prod_{i+1:03d}",
            'name': f"Product {i+1}",
            'description': f"Description for product {i+1}",
            'category': random.choice(categories),
            'brand': random.choice(brands),
            'price': round(random.uniform(10.99, 999.99), 2),
            'condition': random.choice(conditions),
            'in_stock': random.choice([True, False]),
            'quantity': random.randint(0, 100),
            'rating': round(random.uniform(1.0, 5.0), 1),
            'reviews_count': random.randint(0, 500),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 180)),
            'specifications': {
                'weight': f"{random.uniform(0.1, 10.0):.2f} kg",
                'dimensions': {
                    'length': random.randint(10, 100),
                    'width': random.randint(10, 100),
                    'height': random.randint(5, 50)
                },
                'color': random.choice(['Red', 'Blue', 'Green', 'Black', 'White', 'Yellow'])
            },
            'tags': random.sample(['popular', 'bestseller', 'new', 'discount', 'premium', 'eco-friendly'], 
                                random.randint(1, 3))
        }
        sample_products.append(product)
    
    products.insert_many(sample_products)
    print(f"Created {len(sample_products)} products")


def create_orders_collection(db):
    """Create an orders collection with sample data"""
    orders = db['orders']
    
    # Clear existing data
    orders.drop()
    
    # Sample order data
    sample_orders = []
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
    
    for i in range(200):
        order_items = []
        num_items = random.randint(1, 5)
        
        for j in range(num_items):
            order_items.append({
                'product_id': f"prod_{random.randint(1, 100):03d}",
                'quantity': random.randint(1, 3),
                'price': round(random.uniform(10.99, 299.99), 2)
            })
        
        total_amount = sum(item['quantity'] * item['price'] for item in order_items)
        
        order = {
            'order_id': f"order_{i+1:04d}",
            'user_id': f"user_{random.randint(1, 50):03d}",
            'status': random.choice(statuses),
            'payment_method': random.choice(payment_methods),
            'total_amount': round(total_amount, 2),
            'items': order_items,
            'shipping_address': {
                'street': f"{random.randint(100, 9999)} Main St",
                'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                'state': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
                'zip_code': f"{random.randint(10000, 99999)}"
            },
            'created_at': datetime.now() - timedelta(days=random.randint(1, 90)),
            'notes': f"Order notes for order {i+1}" if random.choice([True, False]) else None
        }
        sample_orders.append(order)
    
    orders.insert_many(sample_orders)
    print(f"Created {len(sample_orders)} orders")


if __name__ == '__main__':
    print("Creating sample data for MongoDB Visualizer...")
    create_sample_data()
