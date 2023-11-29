# Definitions for email messages
EMAIL_MESSAGES = {
    "Ticket Creation": {
        "subject": "Support Ticket #{ticket_number} Received",
        "message": """
            Dear {user_name},

            We are pleased to confirm that we have received your Support Ticket:
            Support Ticket Number: {ticket_number}
            
            - Centre: {centre}
            - Title: {title}
            - Category: {category}
            - Subcategory: {subcategory}

            We will promptly review your request and assign it to the appropriate technician.

            You will receive further communication once a technician is assigned to your case.

            Thank you for your patience during this process.

            Sincerely,
            
            Edulution
            Technical Support Team
            techsupport@edulution.org
            +260 96 9929538 / +260 96 1255558
        """,
    },
    "Status Change": {
        "subject": "Support Ticket #{ticket_number} Status Change",
        "message": """
            Dear {user_name},

            The status of your Support Ticket #{ticket_number} is now {status}.
            
            - Centre: {centre}
            - Title: {title}
            - Category: {category}
            - Subcategory: {subcategory}

            Thank you for your patience during this process.

            Sincerely,
            
            Edulution
            Technical Support Team
            techsupport@edulution.org
            +260 96 9929538 / +260 96 1255558
        """,
    },
    "Resolution": {
        "subject": "Support Ticket #{ticket_number} Resolved",
        "message": """
            Dear {user_name},

            Your Support Ticket #{ticket_number} has been resolved.
            
            - Centre: {centre}
            - Title: {title}
            - Category: {category}
            - Subcategory: {subcategory}

            Thank you for your patience during this process.

            Sincerely,
            
            Edulution
            Technical Support Team
            techsupport@edulution.org
            +260 96 9929538 / +260 96 1255558
        """,
    },
    "Assignment": {
        "subject": "Support Ticket #{ticket_number} Assigned",
        "message": """
        Dear {user_name},

        Your Support Ticket #{ticket_number} has been assigned to {assigned_to}.
        
        - Centre: {centre}
        - Title: {title}
        - Category: {category}
        - Subcategory: {subcategory}

        You will be notified once it is resolved.

        Sincerely,
        
        Edulution
        Technical Support Team
        techsupport@edulution.org
        +260 96 9929538 / +260 96 1255558
    """,
    },
}

# Definitions for webhook messages
WEBHOOK_MESSAGES = {
    "Ticket Creation": {
        "text": "A Support Ticket has been created at *{centre}*\n"
        "*Title:* {title}\n"
        "*Category:* {category}\n"
        "*Subcategory:* {subcategory}\n"
        "*Priority:* {priority}\n"
        "*Ticket Number:* {ticket_number}\n"
        "*by:* {user}"
    },
    "Status Change": {
        "text": "The status of Support Ticket *#{ticket_number}* has been changed to *{status}*.\n"
        "*Title:* {title}\n"
        "*Centre:* {centre}\n"
        "*by:* {user}"
    },
    "Resolution": {
        "text": "Support Ticket *#{ticket_number}* has been resolved.\n"
        "*Title:* {title}\n"
        "*Centre:* {centre}\n"
        "*by:* {user}"
    },
    "Assignment": {
        "text": 'A Support Ticket *Title:* "{title}" at *{centre}* has been assigned to {assigned_to}.\n'
        "*by:* {user}"
    },
}
