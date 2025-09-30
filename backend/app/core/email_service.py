"""
Email Service for Cassava AI Support Orchestrator
Handles SMTP sending and IMAP polling for email communications
"""

import smtplib
import imaplib
import email
import os
import time
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.agents.master_orchestrator import MasterOrchestrator

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # SMTP Configuration
        self.smtp_host = os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # IMAP Configuration  
        self.imap_host = os.getenv('EMAIL_IMAP_HOST', 'imap.gmail.com')
        self.imap_port = int(os.getenv('EMAIL_IMAP_PORT', '993'))
        
        # Email polling settings
        self.polling_interval = 30  # seconds
        self.last_check = datetime.now() - timedelta(hours=1)
        
        # Initialize orchestrator
        self.orchestrator = MasterOrchestrator()
        
        logger.info(f"Email service initialized with SMTP: {self.smtp_host}:{self.smtp_port}")

    async def send_email(self, to_email: str, subject: str, content: str, in_reply_to: str = None) -> bool:
        """
        Send an email response using SMTP
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add In-Reply-To header for threading
            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
                msg['References'] = in_reply_to
            
            # Add Cassava branding to email
            email_body = f"""
{content}

---
Best regards,
Cassava Network Support Team

This is an automated response from Cassava AI Support. 
For urgent matters, please contact us directly.
            """
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_username, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def fetch_new_emails(self) -> List[Dict]:
        """
        Fetch new emails from IMAP server since last check
        """
        new_emails = []
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_username, self.email_password)
            mail.select('INBOX')
            
            # Search for emails since last check
            search_date = self.last_check.strftime('%d-%b-%Y')
            search_criteria = f'(SINCE "{search_date}" UNSEEN)'
            
            result, message_ids = mail.search(None, search_criteria)
            
            if result == 'OK' and message_ids[0]:
                for msg_id in message_ids[0].split():
                    try:
                        # Fetch email
                        result, msg_data = mail.fetch(msg_id, '(RFC822)')
                        
                        if result == 'OK':
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Extract email details
                            from_email = email_message['From']
                            subject = email_message['Subject']
                            message_id = email_message['Message-ID']
                            
                            # Get email content
                            content = self._extract_email_content(email_message)
                            
                            if content and from_email:
                                new_emails.append({
                                    'from': from_email,
                                    'subject': subject,
                                    'content': content,
                                    'message_id': message_id,
                                    'received_at': datetime.now().isoformat()
                                })
                                
                                logger.info(f"Fetched email from {from_email}: {subject}")
                                
                    except Exception as e:
                        logger.error(f"Error processing email {msg_id}: {e}")
                        continue
            
            mail.close()
            mail.logout()
            
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
        
        return new_emails

    def _extract_email_content(self, email_message) -> str:
        """
        Extract plain text content from email message
        """
        content = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            content = payload.decode('utf-8', errors='ignore')
                            break
            else:
                if email_message.get_content_type() == "text/plain":
                    payload = email_message.get_payload(decode=True)
                    if payload:
                        content = payload.decode('utf-8', errors='ignore')
        
        except Exception as e:
            logger.error(f"Error extracting email content: {e}")
        
        return content.strip()

    async def process_email(self, email_data: Dict) -> Dict:
        """
        Process incoming email through the orchestrator
        """
        try:
            # Prepare message for orchestrator
            message = {
                "content": email_data['content'],
                "channel": "email",
                "customer_email": email_data['from'],
                "subject": email_data['subject'],
                "message_id": email_data['message_id']
            }
            
            # Process through orchestrator
            result = await self.orchestrator.process_message(message)
            
            # Send response if we have one
            if result and result.get('response'):
                # Extract email address from "Name <email@domain.com>" format
                from_email = email_data['from']
                if '<' in from_email and '>' in from_email:
                    from_email = from_email.split('<')[1].split('>')[0].strip()
                
                # Create reply subject
                subject = email_data['subject']
                if not subject.startswith('Re:'):
                    subject = f"Re: {subject}"
                
                # Send response
                await self.send_email(
                    to_email=from_email,
                    subject=subject,
                    content=result['response'],
                    in_reply_to=email_data['message_id']
                )
                
                logger.info(f"Processed and responded to email from {from_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return {"error": str(e)}

    async def start_email_polling(self):
        """
        Start continuous email polling in background
        """
        logger.info("Starting email polling service...")
        
        while True:
            try:
                # Fetch new emails
                new_emails = self.fetch_new_emails()
                
                # Process each new email
                for email_data in new_emails:
                    await self.process_email(email_data)
                
                # Wait before next poll
                await asyncio.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error(f"Error in email polling loop: {e}")
                await asyncio.sleep(self.polling_interval)

    def test_connection(self) -> Dict:
        """
        Test both SMTP and IMAP connections
        """
        results = {
            "smtp": False,
            "imap": False,
            "errors": []
        }
        
        # Test SMTP
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.quit()
            results["smtp"] = True
            logger.info("SMTP connection successful")
        except Exception as e:
            results["errors"].append(f"SMTP error: {e}")
            logger.error(f"SMTP connection failed: {e}")
        
        # Test IMAP
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_username, self.email_password)
            mail.close()
            mail.logout()
            results["imap"] = True
            logger.info("IMAP connection successful")
        except Exception as e:
            results["errors"].append(f"IMAP error: {e}")
            logger.error(f"IMAP connection failed: {e}")
        
        return results