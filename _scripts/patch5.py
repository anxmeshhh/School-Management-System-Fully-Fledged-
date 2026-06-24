import re

with open('users/templates/users/bulk_upload.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update preview-table CSS to add max-height and overflow-y
old_css = r'''    \.preview-table \{
        overflow-x: auto;
        border-radius: 12px;
        border: 2px solid var\(--border-color\);
        box-shadow: var\(--shadow-sm\);
        margin-bottom: 2rem;
        transition: var\(--transition\);
        -webkit-overflow-scrolling: touch;
    \}'''

new_css = r'''    .preview-table {
        overflow-x: auto;
        overflow-y: auto;
        max-height: 600px;
        border-radius: 12px;
        border: 2px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        margin-bottom: 2rem;
        transition: var(--transition);
        -webkit-overflow-scrolling: touch;
    }
    
    .success-card {
        background: #f0fdf4;
        border: 2px solid #bbf7d0;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    .success-card i {
        margin-bottom: 1rem;
    }
    
    .success-card h2 {
        color: #166534;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .success-card p.success-text {
        color: #15803d;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    
    .success-card .skipped-section {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 1rem;
        text-align: left;
        margin-top: 1.5rem;
    }
    
    .success-card .skipped-section h4 {
        color: #991b1b;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .success-card .skipped-section ul {
        list-style-type: none;
        padding-left: 0;
        margin-bottom: 0;
    }
    
    .success-card .skipped-section li {
        color: #7f1d1d;
        font-size: 0.9rem;
        padding: 0.25rem 0;
        border-bottom: 1px solid #fee2e2;
    }
    
    .success-card .skipped-section li:last-child {
        border-bottom: none;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }'''

text = re.sub(old_css, new_css, text)

# 2. Add the success-data UI block in the HTML
old_html = r'''            <div class="form-container">
                <form id="uploadForm" action="\{% url 'bulk_upload' %\}" method="post" enctype="multipart/form-data">'''

new_html = r'''            {% if success_data %}
            <div class="success-card">
                <i class="fas fa-check-circle" style="font-size: 4rem; color: #22c55e;"></i>
                <h2>Upload Successful!</h2>
                <p class="success-text">Successfully imported <strong>{{ success_data.inserted }}</strong> out of {{ success_data.total }} records.</p>
                
                {% if success_data.skipped > 0 %}
                    <div class="skipped-section">
                        <h4><i class="fas fa-exclamation-triangle"></i> Skipped {{ success_data.skipped }} records:</h4>
                        <ul>
                        {% for detail in success_data.skipped_details %}
                            <li>{{ detail }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                {% endif %}
                
                <div style="margin-top: 2rem;">
                    <a href="{% url 'admin_master' %}" class="back-btn" style="background: var(--white);">
                        <i class="fas fa-arrow-left"></i> Return to Master Data
                    </a>
                </div>
            </div>
            {% endif %}

            <div class="form-container">
                <form id="uploadForm" action="{% url 'bulk_upload' %}" method="post" enctype="multipart/form-data">'''

text = re.sub(old_html, new_html, text)

with open('users/templates/users/bulk_upload.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated bulk_upload.html!')
