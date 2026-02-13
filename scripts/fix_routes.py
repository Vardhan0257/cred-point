#!/usr/bin/env python3
import sys

with open('routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: remove the extra closing parenthesis and add the missing decorator
old_pattern = "return render_template('edit_activity.html', form=form, activity=activity))\n@firebase_required\ndef delete_activity"
new_pattern = "return render_template('edit_activity.html', form=form, activity=activity)\n\n@routes_bp.route('/activities/<activity_id>/delete', methods=['POST'])\n@firebase_required\ndef delete_activity"

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Fixed syntax error')
    sys.exit(0)
else:
    print('ERROR: Pattern not found')
    sys.exit(1)
