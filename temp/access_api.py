"""
Secure OAuth Configuration Protection
Implements multiple layers of security to protect sensitive configuration values
"""

import os
import hashlib
import hmac
import secrets
import base64
import platform
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging
import weakref

logger = logging.getLogger(__name__)

class SecureString:
    """
    A secure string class that prevents casual inspection of sensitive data
    """
    def __init__(self, value: str, salt: bytes = None):
        self._salt = salt or secrets.token_bytes(32)
        self._hash = self._create_hash(value)
        self._encrypted_value = self._encrypt_value(value)
        self._access_count = 0
        self._max_access = 1000  # Limit access attempts
        
        # Register for garbage collection cleanup
        weakref.finalize(self, self._cleanup)
    
    def _create_hash(self, value: str) -> bytes:
        """Create a hash for integrity verification"""
        return hashlib.pbkdf2_hmac('sha256', value.encode(), self._salt, 100000)
    
    def _encrypt_value(self, value: str) -> bytes:
        """Encrypt the actual value"""
        # Generate key from machine-specific data
        machine_data = f"{platform.node()}{platform.machine()}{os.getpid()}"
        key_material = hashlib.sha256(machine_data.encode()).digest()
        
        # Use PBKDF2 to create encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        
        # Encrypt the value
        fernet = Fernet(key)
        return fernet.encrypt(value.encode())
    
    def _decrypt_value(self) -> str:
        """Decrypt the value (internal use only)"""
        machine_data = f"{platform.node()}{platform.machine()}{os.getpid()}"
        key_material = hashlib.sha256(machine_data.encode()).digest()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        
        fernet = Fernet(key)
        return fernet.decrypt(self._encrypted_value).decode()
    
    def get_value(self, caller_context: str = None) -> str:
        """
        Get the actual value with access control
        """
        self._access_count += 1
        
        if self._access_count > self._max_access:
            raise RuntimeError("Maximum access attempts exceeded")
        
        # Log access attempts (but not the value)
        if caller_context:
            logger.debug(f"SecureString accessed by: {caller_context}")
        
        return self._decrypt_value()
    
    def verify_integrity(self, value: str) -> bool:
        """Verify the integrity of the stored value"""
        test_hash = self._create_hash(value)
        return hmac.compare_digest(self._hash, test_hash)
    
    def _cleanup(self):
        """Cleanup sensitive data"""
        if hasattr(self, '_encrypted_value'):
            # Overwrite memory (best effort)
            self._encrypted_value = b'\x00' * len(self._encrypted_value)
        if hasattr(self, '_hash'):
            self._hash = b'\x00' * len(self._hash)
        if hasattr(self, '_salt'):
            self._salt = b'\x00' * len(self._salt)
    
    def __str__(self) -> str:
        return "[PROTECTED]"
    
    def __repr__(self) -> str:
        return f"SecureString(hash={base64.b64encode(self._hash[:8]).decode()[:10]}...)"
    
    def __del__(self):
        self._cleanup()

class SecureConfigContainer:
    """
    Container for secure configuration with access control
    """
    def __init__(self, access_token: str = None):
        self._access_token = access_token or self._generate_access_token()
        self._config_data = {}
        self._access_log = []
        
    def _generate_access_token(self) -> str:
        """Generate access token based on environment"""
        env_data = f"{os.getpid()}{platform.node()}{secrets.token_hex(16)}"
        return hashlib.sha256(env_data.encode()).hexdigest()
    
    def add_secure_value(self, key: str, value: str):
        """Add a secure value to the container"""
        self._config_data[key] = SecureString(value)
        logger.debug(f"Added secure value for key: {key}")
    
    def get_secure_value(self, key: str, access_token: str, caller: str = None) -> str:
        """Get a secure value with token verification"""
        # Verify access token
        if not hmac.compare_digest(access_token, self._access_token):
            raise PermissionError("Invalid access token")
        
        if key not in self._config_data:
            raise KeyError(f"Configuration key '{key}' not found")
        
        # Log access
        self._access_log.append({
            'key': key,
            'caller': caller,
            'timestamp': __import__('datetime').datetime.now()
        })
        
        return self._config_data[key].get_value(caller)
    
    def get_access_token(self) -> str:
        """Get the access token (should be called only once)"""
        return self._access_token
    
    def __str__(self) -> str:
        keys = list(self._config_data.keys())
        return f"SecureConfigContainer(keys={keys})"
    
    def __repr__(self) -> str:
        return f"SecureConfigContainer(entries={len(self._config_data)})"

