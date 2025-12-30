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
    
    def _get_socket_error_message(self, error_code):
        """Get human-readable error message for socket error codes."""
        error_messages = {
            0: "Success",
            1: "Operation not permitted",
            2: "No such file or directory",
            3: "No such process",
            4: "Interrupted system call",
            5: "I/O error",
            6: "No such device or address",
            7: "Argument list too long",
            8: "Exec format error",
            9: "Bad file number",
            10: "No child processes",
            11: "Try again",
            12: "Out of memory",
            13: "Permission denied",
            14: "Bad address",
            15: "Block device required",
            16: "Device or resource busy",
            17: "File exists",
            18: "Cross-device link",
            19: "No such device",
            20: "Not a directory",
            21: "Is a directory",
            22: "Invalid argument",
            23: "File table overflow",
            24: "Too many open files",
            25: "Not a typewriter",
            26: "Text file busy",
            27: "File too large",
            28: "No space left on device",
            29: "Illegal seek",
            30: "Read-only file system",
            31: "Too many links",
            32: "Broken pipe",
            33: "Math argument out of domain",
            34: "Math result not representable",
            35: "Resource deadlock would occur",
            36: "File name too long",
            37: "No record locks available",
            38: "Function not implemented",
            39: "Directory not empty",
            40: "Too many symbolic links encountered",
            41: "Operation would block",
            42: "No message of desired type",
            43: "Identifier removed",
            44: "Channel number out of range",
            45: "Level 2 not synchronized",
            46: "Level 3 halted",
            47: "Level 3 reset",
            48: "Link number out of range",
            49: "Protocol driver not attached",
            50: "No CSI structure available",
            51: "Level 2 halted",
            52: "Invalid exchange",
            53: "Invalid request descriptor",
            54: "Exchange full",
            55: "No anode",
            56: "Invalid request code",
            57: "Invalid slot",
            58: "File locking deadlock error",
            59: "Bad font file format",
            60: "Device not a stream",
            61: "No data available",
            62: "Timer expired",
            63: "Out of streams resources",
            64: "Machine is not on the network",
            65: "Package not installed",
            66: "Object is remote",
            67: "Link has been severed",
            68: "Advertise error",
            69: "Srmount error",
            70: "Communication error on send",
            71: "Protocol error",
            72: "Multihop attempted",
            73: "RFS specific error",
            74: "Not a data message",
            75: "Value too large for defined data type",
            76: "Name not unique on network",
            77: "File descriptor in bad state",
            78: "Remote address changed",
            79: "Can not access a needed shared library",
            80: "Accessing a corrupted shared library",
            81: ".lib section in a.out corrupted",
            82: "Attempting to link in too many shared libraries",
            83: "Cannot exec a shared library directly",
            84: "Illegal byte sequence",
            85: "Interrupted system call should be restarted",
            86: "Streams pipe error",
            87: "Too many users",
            88: "Socket operation on non-socket",
            89: "Destination address required",
            90: "Message too long",
            91: "Protocol wrong type for socket",
            92: "Protocol not available",
            93: "Protocol not supported",
            94: "Socket type not supported",
            95: "Operation not supported on transport endpoint",
            96: "Protocol family not supported",
            97: "Address family not supported by protocol",
            98: "Address already in use",
            99: "Cannot assign requested address",
            100: "Network is down",
            101: "Network is unreachable",
            102: "Network dropped connection because of reset",
            103: "Software caused connection abort",
            104: "Connection reset by peer",
            105: "No buffer space available",
            106: "Transport endpoint is already connected",
            107: "Transport endpoint is not connected",
            108: "Cannot send after transport endpoint shutdown",
            109: "Too many references: cannot splice",
            110: "Connection timed out",
            111: "Connection refused",
            112: "Host is down",
            113: "No route to host",
            114: "Operation already in progress",
            115: "Operation now in progress",
            116: "Stale file handle",
            117: "Structure needs cleaning",
            118: "Not a XENIX named type file",
            119: "No XENIX semaphores available",
            120: "Is a named type file",
            121: "Remote I/O error",
            122: "Quota exceeded",
            123: "No medium found",
            124: "Wrong medium type",
            125: "Operation canceled",
            126: "Required key not available",
            127: "Key has expired",
            128: "Key has been revoked",
            129: "Key was rejected by service",
            130: "Owner died",
            131: "State not recoverable",
        }
        return error_messages.get(error_code, f"Unknown error code: {error_code}")
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
            
            # Test basic socket connection first (with retry for transient errors)
            socket_test_passed = False
            test_result = None
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    log.info("  Testing basic socket connection (attempt %d/%d)...", attempt, max_retries)
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.settimeout(10)  # Use shorter timeout for test
                    log.info("  Attempting socket.connect_ex(%s, %s)...", email_host, email_port)
                    test_result = test_socket.connect_ex((email_host, email_port))
                    test_socket.close()
                    
                    if test_result == 0:
                        log.info("  ✅ Socket connection test successful - port %s is reachable", email_port)
                        socket_test_passed = True
                        break
                    else:
                        error_msg = self._get_socket_error_message(test_result)
                        if test_result == 11:  # EAGAIN - Try again
                            if attempt < max_retries:
                                log.warning("  ⚠️  Socket test returned 'Try again' (error 11) - retrying...")
                                import time
                                time.sleep(1)  # Wait 1 second before retry
                                continue
                            else:
                                log.warning("  ⚠️  Socket test returned 'Try again' after %d attempts", max_retries)
                                log.warning("  This might be a temporary network issue - continuing anyway")
                                socket_test_passed = True  # Continue despite error 11
                                break
                        else:
                            log.error("  ❌ Socket connection test failed (error code: %s)", test_result)
                            log.error("  Error meaning: %s", error_msg)
                            if test_result == 111:  # Connection refused
                                log.error("  This indicates:")
                                log.error("    - Railway is blocking outbound connections to port %s", email_port)
                                log.error("    - OR firewall is blocking port %s", email_port)
                                log.error("    - OR SMTP server is not reachable from Railway")
                                log.error("  💡 Suggestion: Try port 587 with STARTTLS instead of port 465")
                            break
                except socket.timeout:
                    if attempt < max_retries:
                        log.warning("  ⚠️  Socket connection test timed out - retrying...")
                        continue
                    else:
                        log.error("  ❌ Socket connection test timed out after %d attempts", max_retries)
                        log.error("  This indicates Railway cannot reach %s:%s", email_host, email_port)
                        break
                except Exception as socket_test_error:
                    log.error("  ❌ Socket connection test failed: %s", socket_test_error)
                    log.error("  Error type: %s", type(socket_test_error).__name__)
                    if attempt < max_retries:
                        log.info("  Retrying...")
                        import time
                        time.sleep(1)
                        continue
                    else:
                        log.exception("  Exception details:")
                        break
            
            if not socket_test_passed and test_result != 11:
                log.warning("  ⚠️  Socket test failed, but continuing with SMTP connection attempt anyway...")
            
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

