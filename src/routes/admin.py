from flask import Blueprint, request, jsonify, session, render_template_string
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.user import db
from src.models.blog import Blog, Admin
from datetime import datetime
import functools

admin_bp = Blueprint('admin', __name__)

# Admin login required decorator
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialize default admin user
def init_admin():
    admin = Admin.query.filter_by(email='admin@ay-group.net').first()
    if not admin:
        hashed_password = generate_password_hash('AYGroup@2025')
        new_admin = Admin(
            email='admin@ay-group.net',
            password=hashed_password,
            name='AYGroup'
        )
        db.session.add(new_admin)
        db.session.commit()

# Admin login page
@admin_bp.route('/admin')
def admin_login_page():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AY Group Admin Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #121111 0%, #444444 50%, #121111 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #c4c4c4;
        }
        
        .login-container {
            background: rgba(68, 68, 68, 0.3);
            backdrop-filter: blur(10px);
            border: 2px solid #bc9e24;
            border-radius: 15px;
            padding: 40px;
            width: 400px;
            box-shadow: 0 0 30px rgba(188, 158, 36, 0.3);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            color: #bc9e24;
            font-size: 2.5em;
            font-weight: bold;
            text-shadow: 0 0 20px rgba(188, 158, 36, 0.5);
        }
        
        .logo p {
            color: #d6c78b;
            margin-top: 10px;
            font-size: 0.9em;
            letter-spacing: 2px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #c4c4c4;
            font-weight: 500;
        }
        
        input[type="email"], input[type="password"] {
            width: 100%;
            padding: 12px;
            background: rgba(68, 68, 68, 0.5);
            border: 1px solid #575757;
            border-radius: 8px;
            color: #c4c4c4;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input[type="email"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #bc9e24;
            box-shadow: 0 0 10px rgba(188, 158, 36, 0.3);
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(45deg, #bc9e24, #d6c78b);
            border: none;
            border-radius: 8px;
            color: #121111;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(188, 158, 36, 0.4);
        }
        
        .error {
            color: #ff4444;
            text-align: center;
            margin-top: 15px;
            display: none;
        }
        
        .success {
            color: #44ff44;
            text-align: center;
            margin-top: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>AY GROUP</h1>
            <p>ADMIN PANEL</p>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn">LOGIN</button>
            
            <div id="error" class="error"></div>
            <div id="success" class="success"></div>
        </form>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            
            try {
                const response = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    successDiv.textContent = 'Login successful! Redirecting...';
                    successDiv.style.display = 'block';
                    errorDiv.style.display = 'none';
                    setTimeout(() => {
                        window.location.href = '/api/admin/dashboard';
                    }, 1000);
                } else {
                    errorDiv.textContent = data.error || 'Login failed';
                    errorDiv.style.display = 'block';
                    successDiv.style.display = 'none';
                }
            } catch (error) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.style.display = 'block';
                successDiv.style.display = 'none';
            }
        });
    </script>
