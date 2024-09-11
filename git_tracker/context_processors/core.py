from django.contrib import messages


class Navigation:
    '''
    A class to represent a navigation item in the sidebar.
    icon : str -> The icon to display in the sidebar.
    name : str -> The name of the navigation item.
    url : str -> The url to navigate to.
    active : bool -> If the navigation item is active.
    '''

    def __init__(self, icon, name, url, current_active_url):
        self.icon = icon
        self.name = name
        self.url = url
        self.active = url.endswith(f":{current_active_url}")


class Message:
    '''
    A class to represent a messages to be displayed to the user.
    message : str -> The message to display.
    icon : str -> The icon to display with the message.
    class_name : str -> The class name to apply to the message.
    '''

    def get_icon(self, level):
        # Get the icon based on the message level
        return {
            messages.DEBUG: "bi-info-circle-fill",
            messages.INFO: "bi-info-circle-fill",
            messages.SUCCESS: "bi-check-circle-fill",
            messages.WARNING: "bi-exclamation-triangle-fill",
            messages.ERROR: "bi-exclamation-triangle-fill",
        }[level]
        
    def get_class_name(self, level):
        # get the class name based on the message level
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
    # Define the navigation items
    nav = [
        Navigation("bi-house-fill", "Dashboard", "tracker:dashboard", active_url),
        Navigation("bi-shield-lock", "Access Tokens", "tracker:gittoken_list", active_url),
        Navigation("bi-journal", "Repositories", "tracker:repository_list", active_url),
        Navigation("bi-journal", "Anomalies", "tracker:anomaly_list", active_url),
        Navigation("bi-door-closed", "Sign out", "user:logout", active_url),
    ]
    return {"navigation": nav, "active_url": active_url}


def messages_handler(request):
    alerts = []
    for message in messages.get_messages(request):
        # Add the message to the alerts list
        alerts.append(Message(message.message, message.level))
    return {"alerts": alerts}
