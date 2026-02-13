import re

# Read the file
with open('routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the edit_activity function and replace it
# We'll look for the decorator and function definition
pattern = r'(@routes_bp\.route\(\'/activities/<activity_id>/edit\', methods=\[\'GET\', \'POST\'\], endpoint=\'edit_activity\'\)\n@firebase_required\ndef edit_activity\(activity_id\):.*?)(\n@routes_bp\.route\(\'/activities/<activity_id>/delete\', methods=\[\'POST\'\])'

replacement = '''@routes_bp.route('/activities/<activity_id>/edit', methods=['GET', 'POST'], endpoint='edit_activity')
@firebase_required
def edit_activity(activity_id):
    """
    Edit activity details (not CPE awards).
    CPE awards are handled separately via a different interface.
    Simplified to only update basic activity fields without authority validation.
    """
    uid = g.uid

    # Fetch activity
    raw_activities = get_user_activities(uid) or []
    activity = next((a for a in raw_activities if str(a.get('id')) == str(activity_id)), None)
    if not activity:
        flash('Activity not found.', 'danger')
        return redirect(url_for('routes.list_activities'))

    activity = normalize_activity(activity)
    form = ActivityForm()
    
    # Populate activity type choices
    activity_type_choices = sorted([t for t in ESTIMATED_ACTIVITY_RANGES.keys() if ESTIMATED_ACTIVITY_RANGES[t][0] > 0])
    form.activity_type.choices = [('', '----- Select Activity Type -----')] + [(t, t) for t in activity_type_choices]

    if request.method == 'GET':
        # Prefill form with existing data
        form.title.data = activity.get('title')
        form.provider.data = activity.get('provider')
        form.activity_type.data = activity.get('activity_type')
        form.description.data = activity.get('description')
        if activity.get('date_obj'):
            form.activity_date.data = activity['date_obj'].date()

    if request.method == 'POST' and form.validate_on_submit():
        # File upload (optional - use existing if not changed)
        proof_file_name = activity.get('proof_file')
        if form.proof_file.data:
            uploaded_file = form.proof_file.data
            
            is_valid, error_msg = validate_file_upload(uploaded_file)
            if not is_valid:
                flash(f'File upload error: {error_msg}', 'danger')
                return render_template('edit_activity.html', form=form, activity=activity)
            
            filename = secure_filename(uploaded_file.filename)
            unique_name = f"{uid}/{uuid4().hex}_{filename}"
            
            bucket = storage.bucket()
            blob = bucket.blob(f"proofs/{unique_name}")
            blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)
            proof_file_name = blob.name

        # Update only basic activity data
        updated_data = {
            'title': form.title.data,
            'provider': form.provider.data,
            'activity_type': form.activity_type.data,
            'description': form.description.data,
            'activity_date': form.activity_date.data.isoformat() if form.activity_date.data else None,
            'proof_file': proof_file_name,
        }

        from services.models import update_activity
        update_activity(uid, activity_id, updated_data)

        flash('Activity updated successfully!', 'success')
        return redirect(url_for('routes.list_activities'))

    return render_template('edit_activity.html', form=form, activity=activity)\1\2'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Check if replacement was made
if new_content == content:
    print('ERROR: No replacement made - pattern not found or already replaced')
    exit(1)
else:
    # Write the file
    with open('routes.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS: Replacement completed')
    exit(0)
