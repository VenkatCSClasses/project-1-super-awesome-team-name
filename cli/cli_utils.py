def handle_authorization():
    """Helper function to handle authorization for protected commands"""
    token = load_token()
    if not token:
        print("[red]You must be logged in to perform this action.[/red]")
        return

    payload = jwt.decode(token, options={"verify_signature": False})
    permission = payload.get("permission")
    if permission is None:
        print("[red]Invalid token: permission level not found.[/red]")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    return headers