"""
Database module for user management
Stores user information and face embeddings
"""

import sqlite3
import os
import numpy as np
import pickle
from datetime import datetime
from typing import Optional, List, Dict, Tuple


class UserDatabase:
    """Manages user data storage"""
    
    def __init__(self, db_path='data/users.db'):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Face embeddings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS face_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Login history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                liveness_score REAL,
                confidence_score REAL,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, name: str, face_embedding: np.ndarray, 
                     image_path: str, email: str = None) -> Tuple[bool, str]:
        """
        Register a new user
        
        Args:
            name: User's name
            face_embedding: Face embedding vector
            image_path: Path to user's face image
            email: Optional email
            
        Returns:
            (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
            if cursor.fetchone():
                conn.close()
                return False, f"User '{name}' already exists"
            
            # Insert user
            cursor.execute(
                'INSERT INTO users (name, email) VALUES (?, ?)',
                (name, email)
            )
            user_id = cursor.lastrowid
            
            # Store face embedding
            embedding_blob = pickle.dumps(face_embedding)
            cursor.execute(
                'INSERT INTO face_embeddings (user_id, embedding, image_path) VALUES (?, ?, ?)',
                (user_id, embedding_blob, image_path)
            )
            
            conn.commit()
            conn.close()
            
            return True, f"User '{name}' registered successfully"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def get_all_users(self) -> List[Dict]:
        """Get all registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.name, u.email, u.created_at, u.last_login,
                   fe.image_path
            FROM users u
            LEFT JOIN face_embeddings fe ON u.id = fe.user_id
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'created_at': row[3],
                'last_login': row[4],
                'image_path': row[5]
            })
        
        conn.close()
        return users
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.name, u.email, u.created_at, u.last_login,
                   fe.image_path, fe.embedding
            FROM users u
            LEFT JOIN face_embeddings fe ON u.id = fe.user_id
            WHERE u.id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'created_at': row[3],
                'last_login': row[4],
                'image_path': row[5],
                'embedding': pickle.loads(row[6]) if row[6] else None
            }
        return None
    
    def get_user_by_name(self, name: str) -> Optional[Dict]:
        """Get user by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.name, u.email, u.created_at, u.last_login,
                   fe.image_path, fe.embedding
            FROM users u
            LEFT JOIN face_embeddings fe ON u.id = fe.user_id
            WHERE u.name = ?
        ''', (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'created_at': row[3],
                'last_login': row[4],
                'image_path': row[5],
                'embedding': pickle.loads(row[6]) if row[6] else None
            }
        return None
    
    def get_all_face_embeddings(self) -> List[Tuple[int, str, np.ndarray]]:
        """
        Get all face embeddings for recognition
        
        Returns:
            List of (user_id, name, embedding)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.name, fe.embedding
            FROM users u
            JOIN face_embeddings fe ON u.id = fe.user_id
        ''')
        
        embeddings = []
        for row in cursor.fetchall():
            user_id, name, embedding_blob = row
            embedding = pickle.loads(embedding_blob)
            embeddings.append((user_id, name, embedding))
        
        conn.close()
        return embeddings
    
    def update_last_login(self, user_id: int):
        """Update user's last login time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user_id)
        )
        
        conn.commit()
        conn.close()
    
    def add_login_history(self, user_id: int, liveness_score: float,
                         confidence_score: float, status: str):
        """Add login attempt to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO login_history (user_id, liveness_score, confidence_score, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, liveness_score, confidence_score, status))
        
        conn.commit()
        conn.close()
    
    def get_login_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's login history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT login_time, liveness_score, confidence_score, status
            FROM login_history
            WHERE user_id = ?
            ORDER BY login_time DESC
            LIMIT ?
        ''', (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'login_time': row[0],
                'liveness_score': row[1],
                'confidence_score': row[2],
                'status': row[3]
            })
        
        conn.close()
        return history
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_user_count(self) -> int:
        """Get total number of registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

