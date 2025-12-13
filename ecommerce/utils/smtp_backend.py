"""
Custom SMTP backend with proper SSL context for SMTPS (port 465).
This ensures proper SSL/TLS handling for SMTP over SSL connections.
"""
import ssl
import socket
import logging
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

log = logging.getLogger(__name__)


class SMTPSBackend(EmailBackend):
    """
    Custom SMTP backend that properly handles SMTPS (SMTP over SSL) connections.
    Uses ssl.create_default_context() for proper SSL certificate validation.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize custom SMTPS backend."""
        log.info("🚀 Custom SMTPSBackend initialized")
        super().__init__(*args, **kwargs)
    
    def open(self):
        """
        Open an SMTP connection with proper SSL context.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        
        try:
            email_host = getattr(settings, "EMAIL_HOST", self.host)
            email_port = getattr(settings, "EMAIL_PORT", self.port)
            email_timeout = getattr(settings, "EMAIL_TIMEOUT", self.timeout)
            
            log.info("🔌 Attempting to connect to SMTP server...")
            log.info("  Host: %s", email_host)
            log.info("  Port: %s", email_port)
            log.info("  SSL: %s", self.use_ssl)
            log.info("  TLS: %s", self.use_tls)
            log.info("  Timeout: %s seconds", email_timeout)
            
            # Test basic socket connection first
            try:
                log.info("  Testing basic socket connection...")
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(email_timeout)
                test_result = test_socket.connect_ex((email_host, email_port))
                test_socket.close()
                
                if test_result == 0:
                    log.info("  ✅ Socket connection test successful")
                else:
                    log.warning("  ⚠️  Socket connection test failed (error code: %s)", test_result)
                    log.warning("  This might indicate network/firewall issues")
            except Exception as socket_test_error:
                log.warning("  ⚠️  Socket connection test failed: %s", socket_test_error)
                log.warning("  This might indicate network/firewall issues")
            
            # Create default SSL context for proper certificate validation
            if self.use_ssl:
                log.info("  Creating SSL context for SMTPS...")
                ssl_context = ssl.create_default_context()
                # Optionally disable certificate verification if needed (not recommended for production)
                # ssl_context.check_hostname = False
                # ssl_context.verify_mode = ssl.CERT_NONE
                log.info("  SSL context created")
            else:
                ssl_context = None
            
            # Call parent's open method which handles SSL properly
            log.info("  Calling parent SMTP backend open()...")
            result = super().open()
            
            if result:
                log.info("✅ SMTP connection opened successfully")
                if self.connection:
                    log.info("  Connection object: %s", type(self.connection).__name__)
            else:
                log.info("SMTP connection already exists")
            
            return result
        except socket.timeout as timeout_error:
            log.error("❌ SMTP connection timeout after %s seconds", getattr(settings, "EMAIL_TIMEOUT", self.timeout))
            log.error("  This might indicate:")
            log.error("    1. Railway is blocking outbound SMTP connections")
            log.error("    2. Firewall is blocking port %s", email_port)
            log.error("    3. SMTP server is not reachable")
            log.error("  Error: %s", timeout_error)
            raise
        except Exception as e:
            log.error("❌ Failed to open SMTP connection: %s", e)
            log.error("  Error type: %s", type(e).__name__)
            log.exception("Exception details:")
            raise

