import msal
from msgraph.core import GraphClient

def get_graph_client(client_id, client_secret, tenant_id):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return GraphClient(token_credential=token["access_token"])

def purge_malicious_email(graph_client, subject_line, sender_email, user_id):
    search_query = f"subject:'{subject_line}' AND from:'{sender_email}'"
    messages = graph_client.get(f'/users/{user_id}/messages', params={'$search': search_query}).json().get('value', [])
    purged_count = 0
    for msg in messages:
        graph_client.delete(f"/users/{user_id}/messages/{msg['id']}")
        purged_count += 1
    return {"status": "success", "purged": purged_count}

def remediate_compromised_user(graph_client, user_id):
    # 1. Revoke existing sessions
    graph_client.post(f"/users/{user_id}/revokeSignInSessions")
    # 2. Force password reset on next login
    password_profile = {
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "forceChangePasswordNextSignInWithMfa": True
        }
    }
    graph_client.patch(f"/users/{user_id}", data=password_profile)
    # 3. Log the action (placeholder)
    print(f"Remediation initiated for {user_id}: Sessions revoked, Password reset enforced.")
    return "Remediation sequence complete."

# Example usage (fill in your values):
# client_id = 'YOUR_CLIENT_ID'
# client_secret = 'YOUR_CLIENT_SECRET'
# tenant_id = 'YOUR_TENANT_ID'
# user_id = 'user@domain.com' or objectId
# graph_client = get_graph_client(client_id, client_secret, tenant_id)
# purge_malicious_email(graph_client, 'Phish Subject', 'attacker@evil.com', user_id)
# remediate_compromised_user(graph_client, user_id)