</body>
</html>
    ''')

# Admin login API
@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    admin = Admin.query.filter_by(email=email).first()
    
    if admin and check_password_hash(admin.password, password):
        session['admin_id'] = admin.id
        session['admin_name'] = admin.name
        return jsonify({'message': 'Login successful', 'admin': admin.to_dict()}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Admin logout
@admin_bp.route('/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Admin dashboard
@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AY Group Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #121111 0%, #444444 50%, #121111 100%);
            min-height: 100vh;
            color: #c4c4c4;
        }
        
        .header {
            background: rgba(68, 68, 68, 0.3);
            backdrop-filter: blur(10px);
            border-bottom: 2px solid #bc9e24;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo h1 {
            color: #bc9e24;
            font-size: 1.8em;
            text-shadow: 0 0 10px rgba(188, 158, 36, 0.5);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .logout-btn {
            padding: 8px 16px;
            background: linear-gradient(45deg, #bc9e24, #d6c78b);
            border: none;
            border-radius: 5px;
            color: #121111;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 3px 10px rgba(188, 158, 36, 0.4);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(68, 68, 68, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid #575757;
            border-radius: 10px;
            padding: 20px;
        }
        
        .card h2 {
            color: #bc9e24;
            margin-bottom: 20px;
            text-shadow: 0 0 5px rgba(188, 158, 36, 0.3);
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #c4c4c4;
            font-weight: 500;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 10px;
            background: rgba(68, 68, 68, 0.5);
            border: 1px solid #575757;
            border-radius: 5px;
            color: #c4c4c4;
            font-size: 14px;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #bc9e24;
            box-shadow: 0 0 5px rgba(188, 158, 36, 0.3);
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .btn {
            padding: 10px 20px;
            background: linear-gradient(45deg, #bc9e24, #d6c78b);
            border: none;
            border-radius: 5px;
            color: #121111;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 3px 10px rgba(188, 158, 36, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(45deg, #ff4444, #ff6666);
        }
        
        .blog-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .blog-item {
            background: rgba(87, 87, 87, 0.3);
            border: 1px solid #575757;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .blog-item:hover {
            border-color: #bc9e24;
            transform: translateY(-2px);
        }
        
        .blog-title {
            color: #bc9e24;
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .blog-meta {
            color: #969696;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .blog-excerpt {
            color: #c4c4c4;
            font-size: 0.95em;
            line-height: 1.4;
            margin-bottom: 10px;
        }
        
        .blog-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn-small {
            padding: 5px 10px;
            font-size: 0.8em;
        }
        
        .message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            display: none;
        }
        
        .message.success {
            background: rgba(68, 255, 68, 0.1);
            border: 1px solid #44ff44;
            color: #44ff44;
        }
        
        .message.error {
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid #ff4444;
            color: #ff4444;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <h1>AY GROUP ADMIN</h1>
        </div>
        <div class="user-info">
            <span>Welcome, {{ session.admin_name }}</span>
            <button class="logout-btn" onclick="logout()">Logout</button>
        </div>
    </div>
    
    <div class="container">
        <div id="message" class="message"></div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>Create New Blog Post</h2>
                <form id="blogForm">
                    <input type="hidden" id="blogId" name="blogId">
                    
                    <div class="form-group">
                        <label for="title">Title:</label>
                        <input type="text" id="title" name="title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="excerpt">Excerpt:</label>
                        <textarea id="excerpt" name="excerpt" placeholder="Brief description..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="category">Category:</label>
                        <select id="category" name="category">
                            <option value="">Select Category</option>
                            <option value="Technology">Technology</option>
                            <option value="Business">Business</option>
                            <option value="Innovation">Innovation</option>
                            <option value="News">News</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="content">Content:</label>
                        <textarea id="content" name="content" required placeholder="Write your blog content here..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="published" name="published" checked>
                            Published
                        </label>
                    </div>
                    
                    <button type="submit" class="btn" id="submitBtn">Create Post</button>
                    <button type="button" class="btn btn-danger" onclick="resetForm()" id="cancelBtn" style="display: none;">Cancel</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Blog Posts</h2>
                <div id="blogList" class="blog-list">
                    <!-- Blog posts will be loaded here -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let editingBlogId = null;
        
        // Load blogs on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadBlogs();
        });
        
        // Blog form submission
        document.getElementById('blogForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const blogData = {
                title: formData.get('title'),
                excerpt: formData.get('excerpt'),
                category: formData.get('category'),
                content: formData.get('content'),
                published: formData.get('published') === 'on'
            };
            
            try {
                let response;
                if (editingBlogId) {
                    response = await fetch(`/api/admin/blogs/${editingBlogId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(blogData)
                    });
                } else {
                    response = await fetch('/api/admin/blogs', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(blogData)
                    });
                }
                
                const result = await response.json();
                
                if (response.ok) {
                    showMessage(editingBlogId ? 'Blog updated successfully!' : 'Blog created successfully!', 'success');
                    resetForm();
                    loadBlogs();
                } else {
                    showMessage(result.error || 'Operation failed', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
            }
        });
        
        async function loadBlogs() {
            try {
                const response = await fetch('/api/admin/blogs');
                const blogs = await response.json();
                
                const blogList = document.getElementById('blogList');
                blogList.innerHTML = '';
                
                blogs.forEach(blog => {
                    const blogItem = document.createElement('div');
                    blogItem.className = 'blog-item';
                    blogItem.innerHTML = `
                        <div class="blog-title">${blog.title}</div>
                        <div class="blog-meta">
                            By ${blog.author} | ${new Date(blog.created_at).toLocaleDateString()} | ${blog.category || 'Uncategorized'}
                            ${blog.published ? '<span style="color: #44ff44;">Published</span>' : '<span style="color: #ff4444;">Draft</span>'}
                        </div>
                        <div class="blog-excerpt">${blog.excerpt || blog.content.substring(0, 150) + '...'}</div>
                        <div class="blog-actions">
                            <button class="btn btn-small" onclick="editBlog(${blog.id})">Edit</button>
                            <button class="btn btn-danger btn-small" onclick="deleteBlog(${blog.id})">Delete</button>
                        </div>
                    `;
                    blogList.appendChild(blogItem);
                });
            } catch (error) {
                showMessage('Failed to load blogs', 'error');
            }
        }
        
        async function editBlog(id) {
            try {
                const response = await fetch(`/api/admin/blogs/${id}`);
                const blog = await response.json();
                
                document.getElementById('blogId').value = blog.id;
                document.getElementById('title').value = blog.title;
                document.getElementById('excerpt').value = blog.excerpt || '';
                document.getElementById('category').value = blog.category || '';
                document.getElementById('content').value = blog.content;
                document.getElementById('published').checked = blog.published;
                
                document.getElementById('submitBtn').textContent = 'Update Post';
                document.getElementById('cancelBtn').style.display = 'inline-block';
                
                editingBlogId = id;
            } catch (error) {
                showMessage('Failed to load blog for editing', 'error');
            }
        }
        
        async function deleteBlog(id) {
            if (confirm('Are you sure you want to delete this blog post?')) {
                try {
                    const response = await fetch(`/api/admin/blogs/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        showMessage('Blog deleted successfully!', 'success');
                        loadBlogs();
                    } else {
                        const result = await response.json();
                        showMessage(result.error || 'Delete failed', 'error');
                    }
                } catch (error) {
                    showMessage('Network error. Please try again.', 'error');
                }
            }
        }
        
        function resetForm() {
            document.getElementById('blogForm').reset();
            document.getElementById('blogId').value = '';
            document.getElementById('submitBtn').textContent = 'Create Post';
            document.getElementById('cancelBtn').style.display = 'none';
            editingBlogId = null;
        }
        
        function showMessage(text, type) {
            const message = document.getElementById('message');
            message.textContent = text;
            message.className = `message ${type}`;
            message.style.display = 'block';
            
            setTimeout(() => {
                message.style.display = 'none';
            }, 5000);
        }
        
        async function logout() {
            try {
                await fetch('/api/admin/logout', { method: 'POST' });
                window.location.href = '/api/admin';
            } catch (error) {
                console.error('Logout failed:', error);
            }
        }
    </script>
</body>
</html>
    ''')

