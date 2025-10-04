from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        import core.signals
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            import firebase_admin
            from firebase_admin import credentials
            from django.conf import settings
            import os
            
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get Firebase credentials path from settings
                credentials_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
                project_id = getattr(settings, 'FIREBASE_PROJECT_ID', None)
                
                if credentials_path and os.path.exists(credentials_path):
                    # Initialize with service account credentials
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred, {'projectId': project_id})
                    
                    # Set Firebase initialized flag in settings
                    settings.FIREBASE_INITIALIZED = True
                    
                    logger.info("Firebase Admin SDK initialized successfully")
                else:
                    logger.warning(f"Firebase credentials not found at {credentials_path}")
                    settings.FIREBASE_INITIALIZED = False
            else:
                settings.FIREBASE_INITIALIZED = True
                logger.info("Firebase Admin SDK already initialized")
                
        except ImportError:
            logger.warning("Firebase Admin SDK not installed")
            settings.FIREBASE_INITIALIZED = False
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            settings.FIREBASE_INITIALIZED = False