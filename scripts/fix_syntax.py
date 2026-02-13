import re

# Read the file
with open('routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the syntax error - remove the extra closing parenthesis and restore the delete_activity decorator
old_pattern = r"return render_template\('edit_activity\.html', form=form, activity=activity\)\)\n@firebase_required\ndef delete_activity\(activity_id\):"

new_pattern = r"return render_template('edit_activity.html', form=form, activity=activity)" + "\n\n@routes_bp.route('/activities/<activity_id>/delete', methods=['POST'])\n@firebase_required\ndef delete_activity(activity_id):"

new_content = re.sub(old_pattern, new_pattern, content)

# Check if replacement was made
if new_content == content:
    print('ERROR: No fix applied - pattern not found')
    exit(1)
else:
    # Write the file
    with open('routes.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS: Fix completed')
    exit(0)
