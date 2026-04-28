"""Data models for Symplectic Elements API objects."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class APIObject:
    """Base class for API objects."""
    category: str
    id: int
    href: str
    type: str
    type_id: int
    type_display_name: str
    privacy_level: str
    last_modified_when: str
    created_when: str
    last_affected_when: Optional[str] = None
    ever_approved: Optional[bool] = None
    allow_type_switching: Optional[bool] = None
    relationships_href: Optional[str] = None


@dataclass_json
@dataclass
class Field:
    """Represents a field in a record."""
    name: str
    type: str
    display_name: str
    text: Optional[str] = None
    items: List[str] = field(default_factory=list)
    people: List['Person'] = field(default_factory=list)
    links: List['Link'] = field(default_factory=list)
    date: Optional['Date'] = None
    pagination: Optional['Pagination'] = None
    keywords: List['Keyword'] = field(default_factory=list)
    addresses: List['Address'] = field(default_factory=list)
    identifiers: List['Identifier'] = field(default_factory=list)
    academic_appointments: List['AcademicAppointment'] = field(default_factory=list)
    degrees: List['Degree'] = field(default_factory=list)
    email_addresses: List['EmailAddress'] = field(default_factory=list)
    phone_numbers: List['PhoneNumber'] = field(default_factory=list)
    web_addresses: List['WebAddress'] = field(default_factory=list)
    non_academic_employments: List['NonAcademicEmployment'] = field(default_factory=list)
    decimal: Optional[float] = None
    boolean: Optional[bool] = None


@dataclass_json
@dataclass
class Person:
    """Represents a person in a field."""
    last_name: str
    initials: str
    first_names: str
    separate_first_names: List[str] = field(default_factory=list)
    addresses: List['Address'] = field(default_factory=list)
    links: List['Link'] = field(default_factory=list)
    identifiers: List['Identifier'] = field(default_factory=list)


@dataclass_json
@dataclass
class Link:
    """Represents a link."""
    type: str
    href: str


@dataclass_json
@dataclass
class Date:
    """Represents a date."""
    year: int
    month: Optional[int] = None
    day: Optional[int] = None

    def to_ymd_string(self) -> str:
        if self.month is None:
            return f"{self.year}"
        if self.day is None:
            return f"{self.year}-{self.month:02d}"
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

@dataclass_json
@dataclass
class Pagination:
    """Represents pagination info."""
    begin_page: Optional[Union[int, str]] = None
    end_page: Optional[Union[int, str]] = None


@dataclass_json
@dataclass
class Keyword:
    """Represents a keyword."""
    scheme: str
    text: str
    origin: Optional[str] = None
    source: Optional[str] = None


@dataclass_json
@dataclass
class Address:
    """Represents an address."""
    iso_country_code: str
    line: List[str] = field(default_factory=list)
    grid: Optional['Grid'] = None


@dataclass_json
@dataclass
class Grid:
    """Represents a GRID identifier."""
    id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass_json
@dataclass
class Identifier:
    """Represents an identifier."""
    scheme: str
    text: str


@dataclass_json
@dataclass
class AcademicAppointment:
    """Represents an academic appointment."""
    institution: 'Institution'
    position: str
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None


@dataclass_json
@dataclass
class Institution:
    """Represents an institution."""
    iso_country_code: str
    line: List[str] = field(default_factory=list)


@dataclass_json
@dataclass
class Degree:
    """Represents a degree."""
    name: str
    institution: Institution
    field_of_study: str
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None


@dataclass_json
@dataclass
class EmailAddress:
    """Represents an email address."""
    address: str
    type: str


@dataclass_json
@dataclass
class PhoneNumber:
    """Represents a phone number."""
    number: str
    type: str


@dataclass_json
@dataclass
class WebAddress:
    """Represents a web address."""
    url: str
    label: str
    type: Optional[str] = None


@dataclass_json
@dataclass
class NonAcademicEmployment:
    """Represents non-academic employment."""
    employer: 'Employer'
    position: str
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None


@dataclass_json
@dataclass
class Employer:
    """Represents an employer."""
    line: List[str] = field(default_factory=list)


@dataclass_json
@dataclass
class Record:
    """Represents a record."""
    format: str = ""
    id: Optional[int] = None
    source_id: int = 0
    source_name: str = ""
    source_display_name: str = ""
    id_at_source: str = ""
    citation_count: Optional[int] = None
    native: List[Field] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)


@dataclass_json
@dataclass
class Publication:
    """Represents a publication."""
    # Common fields
    category: str = "publication"
    id: int = 0
    href: str = ""
    type: str = ""
    type_id: int = 0
    type_display_name: str = ""
    privacy_level: str = ""
    last_modified_when: str = ""
    created_when: str = ""
    last_affected_when: Optional[str] = None
    ever_approved: Optional[bool] = None
    allow_type_switching: Optional[bool] = None
    relationships_href: Optional[str] = None
    # Publication specific
    reporting_date_1: Optional[str] = None
    open_access_status: Optional[str] = None
    online_publication_date: Optional['Date'] = None
    publication_date: Optional['Date'] = None
    records: List[Record] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)
    authors: List[Person] = field(default_factory=list)
    fields_dict: Dict[str, str] = field(default_factory=dict)
    all_labels: List[Keyword] = field(default_factory=list)
    journal: Optional['Journal'] = None


@dataclass_json
@dataclass
class Journal:
    """Represents a journal."""
    issn: str
    title: str
    href: str
    records: List[Record] = field(default_factory=list)


@dataclass_json
@dataclass
class User:
    """Represents a user."""
    # Common fields
    category: str = "user"
    id: int = 0
    href: str = ""
    type: str = "person"
    type_id: int = 1
    type_display_name: str = "Person"
    privacy_level: str = ""
    last_modified_when: str = ""
    created_when: str = ""
    last_affected_when: Optional[str] = None
    ever_approved: Optional[bool] = None
    allow_type_switching: Optional[bool] = None
    relationships_href: Optional[str] = None
    # User specific
    proprietary_id: str = ""
    authenticating_authority: str = ""
    username: str = ""
    title: Optional[str] = None
    initials: str = ""
    last_name: str = ""
    first_name: str = ""
    user_preferred_pronouns: Optional[str] = None
    email_address: str = ""
    primary_group_descriptor: str = ""
    position: str = ""
    department: str = ""
    institutional_email_is_public: bool = False
    claimed: bool = False
    organisation_defined_data: Dict[str, str] = field(default_factory=dict)
    user_search_settings: Optional['UserSearchSettings'] = None
    records: List[Record] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)
    all_labels: List[Keyword] = field(default_factory=list)
    user_identifier_associations: List['UserIdentifierAssociation'] = field(default_factory=list)
    photo_href: Optional[str] = None
    is_current_staff: bool = False
    is_academic: bool = False
    is_student: bool = False
    is_login_allowed: bool = False


@dataclass_json
@dataclass
class UserSearchSettings:
    """Represents user search settings."""
    default: 'SearchSettings'


@dataclass_json
@dataclass
class SearchSettings:
    """Represents search settings."""
    affiliation: str
    name: str


@dataclass_json
@dataclass
class UserIdentifierAssociation:
    """Represents a user identifier association."""
    scheme: str
    status: str
    decision: str


@dataclass_json
@dataclass
class Group:
    """Represents a group."""
    # Common fields
    category: str = "group"
    id: int = 0
    href: str = ""
    type: str = "group"
    type_id: int = 2
    type_display_name: str = "Group"
    privacy_level: str = ""
    last_modified_when: str = ""
    created_when: str = ""
    last_affected_when: Optional[str] = None
    ever_approved: Optional[bool] = None
    allow_type_switching: Optional[bool] = None
    relationships_href: Optional[str] = None
    # Group specific
    group_properties: 'GroupProperties' = None
    records: List[Record] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)
    all_labels: List[Keyword] = field(default_factory=list)


@dataclass_json
@dataclass
class GroupProperties:
    """Represents group properties."""
    name: str = ""
    group_description: str = ""
    parent: Optional['Parent'] = None
    children: List['Child'] = field(default_factory=list)
    group_membership: 'GroupMembership' = None


@dataclass_json
@dataclass
class Parent:
    """Represents a parent group."""
    id: int
    href: str


@dataclass_json
@dataclass
class Child:
    """Represents a child group."""
    id: int


@dataclass_json
@dataclass
class GroupMembership:
    """Represents group membership."""
    explicit_group_members_href: str
    implicit_group_members_href: str


@dataclass_json
@dataclass
class Relationship:
    """Represents a relationship."""
    id: int
    type_id: int
    type: str
    last_modified_when: str
    href: str
    privacy_level: str
    effective_privacy_level: str
    is_favourite: bool
    related: List['RelatedObject'] = field(default_factory=list)


@dataclass_json
@dataclass
class RelatedObject:
    """Represents a related object in a relationship."""
    direction: str
    category: str
    id: int
    object: APIObject


@dataclass_json
@dataclass
class APIResponse:
    """Represents an API response."""
    version: 'Version'
    request_href: str
    result: Optional[Any] = None  # Can be APIObject or List[APIObject] or Relationship
    result_list: List[Any] = field(default_factory=list)
    pagination: Optional['PaginationInfo'] = None


@dataclass_json
@dataclass
class Version:
    """Represents API version info."""
    uri: str
    elements_version: str
    schema_version: str
    product_name: str


@dataclass_json
@dataclass
class PaginationInfo:
    """Represents pagination information."""
    results_count: int
    items_per_page: int
    page: List['Page'] = field(default_factory=list)


@dataclass_json
@dataclass
class Page:
    """Represents a page in pagination."""
    position: str
    href: str