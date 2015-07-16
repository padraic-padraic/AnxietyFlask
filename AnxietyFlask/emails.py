ANXIETY_PLAIN = """
Dear {0},

{1}
{2}
{3}
{4}

Sincerely,

Your Anxiety

P.S You can deactivate your account anytime at {domain}/deactivate?uuid={uid}, or just straight up delete it at {domain}/delete?uuid={uid}
"""

ANXIETY_HTML= """
Dear {0},<br><br>
{1} <br>
{2} <br>
{3} <br>
{4} <br><br>
Sincerely, <br> Your Anxiety <br>
<br>
P.S, you can <a href="{domain}/deactivate?uuid={uid}">deactivate</a> your account anytime, or just<a href="{domain}/delete?uuid={uid}">delete</a> it, by clicking either of those.
"""

ACTIVATION_TEMPLATE = """
Dear {0},

You've asked us to fill up an Anxiety Flask for you.

To confirm that, click this link:
{domain}/activate?uuid={uid}

Don't worry. If it gets overwhelming, each email will have a link to deactivate or delete your account in one click. Or, you can do it any time at
{domain}/deactivate
{domain}/delete

Sincerely,
Your Anxiety
"""

ACTIVATION_HTML = """
Dear {0}, <br>
You've asked us to fill up an Anxiety Flask for you. <br>
To confirm that, click <a href="{domain}/activate?uuid={uid}"> here</a>. <br>
Don't worry, if it gets overwhelming you can always <a href="{domain}/deactivate>deactivate</a> or <a href="{domain}/delete">delete</a> your account.<br>
Sincerely, <br> Your Anxiety
"""

ADMIN_PLAIN = """
Dear{0}, 

The following emails failed to send. You can review each one below:

{emails}

Sincerely, 
The Anxiety Flask
"""

ADMIN_HTML = """
Dear{0},<br> 
The following emails failed to send. You can review each one below:<br>
{emails}
<br>
Sincerely,<br> 
The Anxiety Flask
"""
