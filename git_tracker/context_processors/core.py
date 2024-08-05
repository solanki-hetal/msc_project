from django.contrib import messages


class Navigation:

    def __init__(self, icon, name, url, current_active_url):
        self.icon = icon
        self.name = name
        self.url = url
        self.active = url.endswith(f":{current_active_url}")


class Message:

    def get_icon(self, level):
        return {
            messages.DEBUG: "bi-info-circle-fill",
            messages.INFO: "bi-info-circle-fill",
            messages.SUCCESS: "bi-check-circle-fill",
            messages.WARNING: "bi-exclamation-triangle-fill",
            messages.ERROR: "bi-exclamation-triangle-fill",
        }[level]
        
    def get_class_name(self, level):
        return {
            messages.DEBUG: "alert-info",
            messages.INFO: "alert-info",
            messages.SUCCESS: "alert-success",
            messages.WARNING: "alert-warning",
            messages.ERROR: "alert-danger",
        }[level]
        
    def __str__(self) -> str:
        return self.message

    def __init__(self, message, level):
        self.message = message
        self.icon = self.get_icon(level)
        self.class_name = self.get_class_name(level)


def navigation(request):
    active_url = request.resolver_match.url_name

    nav = [
        Navigation("bi-house-fill", "Dashboard", "tracker:home", active_url),
        Navigation("bi-shield-lock", "Access Tokens", "tracker:token_list", active_url),
        Navigation("bi-door-closed", "Sign out", "user:logout", active_url),
    ]
    return {"navigation": nav, "active_url": active_url}


def messages_handler(request):
    alerts = []
    for message in messages.get_messages(request):
        alerts.append(Message(message.message, message.level))
    return {"alerts": alerts}
