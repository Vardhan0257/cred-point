# n8n Workflow Setup Guide for CPE Management Platform

## Overview

This guide explains how to set up three n8n workflows to automate CPE grading, recommendations, and admin notifications for your credential management platform.

## Prerequisites

1. **n8n Instance**: n8n cloud (https://n8n.cloud) or self-hosted Docker instance.
2. **Google Firestore Credentials**: Service account JSON file with read/write access to your Firestore database.
3. **SendGrid API Key** (for email notifications): https://sendgrid.com
4. **Slack Webhook** (optional, for Slack notifications): https://slack.com/apps/manage/custom-integrations

## Workflows Included

### 1. Auto-Grade CPE Activity on Creation
**File**: `workflow_auto_grade_activity.json`

**Purpose**: Automatically grade CPE submissions based on OffSec rules.

**Flow**:
- Firestore detects new activity creation
- Grading function applies rules (course = 1 CPE/hour capped at 40, webinar = 1 CPE/hour, public speaking = 4 CPE, etc.)
- If auto-approvable (has duration, evidence, etc.), updates activity status to "approved"
- Creates verification record
- If pending manual review, marks status as "pending"

**Setup**:
1. Import `workflow_auto_grade_activity.json` into n8n
2. Configure Firestore credentials:
   - Click "Firestore Trigger" node
   - Set credentials to your service account JSON
   - Set collection to `users` (will listen to subcollection `activities`)
3. Enable workflow and test by creating a test activity

---

### 2. Daily CPE Recommendations Generator
**File**: `workflow_daily_recommendations.json`

**Purpose**: Generate personalized CPE recommendations for all users daily.

**Flow**:
- Scheduled trigger runs daily at 9:00 AM
- Fetches all users from Firestore
- Calls your backend recommendation engine (`/recommendations/generate` endpoint)
- Sends personalized email to each user with their recommendations

**Setup**:
1. Import `workflow_daily_recommendations.json` into n8n
2. Configure credentials:
   - Firestore: Set service account JSON
   - SendGrid: Paste your SendGrid API key
3. Modify the HTTP request node:
   - Change `http://localhost:5000/recommendations/generate` to your production URL
   - Consider adding authentication token if needed
4. Set schedule time (default 9:00 AM) in the "Schedule Daily" node
5. Enable workflow

**Note**: Your backend should have a `/recommendations/generate` endpoint. Add this to `routes.py` if missing:

```python
@routes_bp.route('/recommendations/generate', methods=['POST'])
@admin_required
def generate_recommendations_endpoint():
    uid = request.json.get('uid')
    force = request.json.get('force_generate', False)
    try:
        recs = generate_recommendations(None, None, uid, force_refresh=force)
        return jsonify({'success': True, 'recommendations': recs}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### 3. Admin Notification on Pending CPE
**File**: `workflow_admin_notifications.json`

**Purpose**: Alert admins (via Slack and email) when new CPE submissions are pending review.

**Flow**:
- Firestore document listener detects `status == 'pending'`
- Fetches admin user details
- Sends Slack message to `#admin-alerts` channel
- Sends email to admin with submission details and review link

**Setup**:
1. Import `workflow_admin_notifications.json` into n8n
2. Configure credentials:
   - Firestore: Set service account JSON
   - Slack: Create a webhook or use Slack Bot token
   - SendGrid: Paste your API key
3. Modify admin references:
   - Update `{{ $json.admin_uid }}` and `{{ $json.admin_email }}` to match your admin user ID and email
   - Or create a config lookup to fetch admin details from a settings collection
4. Set Slack channel (default `#admin-alerts`)
5. Enable workflow

---

## Importing Workflows into n8n

### n8n Cloud

1. Log in to https://n8n.cloud
2. Go to **Workflows** → **New**
3. Click the **⋮** menu (top right) → **Import from file**
4. Select the workflow JSON file
5. Configure credentials
6. Save and activate

### Self-Hosted n8n

1. Open your n8n instance (e.g., `http://localhost:5678`)
2. Navigate to **Workflows** → **New**
3. Click **⋮** → **Import from file**
4. Select the workflow JSON
5. Configure credentials (Firestore, SendGrid, Slack)
6. Save and activate

---

## Credentials Setup in n8n

### Firestore Credential
1. Go to **Credentials** → **New** → **Google Firestore**
2. Paste your GCP service account JSON
3. Name it `firestore_cred`

### SendGrid Credential
1. Go to **Credentials** → **New** → **SendGrid**
2. Paste your SendGrid API key
3. Name it `sendgrid_cred`

### Slack Credential (optional)
1. Go to **Credentials** → **New** → **Slack**
2. Use OAuth or a bot token
3. Name it `slack_cred`

---

## Configuration & Customization

### Grading Rules

Edit the `Grade Activity` function node in `workflow_auto_grade_activity.json` to adjust CPE award thresholds. Current rules:
- **Course**: 1 CPE/hour, cap 40
- **Webinar/Conference**: 1 CPE/hour
- **Public Speaking**: 4 CPE fixed
- **Published Paper**: 4 CPE fixed
- **Lab Submission**: 20 CPE (if accepted)
- **Default**: User-provided value (if evidence attached)

### Notification Recipients

For `workflow_admin_notifications.json`:
- Change `#admin-alerts` to your Slack channel
- Modify email template in the "Email Admin" node
- Update admin lookup logic (currently assumes `admin_uid` and `admin_email` from a document)

### Recommendation Schedule

In `workflow_daily_recommendations.json`, adjust the "Schedule Daily" node:
- Change `triggerAtHour` to desired time (0–23)
- Change `triggerAtMinute` for minute offset
- Change `triggerValue` and `triggerUnit` for frequency (e.g., every 2 days, every hour)

---

## Testing & Troubleshooting

### Test Auto-Grading
1. Activate `workflow_auto_grade_activity.json`
2. Create a new activity via your app's UI with:
   - `activity_type: "course"`
   - `duration_hours: 10`
   - `proof_file: [any file]`
3. Check Firestore to see if `status` changed to "approved" and `awarded_cpe` was set to 10

### Test Recommendations
1. Activate `workflow_daily_recommendations.json`
2. Manually trigger the workflow (click **Execute Workflow** in n8n)
3. Check email inbox for recommendation emails
4. Verify backend `/recommendations/generate` endpoint is accessible

### Test Admin Notifications
1. Activate `workflow_admin_notifications.json`
2. Create an activity with `status: "pending"` in Firestore
3. Check Slack `#admin-alerts` and admin email inbox

### Debug Logs
- Each n8n workflow has an **Execution** tab; click to see logs, errors, and data flow
- Check n8n logs for HTTP errors, credential issues, or Firestore query failures

---

## Security Best Practices

1. **Credentials**: Never commit service account JSON to version control. Store in n8n secret manager or environment variables.
2. **HTTPS**: Use HTTPS URLs for all outbound requests (SendGrid, Slack, your backend).
3. **Rate Limits**: Add delays between operations if hitting Firestore or SendGrid rate limits.
4. **Access Control**: Ensure n8n instance is behind authentication and firewall.
5. **Audit Logs**: Enable n8n audit logging to track workflow executions.

---

## Monitoring & Maintenance

- **Check workflow health** weekly; navigate to each workflow and review recent executions
- **Monitor Firestore quota** to ensure n8n workflows don't exceed free tier
- **Test after updates**: If you modify your backend, re-test workflows with sample data
- **Alert on failures**: Configure n8n notifications to email admins if a workflow fails

---

## Support & Next Steps

For issues:
1. Check n8n logs and execution history
2. Verify credentials and permissions in Firestore
3. Test individual nodes (right-click → Execute Node)
4. Review n8n documentation: https://docs.n8n.io/

For extending workflows:
- Add approval chains (multiple admins)
- Integrate with external LMS (SAP, Cornerstone, etc.)
- Auto-sync CPE data to certificate authorities
- Generate compliance reports (PDF/CSV)

---

*Last updated: February 6, 2026*
