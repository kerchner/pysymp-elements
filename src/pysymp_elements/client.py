"""API client for Symplectic Elements."""

import requests
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlencode, urlparse, parse_qs
from .parsers import parse_response
from .models import APIResponse, APIObject, Relationship


class APIClient:
    """Client for interacting with the Symplectic Elements API."""
    
    ITEMS_PER_PAGE = 25  # Number of results per page from the API
    
    def __init__(self, base_url: str, username: str, password: str, version: str = 'v6.13', timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the Elements instance (e.g., 'https://your-instance.symplectic.co.uk/')
            username: Username for authentication
            password: Password for authentication
            version: API version (default: v6.13)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/secure-api/{version}/"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        })
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make a GET request to the API."""
        url = urljoin(self.api_base, endpoint)
        if params:
            url += '?' + urlencode(params)
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return parse_response(response.text)
    
    def _post(self, endpoint: str, data: str, params: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make a POST request to the API."""
        url = urljoin(self.api_base, endpoint)
        if params:
            url += '?' + urlencode(params)
        
        response = self.session.post(url, data=data, headers={'Content-Type': 'text/xml'}, timeout=self.timeout)
        response.raise_for_status()
        
        return parse_response(response.text)
    
    def get_object(self, category: str, id: int, detail: str = 'full') -> APIObject:
        """
        Get a single object by category and ID.
        
        Args:
            category: Object category (e.g., 'publications', 'users', 'groups')
            id: Object ID
            detail: Detail level ('ref', 'full', 'single-record')
        
        Returns:
            The requested object
        """
        endpoint = f"{category}/{id}"
        params = {'detail': detail}
        response = self._get(endpoint, params)
        return response.result
    
    def get_objects(self, category: str, detail: str = 'ref', limit: Optional[int] = None, **filters) -> List[APIObject]:
        """
        Get a list of objects by category, handling pagination automatically.
        
        Args:
            category: Object category
            detail: Detail level
            limit: Maximum number of results to fetch (None for all)
            **filters: Additional query parameters
        
        Returns:
            List of objects
        """
        endpoint = category
        params = {'detail': detail}
        params.update(filters)
        
        all_results = []
        
        while True:
            response = self._get(endpoint, params)
            all_results.extend(response.result_list)
            
            # Stop if we've reached the limit
            if limit is not None and len(all_results) >= limit:
                all_results = all_results[:limit]
                break
            
            # Check for next page
            if response.pagination:
                next_page = None
                for page in response.pagination.page:
                    if page.position == 'next':
                        next_page = page
                        break
                
                if next_page:
                    # Parse the href to get updated params
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(next_page.href)
                    query_params = parse_qs(parsed.query)
                    # Update params with the new after-id, etc.
                    params.update({k: v[0] if v else '' for k, v in query_params.items()})
                else:
                    break
            else:
                break
        
        return all_results
    
    def get_relationship(self, id: int, detail: str = 'full') -> Relationship:
        """
        Get a relationship by ID.
        
        Args:
            id: Relationship ID
            detail: Detail level
        
        Returns:
            The relationship
        """
        endpoint = f"relationships/{id}"
        params = {'detail': detail}
        response = self._get(endpoint, params)
        return response.result
    
    def get_relationships(self, **filters) -> List[Relationship]:
        """
        Get a list of relationships.
        
        Args:
            **filters: Query parameters
        
        Returns:
            List of relationships
        """
        endpoint = "relationships"
        response = self._get(endpoint, filters)
        return response.result_list
    
    def import_relationship(self, from_object: str, to_object: str, type_name: str, validate: bool = False) -> APIResponse:
        """
        Import (create or update) a relationship.
        
        Args:
            from_object: From object identifier (e.g., 'publication(123)')
            to_object: To object identifier (e.g., 'user(456)')
            type_name: Relationship type name
            validate: Whether to validate only
        
        Returns:
            API response
        """
        xml_data = f"""<import-relationship xmlns="http://www.symplectic.co.uk/publications/api">
    <from-object>{from_object}</from-object>
    <to-object>{to_object}</to-object>
    <type-name>{type_name}</type-name>
</import-relationship>"""
        
        params = {'validate': str(validate).lower()}
        return self._post("relationships", xml_data, params)
    
    def get_publications(self,
                         detail: str = 'ref', # other values are 'full' and 'single-record'
                         limit: Optional[int] = None,
                         # types: str = 'book,chapter,journal-article', # See /publication/types endpoint for valid values
                         **filters) -> List[APIObject]:
        """Get publications."""
        return self.get_objects('publications', detail, limit, **filters)
    
    def get_users(self, detail: str = 'ref', limit: Optional[int] = None, **filters) -> List[APIObject]:
        """Get users."""
        return self.get_objects('users', detail, limit, **filters)
    
    def get_groups(self, detail: str = 'ref', limit: Optional[int] = None, **filters) -> List[APIObject]:
        """Get groups."""
        return self.get_objects('groups', detail, limit, **filters)
    
    def get_journals(self, detail: str = 'ref', limit: Optional[int] = None, **filters) -> List[APIObject]:
        """Get journals."""
        return self.get_objects('journals', detail, limit, **filters)