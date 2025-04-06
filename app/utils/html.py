def account_activation_html(recipient: str, activation_link: str) -> str:
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Activate Your Account</title>
      <style>
        body {{
          margin: 0;
          padding: 0;
          background-color: #f4f4f4;
          font-family: Arial, sans-serif;
        }}
        .email-container {{
          max-width: 600px;
          margin: 40px auto;
          background-color: #ffffff;
          padding: 20px 30px;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}
        .email-header {{
          text-align: center;
          padding-bottom: 10px;
        }}
        .email-content {{
          font-size: 16px;
          line-height: 1.6;
          color: #333333;
          text-align: center;
        }}
        .button-wrapper {{
          margin: 30px 0;
          text-align: center;
        }}
        .btn {{
          background-color: #007bff;
          color: #ffffff !important;
          padding: 14px 28px;
          text-decoration: none;
          font-weight: bold;
          border-radius: 5px;
          display: inline-block;
        }}
        .email-footer {{
          font-size: 13px;
          color: #777;
          text-align: center;
          margin-top: 30px;
        }}
      </style>
    </head>
    <body>
      <div class="email-container">
        <div class="email-header">
          <h2>Welcome to NOXUS, {recipient}!</h2>
        </div>
        <div class="email-content">
          <p>Thanks for signing up! Please confirm your email address by clicking the button below.</p>
        </div>
        <div class="button-wrapper">
          <a href="{activation_link}" class="btn">Activate Account</a>
        </div>
        <div class="email-content">
          <p>If you didn’t create an account, you can ignore this email.</p>
        </div>
        <div class="email-footer">
          &copy; 2025 YourApp Inc. All rights reserved.
        </div>
      </div>
    </body>
    </html>
    """

    return html_content
