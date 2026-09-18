# import os
# import smtplib
# from email.mime.text import MIMEText


# # =========================
# # EMAIL NOTIFICATION
# # =========================
# def send_order_email(customer_email, customer_name, product_name, quantity):

#     sender_email = os.getenv("EMAIL_USER")
#     sender_password = os.getenv("EMAIL_PASSWORD")

#     message = f"""
# Hi {customer_name},

# Your order has been placed successfully 🎉

# Product: {product_name}
# Quantity: {quantity}

# Thank you for shopping with us!
# """

#     msg = MIMEText(message)
#     msg["Subject"] = "Order Confirmation"
#     msg["From"] = sender_email
#     msg["To"] = customer_email

#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()
#     server.login(sender_email, sender_password)
#     server.send_message(msg)
#     server.quit()


# # =========================
# # WHATSAPP (SIMULATION / TWILIO READY)
# # =========================
# def send_whatsapp_message(phone, product_name):

#     # For now just simulate (no real API needed yet)
#     print(f"[WHATSAPP] Message sent to {phone}: Order confirmed for {product_name}")

#     # Later you can plug Twilio here
#     return True