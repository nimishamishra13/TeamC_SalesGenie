# modules/crm_integration.py


def sync_activity_to_crm(
        lead_id,
        summary,
        action_items
):

    # Future:
    # Salesforce API
    # HubSpot API
    # Zoho CRM API


    crm_data = {

        "lead_id": lead_id,

        "activity_type":
        "Conversation Analysis",

        "summary":
        summary,

        "action_items":
        action_items,

        "status":
        "Synced"

    }


    return crm_data
