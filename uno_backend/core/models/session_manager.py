from core.config import active_sessions

class SessionManager:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

    def is_legit(self) -> bool:
        """
        Check if the session is valid and exists in the active sessions.
        
        Returns:
            bool: True if the session is legitimate, False otherwise.
        """
        return self.session_id in active_sessions

    def remove(self) -> None:
        """
        Remove the session from active sessions.
        """
        if self.is_legit():
            del active_sessions[self.session_id]

    def join_game(self) -> None:
        """
        Mark the session as part of a game.
        """
        if self.is_legit():
            active_sessions[self.session_id]['in_game'] = True

    def add(self, **kwargs) -> None:
        """
        Add or update the session details.
        
        Args:
            **kwargs: Key-value pairs of session details to add or update.
        """
        active_sessions[self.session_id] = {}
        for key, value in kwargs.items():
            active_sessions[self.session_id][key] = value

    def get_name(self) -> str:
        """
        Retrieve the name of the session.
        
        Returns:
            str: The name associated with the session.
        """
        return active_sessions[self.session_id].get('name', 'Unknown')
    
    def get_pfp(self) -> str:
        """
        Retrieve the profile picture URL of the session.
        
        Returns:
            str: The profile picture URL associated with the session.
        """
        return active_sessions[self.session_id].get('pfp', 'default_pfp.png')

    def in_game(self) -> bool:
        """
        Check if the session is currently in a game.
        
        Returns:
            bool: True if the session is in a game, False otherwise.
        """
        return active_sessions[self.session_id].get('in_game', False)