# Get all blogs (admin)
@admin_bp.route('/admin/blogs', methods=['GET'])
@login_required
def get_blogs():
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return jsonify([blog.to_dict() for blog in blogs]), 200

# Get single blog (admin)
@admin_bp.route('/admin/blogs/<int:blog_id>', methods=['GET'])
@login_required
def get_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return jsonify(blog.to_dict()), 200

# Create blog
@admin_bp.route('/admin/blogs', methods=['POST'])
@login_required
def create_blog():
    data = request.get_json()
    
    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    blog = Blog(
        title=data['title'],
        content=data['content'],
        excerpt=data.get('excerpt', ''),
        author=session.get('admin_name', 'AYGroup'),
        published=data.get('published', True),
        category=data.get('category', '')
    )
    
    db.session.add(blog)
    db.session.commit()
    
    return jsonify(blog.to_dict()), 201

# Update blog
@admin_bp.route('/admin/blogs/<int:blog_id>', methods=['PUT'])
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    data = request.get_json()
    
    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    blog.title = data['title']
    blog.content = data['content']
    blog.excerpt = data.get('excerpt', '')
    blog.published = data.get('published', True)
    blog.category = data.get('category', '')
    blog.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(blog.to_dict()), 200

# Delete blog
@admin_bp.route('/admin/blogs/<int:blog_id>', methods=['DELETE'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    
    return jsonify({'message': 'Blog deleted successfully'}), 200

# Public API to get published blogs
@admin_bp.route('/blogs', methods=['GET'])
def get_public_blogs():
    blogs = Blog.query.filter_by(published=True).order_by(Blog.created_at.desc()).all()
    return jsonify([blog.to_dict() for blog in blogs]), 200

# Public API to get single published blog
@admin_bp.route('/blogs/<int:blog_id>', methods=['GET'])
def get_public_blog(blog_id):
    blog = Blog.query.filter_by(id=blog_id, published=True).first_or_404()
    return jsonify(blog.to_dict()), 200

