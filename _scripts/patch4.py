import re

with open('users/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update GET block to fetch success_data
old_get = r'''    if request\.method == 'POST':'''
new_get = r'''    if request.method == 'GET':
        success_data = request.session.pop('upload_success', None)
        return render(request, 'users/bulk_upload.html', {'success_data': success_data})

    if request.method == 'POST':'''
text = re.sub(old_get, new_get, text, count=1)

# 2. Update preview data length
old_preview = r'''preview_data = df\.head\(10\)\.to_dict\('records'\)'''
new_preview = r'''preview_data = df.to_dict('records')'''
text = re.sub(old_preview, new_preview, text)

# 3. Update upload completion message
old_upload_end = r'''                if skipped_rows:
                    messages\.warning\(request, f"Some rows were skipped: \{'; '\.join\(skipped_rows\)\}"\)
                messages\.success\(request, 'Data upload completed!'\)
                fs\.delete\(filename\)
                if 'temp_excel_file' in request\.session:
                    del request\.session\['temp_excel_file'\]
                return redirect\('bulk_upload'\)'''

new_upload_end = r'''                # Set success data in session
                request.session['upload_success'] = {
                    'total': len(df),
                    'inserted': len(df) - len(skipped_rows),
                    'skipped': len(skipped_rows),
                    'skipped_details': skipped_rows
                }

                fs.delete(filename)
                if 'temp_excel_file' in request.session:
                    del request.session['temp_excel_file']
                return redirect('bulk_upload')'''

text = re.sub(old_upload_end, new_upload_end, text)

# Wait, the end of the view originally had:
# return render(request, 'users/bulk_upload.html')
# We need to remove that if we return in GET.
old_final_return = r'''    return render\(request, 'users/bulk_upload\.html'\)'''
new_final_return = r'''    # Fallback return
    return render(request, 'users/bulk_upload.html')'''
text = re.sub(old_final_return, new_final_return, text)

with open('users/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated views.py!')