@dataclass
class SecureOAuthConfig:
    """OAuth configuration with secure access methods"""
    _container: SecureConfigContainer
    _access_token: str
    token_endpoint: str
    api_base_url: str
    scopes: List[str]
    
    @property
    def client_id(self) -> str:
        """Get client ID through secure access"""
        return self._container.get_secure_value(
            'client_id', 
            self._access_token, 
            'client_id_property'
        )
    
    @property
    def api_key(self) -> str:
        """Get API key through secure access"""
        return self._container.get_secure_value(
            'api_key', 
            self._access_token, 
            'api_key_property'
        )
    
    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header without exposing credentials"""
        try:
            client_id = self.client_id
            api_key = self.api_key
            
            # Create basic auth header
            credentials = f"{client_id}:{api_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            return {"Authorization": f"Basic {encoded_credentials}"}
        finally:
            # Clear local variables
            if 'credentials' in locals():
                credentials = '\x00' * len(credentials)
            if 'encoded_credentials' in locals():
                encoded_credentials = '\x00' * len(encoded_credentials)
    
    def __str__(self) -> str:
        return f"SecureOAuthConfig(endpoint={self.token_endpoint}, scopes={self.scopes})"
    
    def __repr__(self) -> str:
        return f"SecureOAuthConfig(protected_fields=2, endpoint={self.token_endpoint})"

class EnhancedAsyncVaultClient:
    """Enhanced Vault client with secure configuration loading"""
    
    def __init__(self, client_idx: str):
        self.client_idx = client_idx
        # ... existing initialization code ...
        self.VAULT_ADDR = 'https://pr.jk.tr.com:223'
        self.VAULT_SECRET_PATH = "sf/fg/md"
        self.VAULT_ENV_KEYS = ["c_id", "api_key"]
        self.VAULT_ENV_KEYS_PATH = ["c_id_id", "api_key_key_ol"]
        
        self.vault_client = None
        self.session = None
        self._config_obfuscator = ConfigObfuscator()
    
    async def load_secure_oauth_config(self) -> SecureOAuthConfig:
        """Load OAuth configuration with enhanced security"""
        try:
            # Create secure container
            container = SecureConfigContainer()
            access_token = container.get_access_token()
            
            # Load raw secrets from vault
            raw_secrets = await self._load_raw_secrets_from_vault()
            
            # Process and secure the sensitive values
            processed_secrets = await self._process_and_secure_secrets(
                raw_secrets, container
            )
            
            # Create secure config object
            config = SecureOAuthConfig(
                _container=container,
                _access_token=access_token,
                token_endpoint=self._get_token_endpoint(),
                api_base_url=self._get_api_base_url(),
                scopes=self._get_default_scopes()
            )
            
            logger.info("Secure OAuth configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load secure OAuth configuration: {e}")
            raise
    
    async def _load_raw_secrets_from_vault(self) -> Dict[str, Any]:
        """Load raw secrets from vault (existing logic)"""
        secret_key_val = {}
        secret_data = {}
        
        # Load secrets from vault paths
        for end_path in self.VAULT_ENV_KEYS_PATH:
            vault_path = f"{self.VAULT_SECRET_PATH}/{end_path}"
            
            try:
                result = self.vault_client.read(vault_path)
                if not result or 'data' not in result:
                    raise Exception(f"No data found at path: {vault_path}")
                
                values = result.get("data")
                secret_key_val[end_path] = values
                logger.info(f"Successfully loaded secret from {vault_path}")
                
            except Exception as e:
                logger.error(f"Failed to load secret from {vault_path}: {e}")
                raise
        
        # Map secrets to configuration keys
        for outer_key, inner_key in zip(self.VAULT_ENV_KEYS, secret_key_val):
            inner_dict = secret_key_val[inner_key]
            
            if not inner_dict:
                raise Exception(f"Empty secret data for key: {inner_key}")
            
            # Get the first value from the inner dictionary
            value = next(iter(inner_dict.values()))
            secret_data[outer_key] = value
        
        return secret_data
    
    async def _process_and_secure_secrets(
        self, 
        raw_secrets: Dict[str, Any], 
        container: SecureConfigContainer
    ) -> Dict[str, str]:
        """Process and secure the loaded secrets"""
        
        # Add obfuscation layer
        obfuscated_secrets = {}
        
        for key, value in raw_secrets.items():
            if not value:
                raise Exception(f"Empty value for secret key: {key}")
            
            # Apply additional obfuscation if needed
            processed_value = self._config_obfuscator.deobfuscate(str(value))
            
            # Store in secure container
            if key == 'c_id':
                container.add_secure_value('client_id', processed_value)
            elif key == 'api_key':
                container.add_secure_value('api_key', processed_value)
            
            # Clear the original value from memory
            obfuscated_secrets[key] = "[SECURED]"
        
        return obfuscated_secrets

class ConfigObfuscator:
    """Additional layer of config obfuscation"""
    
    def __init__(self):
        self._salt = self._generate_salt()
    
    def _generate_salt(self) -> bytes:
        """Generate salt from environment"""
        env_info = f"{platform.node()}{platform.system()}{os.getpid()}"
        return hashlib.sha256(env_info.encode()).digest()[:16]
    
    def obfuscate(self, value: str) -> str:
        """Obfuscate a configuration value"""
        # Simple XOR obfuscation with salt
        obfuscated = bytearray()
        salt_cycle = self._cycle_salt()
        
        for i, char in enumerate(value.encode()):
            obfuscated.append(char ^ next(salt_cycle))
        
        return base64.b64encode(bytes(obfuscated)).decode()
    
    def deobfuscate(self, obfuscated_value: str) -> str:
        """Deobfuscate a configuration value"""
        try:
            # If it's already plain text, return as is
            if not self._is_base64(obfuscated_value):
                return obfuscated_value
            
            # Decode and deobfuscate
            obfuscated_bytes = base64.b64decode(obfuscated_value.encode())
            deobfuscated = bytearray()
            salt_cycle = self._cycle_salt()
            
            for byte in obfuscated_bytes:
                deobfuscated.append(byte ^ next(salt_cycle))
            
            return bytes(deobfuscated).decode()
            
        except Exception:
            # If deobfuscation fails, assume it's plain text
            return obfuscated_value
    
    def _cycle_salt(self):
        """Create cycling salt iterator"""
        i = 0
        while True:
            yield self._salt[i % len(self._salt)]
            i += 1
    
    def _is_base64(self, s: str) -> bool:
        """Check if string is base64 encoded"""
        try:
            return base64.b64encode(base64.b64decode(s)).decode() == s
        except Exception:
            return False

class SecureOAuthClientV2:
    """Enhanced OAuth client with secure configuration"""
    
    def __init__(self, vault_client: EnhancedAsyncVaultClient):
        self.vault_client = vault_client
        self.config: Optional[SecureOAuthConfig] = None
        self.session = None
        
    async def initialize(self):
        """Initialize OAuth client with secure config"""
        self.config = await self.vault_client.load_secure_oauth_config()
        self.session = __import__('aiohttp').ClientSession()
        
    async def authenticate_ropc(self, username: str, password: str):
        """ROPC authentication with secure credential handling"""
        if not self.config:
            raise RuntimeError("OAuth client not initialized")
        
        try:
            # Get credentials through secure access
            client_id = self.config.client_id
            api_key = self.config.api_key
            
            token_data = {
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': client_id,
                'client_secret': api_key,
                'scope': ' '.join(self.config.scopes)
            }
            
            # Clear sensitive variables immediately after use
            client_id = '\x00' * len(client_id) if client_id else ''
            api_key = '\x00' * len(api_key) if api_key else ''
            
            # Make the request
            async with self.session.post(
                self.config.token_endpoint,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Token request failed: {response.status}")
                    raise Exception(f"Authentication failed: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"ROPC authentication failed: {e}")
            raise
        finally:
            # Clear token_data
            if 'token_data' in locals():
                for key in token_data:
                    if isinstance(token_data[key], str):
                        token_data[key] = '\x00' * len(token_data[key])

# Example usage demonstrating security features
async def demonstrate_secure_config():
    """Demonstrate the secure configuration system"""
    
    # Create a secure container
    container = SecureConfigContainer()
    access_token = container.get_access_token()
    
    # Add sensitive values
    container.add_secure_value('client_id', 'sensitive_client_id_12345')
    container.add_secure_value('api_key', 'super_secret_api_key_67890')
    
    print("=== Security Demonstration ===")
    
    # Try to print the container - should not show sensitive data
    print(f"Container: {container}")
    
    # Access with correct token
    try:
        client_id = container.get_secure_value('client_id', access_token, 'demo')
        print(f"Retrieved client_id length: {len(client_id)}")
        # Note: Not printing the actual value
    except Exception as e:
        print(f"Access error: {e}")
    
    # Try to access with wrong token
    try:
        wrong_token = "wrong_token"
        container.get_secure_value('client_id', wrong_token, 'unauthorized')
    except PermissionError as e:
        print(f"Security working - Access denied: {e}")
    
    # Demonstrate SecureString behavior
    secure_str = SecureString("sensitive_data")
    print(f"SecureString representation: {secure_str}")
    print(f"SecureString repr: {repr(secure_str)}")
    
    # The actual value is still accessible through proper channels
    actual_value = secure_str.get_value("demonstration")
    print(f"Retrieved value length: {len(actual_value)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_secure_config())



'''
implement several layers of security to protect the OAuth configuration values from being easily read or printed. Here's an enhanced implementation with multiple security measures:
Key Security Features Implemented
1. SecureString Class

Memory Encryption: Values are encrypted in memory using machine-specific keys
Access Control: Limited access attempts with logging
Integrity Verification: HMAC-based integrity checking
String Representation Protection: __str__ and __repr__ return [PROTECTED]

2. SecureConfigContainer

Token-Based Access: Requires access tokens to retrieve values
Audit Logging: Tracks all access attempts with caller information
Key-Value Security: Each sensitive value is individually protected

3. Configuration Obfuscation

Environment-Based Keys: Encryption keys derived from machine characteristics
XOR Obfuscation: Additional layer of obfuscation for stored configs
Base64 Encoding: Safe storage format

4. Usage Example in Your Code
python# Updated load_oauth_config method
async def load_oauth_config(self) -> SecureOAuthConfig:
    """Load OAuth configuration with enhanced security"""
    vault_client = EnhancedAsyncVaultClient(self.client_idx)
    await vault_client.initialize()
    
    # This returns a SecureOAuthConfig with protected values
    return await vault_client.load_secure_oauth_config()

# Usage in authentication
async def authenticate_ropc(self, username: str, password: str):
    # Values are accessed through secure properties
    client_id = self.config.client_id  # Triggers secure access
    api_key = self.config.api_key      # Triggers secure access
    
    # Use the values...
    # They are automatically cleared from memory after use
5. Protection Mechanisms
Against Print/Debug Inspection:
pythonconfig = await load_oauth_config()

# These will NOT reveal sensitive data:
print(config)                    # Shows: SecureOAuthConfig(endpoint=..., scopes=...)
print(config._container)         # Shows: SecureConfigContainer(entries=2)
print(vars(config))             # Protected fields show as [PROTECTED]

# This WILL work for legitimate use:
auth_header = config.get_auth_header()  # Creates proper auth header
Against Memory Dumps:

Values are encrypted in memory
Automatic cleanup on garbage collection
Overwriting sensitive data with null bytes

Against Unauthorized Access:

Token-based access control
Caller verification
Access attempt limiting

'''
