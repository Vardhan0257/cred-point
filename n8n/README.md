# n8n Workflow Integration Summary

## Files Created

This directory contains three n8n workflow JSONs and a comprehensive setup guide:

### Workflow JSONs

1. **workflow_auto_grade_activity.json**
   - Auto-grades CPE submissions on creation
   - Uses OffSec grading rules (1 CPE/hr for courses, 4 CPE for papers, etc.)
   - Sets `status: 'approved'` or `'pending'` based on auto-gradeability
   - Creates verification records

2. **workflow_daily_recommendations.json**
   - Runs daily at 9:00 AM (configurable)
   - Fetches all users from Firestore
   - Calls `/recommendations/generate` endpoint on your backend
   - Sends personalized recommendation emails via SendGrid

3. **workflow_admin_notifications.json**
   - Triggers on new activity with `status: 'pending'`
   - Sends Slack message to `#admin-alerts`
   - Sends email to admin with submission details
   - Includes link to admin review page

### Setup Guide

**N8N_SETUP_GUIDE.md** — Complete setup instructions including:
- Prerequisites (n8n instance, credentials)
- Import steps for cloud and self-hosted
- Configuration details for each workflow
- Customization options
- Testing & troubleshooting tips
- Security best practices

## Quick Start

1. **Install n8n** (cloud or self-hosted)
2. **Create credentials** in n8n for:
   - Google Firestore (service account JSON)
   - SendGrid (API key)
   - Slack (optional, for notifications)
3. **Import workflows** (see guide)
4. **Enable workflows** and test
5. **Monitor executions** in n8n dashboard

## Next Steps

- Backend endpoint `/recommendations/generate` has been added to `routes.py`
- Ensure your Firestore rules allow n8n service account access
- Test workflows with sample data before production deployment
- Set up monitoring/alerts for workflow failures

---

For detailed setup, configuration, and troubleshooting, see **N8N_SETUP_GUIDE.md**.
