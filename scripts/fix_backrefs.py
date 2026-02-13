#!/usr/bin/env python3
import sys

with open('routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The regex replacement left literal backreferences \1\2 as bytes \x01\x02
# Fix by removing these and restoring the decorator
old_pattern = "return render_template('edit_activity.html', form=form, activity=activity)\x01\x02)\n@firebase_required\ndef delete_activity"
new_pattern = "return render_template('edit_activity.html', form=form, activity=activity)\n\n@routes_bp.route('/activities/<activity_id>/delete', methods=['POST'])\n@firebase_required\ndef delete_activity"

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Fixed backreference issue')
    sys.exit(0)
else:
    print('ERROR: Pattern with backreferences not found')
    # Try alternative - just look for the corrupted line and fix it
    if "activity=activity)\x01\x02)\n" in content:
        print('Found corrupted line, attempting alternative fix...')
        content = content.replace("activity=activity)\x01\x02)\n", "activity=activity)\n\n@routes_bp.route('/activities/<activity_id>/delete', methods=['POST'])\n")
        content = content.replace("@firebase_required\ndef delete_activity", "@firebase_required\ndef delete_activity")
        with open('routes.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('SUCCESS: Applied alternative fix')
        sys.exit(0)
    sys.exit(1)
