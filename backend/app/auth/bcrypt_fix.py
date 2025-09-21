"""
Fix for bcrypt warnings related to __about__ attribute.
This module patches the bcrypt module to suppress the warnings.
"""

import logging
import sys

def patch_bcrypt():
    """
    Apply a patch to the bcrypt module to prevent warnings.
    This adds a dummy __about__ attribute with a __version__ attribute.
    """
    try:
        import bcrypt
        
        # Check if bcrypt already has __about__
        if not hasattr(bcrypt, '__about__'):
            # Create a dummy __about__ module with __version__
            class DummyAbout:
                __version__ = '4.0.1'  # Use a recent version
            
            # Add the dummy __about__ to bcrypt
            bcrypt.__about__ = DummyAbout()
            
            # Suppress the specific warning from passlib
            logging.getLogger('passlib.handlers.bcrypt').setLevel(logging.ERROR)
            
            return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error patching bcrypt: {e}")
        return False
        
    return True
