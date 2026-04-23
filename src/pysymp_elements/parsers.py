"""XML parsers for Symplectic Elements API responses."""

from lxml import etree
from typing import List, Any, Optional
from .models import *


NS = {'api': 'http://www.symplectic.co.uk/publications/api'}


def parse_response(xml_string: str) -> APIResponse:
    """Parse the root API response."""
    root = etree.fromstring(xml_string.encode('utf-8'))
    
    version = parse_version(root.find('.//api:version', NS))
    request_href = root.find('.//api:request', NS).get('href')
    
    result = None
    result_list = []
    
    result_elem = root.find('.//api:result', NS)
    if result_elem is not None:
        result = parse_result(result_elem)
    
    result_list_elem = root.find('.//api:result-list', NS)
    if result_list_elem is not None:
        for res in result_list_elem:
            result_list.append(parse_result(res))
    
    pagination = None
    pag_elem = root.find('.//api:pagination', NS)
    if pag_elem is not None:
        pagination = parse_pagination(pag_elem)
    
    return APIResponse(
        version=version,
        request_href=request_href,
        result=result,
        result_list=result_list,
        pagination=pagination
    )


def parse_version(elem) -> Version:
    """Parse version element."""
    return Version(
        uri=elem.get('uri'),
        elements_version=elem.get('elements-version'),
        schema_version=elem.get('schema-version'),
        product_name=elem.get('product-name')
    )


def parse_pagination(elem) -> PaginationInfo:
    """Parse pagination element."""
    results_count = int(elem.get('results-count'))
    items_per_page = int(elem.get('items-per-page'))
    pages = []
    for page in elem.findall('api:page', NS):
        pages.append(Page(
            position=page.get('position'),
            href=page.get('href')
        ))
    return PaginationInfo(
        results_count=results_count,
        items_per_page=items_per_page,
        page=pages
    )


def parse_result(elem) -> Any:
    """Parse a result element."""
    obj = elem.find('api:object', NS)
    if obj is not None:
        return parse_object(obj)
    
    rel = elem.find('api:relationship', NS)
    if rel is not None:
        return parse_relationship(rel)
    
    return None


def parse_object(elem) -> Any:
    """Parse an object element."""
    category = elem.get('category')
    
    if category == 'publication':
        return parse_publication(elem)
    elif category == 'user':
        return parse_user(elem)
    elif category == 'group':
        return parse_group(elem)
    else:
        # Generic object - but since we don't have it, return None or raise
        return None


def parse_generic_object(elem) -> APIObject:
    """Parse a generic object."""
    return APIObject(
        category=elem.get('category'),
        id=int(elem.get('id')),
        href=elem.get('href'),
        type=elem.get('type'),
        type_id=int(elem.get('type-id')),
        type_display_name=elem.get('type-display-name'),
        privacy_level=elem.find('api:privacy-level', NS).text if elem.find('api:privacy-level', NS) is not None else None,
        last_modified_when=elem.get('last-modified-when'),
        created_when=elem.get('created-when'),
        last_affected_when=elem.get('last-affected-when'),
        ever_approved=parse_bool(elem.find('api:ever-approved', NS)),
        allow_type_switching=parse_bool(elem.find('api:allow-type-switching', NS)),
        relationships_href=elem.find('api:relationships', NS).get('href') if elem.find('api:relationships', NS) is not None else None
    )


def parse_publication(elem) -> Publication:
    """Parse a publication object."""
    pub = Publication()
    
    # Common fields
    pub.category = elem.get('category', 'publication')
    pub.id = int(elem.get('id', 0))
    pub.href = elem.get('href', '')
    pub.type = elem.get('type', '')
    pub.type_id = int(elem.get('type-id', 0))
    pub.type_display_name = elem.get('type-display-name', '')
    pub.privacy_level = elem.find('api:privacy-level', NS).text if elem.find('api:privacy-level', NS) is not None else ''
    pub.last_modified_when = elem.get('last-modified-when', '')
    pub.created_when = elem.get('created-when', '')
    pub.last_affected_when = elem.get('last-affected-when')
    pub.ever_approved = parse_bool(elem.find('api:ever-approved', NS))
    pub.allow_type_switching = parse_bool(elem.find('api:allow-type-switching', NS))
    pub.relationships_href = elem.find('api:relationships', NS).get('href') if elem.find('api:relationships', NS) is not None else None
    
    # Publication specific
    reporting_date_1 = elem.find('api:reporting-date-1', NS)
    pub.reporting_date_1 = reporting_date_1.text if reporting_date_1 is not None else None
    
    records = []
    records_elem = elem.find('api:records', NS)
    if records_elem is not None:
        for rec in records_elem.findall('api:record', NS):
            records.append(parse_record(rec))
    pub.records = records
    
    fields = []
    publication_fields_elem = elem.find('api:fields', NS)
    if publication_fields_elem is not None:
        for field in publication_fields_elem.findall('api:field', NS):
            fields.append(parse_field(field))

    for record in records:
        fields.extend(record.native)
        fields.extend(record.fields)

    authors = []
    for field in fields:
        if field.name == 'authors' and field.people:
            authors.extend(field.people)

    open_access_status = None
    for field in fields:
        if field.name == 'open-access-status':
            open_access_status = field.text
            break
    pub.fields = fields
    pub.authors = authors
    pub.open_access_status = open_access_status

    fields_tuples_list = [(f.name, f.text) for f in fields]
    pub.fields_dict = dict(fields_tuples_list)

    all_labels = []
    labels_elem = elem.find('api:all-labels', NS)
    if labels_elem is not None:
        for kw in labels_elem.findall('api:keywords/api:keyword', NS):
            all_labels.append(parse_keyword(kw))
    pub.all_labels = all_labels
    
    journal = None
    journal_elem = elem.find('api:journal', NS)
    if journal_elem is not None:
        journal = parse_journal(journal_elem)
    pub.journal = journal
    
    return pub


def parse_user(elem) -> User:
    """Parse a user object."""
    user = User()
    
    # Common fields
    user.category = elem.get('category', 'user')
    user.id = int(elem.get('id', 0))
    user.href = elem.get('href', '')
    user.type = elem.get('type', 'person')
    user.type_id = int(elem.get('type-id', 1))
    user.type_display_name = elem.get('type-display-name', 'Person')
    user.privacy_level = elem.find('api:privacy-level', NS).text if elem.find('api:privacy-level', NS) is not None else ''
    user.last_modified_when = elem.get('last-modified-when', '')
    user.created_when = elem.get('created-when', '')
    user.last_affected_when = elem.get('last-affected-when')
    user.ever_approved = parse_bool(elem.find('api:ever-approved', NS))
    user.allow_type_switching = parse_bool(elem.find('api:allow-type-switching', NS))
    user.relationships_href = elem.find('api:relationships', NS).get('href') if elem.find('api:relationships', NS) is not None else None
    
    # User specific
    user.proprietary_id = elem.get('proprietary-id', '')
    user.authenticating_authority = elem.get('authenticating-authority', '')
    user.username = elem.get('username', '')
    
    title = elem.find('api:title', NS)
    user.title = title.text if title is not None else None
    
    user.initials = elem.find('api:initials', NS).text if elem.find('api:initials', NS) is not None else ''
    user.last_name = elem.find('api:last-name', NS).text if elem.find('api:last-name', NS) is not None else ''
    user.first_name = elem.find('api:first-name', NS).text if elem.find('api:first-name', NS) is not None else ''
    
    pronouns = elem.find('api:user-preferred-pronouns', NS)
    user.user_preferred_pronouns = pronouns.text if pronouns is not None else None
    
    user.email_address = elem.find('api:email-address', NS).text if elem.find('api:email-address', NS) is not None else ''
    user.primary_group_descriptor = elem.find('api:primary-group-descriptor', NS).text if elem.find('api:primary-group-descriptor', NS) is not None else ''
    user.position = elem.find('api:position', NS).text if elem.find('api:position', NS) is not None else ''
    user.department = elem.find('api:department', NS).text if elem.find('api:department', NS) is not None else ''
    user.institutional_email_is_public = parse_bool(elem.find('api:institutional-email-is-public', NS)) or False
    user.claimed = parse_bool(elem.find('api:claimed', NS)) or False
    
    org_data = {}
    for data in elem.findall('api:organisation-defined-data', NS):
        key = data.get('field-name')
        value = data.text
        org_data[key] = value
    user.organisation_defined_data = org_data
    
    settings_elem = elem.find('api:user-search-settings', NS)
    user.user_search_settings = parse_user_search_settings(settings_elem) if settings_elem is not None else None
    
    records = []
    records_elem = elem.find('api:records', NS)
    if records_elem is not None:
        for rec in records_elem.findall('api:record', NS):
            records.append(parse_record(rec))
    user.records = records
    
    fields = []
    fields_elem = elem.find('api:fields', NS)
    if fields_elem is not None:
        for field in fields_elem.findall('api:field', NS):
            fields.append(parse_field(field))
    user.fields = fields
    
    all_labels = []
    labels_elem = elem.find('api:all-labels', NS)
    if labels_elem is not None:
        for kw in labels_elem.findall('api:keywords/api:keyword', NS):
            all_labels.append(parse_keyword(kw))
    user.all_labels = all_labels
    
    associations = []
    assoc_elem = elem.find('api:user-identifier-associations', NS)
    if assoc_elem is not None:
        for assoc in assoc_elem.findall('api:user-identifier-association', NS):
            associations.append(parse_user_identifier_association(assoc))
    user.user_identifier_associations = associations
    
    photo_href = elem.find('api:photo', NS)
    user.photo_href = photo_href.get('href') if photo_href is not None else None
    
    user.is_current_staff = parse_bool(elem.find('api:is-current-staff', NS)) or False
    user.is_academic = parse_bool(elem.find('api:is-academic', NS)) or False
    user.is_student = parse_bool(elem.find('api:is-student', NS)) or False
    user.is_login_allowed = parse_bool(elem.find('api:is-login-allowed', NS)) or False
    
    return user


def parse_group(elem) -> Group:
    """Parse a group object."""
    group = Group()
    
    # Common fields
    group.category = elem.get('category', 'group')
    group.id = int(elem.get('id', 0))
    group.href = elem.get('href', '')
    group.type = elem.get('type', 'group')
    group.type_id = int(elem.get('type-id', 2))
    group.type_display_name = elem.get('type-display-name', 'Group')
    group.privacy_level = elem.find('api:privacy-level', NS).text if elem.find('api:privacy-level', NS) is not None else ''
    group.last_modified_when = elem.get('last-modified-when', '')
    group.created_when = elem.get('created-when', '')
    group.last_affected_when = elem.get('last-affected-when')
    group.ever_approved = parse_bool(elem.find('api:ever-approved', NS))
    group.allow_type_switching = parse_bool(elem.find('api:allow-type-switching', NS))
    group.relationships_href = elem.find('api:relationships', NS).get('href') if elem.find('api:relationships', NS) is not None else None
    
    # Group specific
    group_properties = parse_group_properties(elem.find('api:group-properties', NS))
    group.group_properties = group_properties
    
    records = []
    records_elem = elem.find('api:records', NS)
    if records_elem is not None:
        for rec in records_elem.findall('api:record', NS):
            records.append(parse_record(rec))
    group.records = records
    
    fields = []
    fields_elem = elem.find('api:fields', NS)
    if fields_elem is not None:
        for field in fields_elem.findall('api:field', NS):
            fields.append(parse_field(field))
    group.fields = fields
    
    all_labels = []
    labels_elem = elem.find('api:all-labels', NS)
    if labels_elem is not None:
        for kw in labels_elem.findall('api:keywords/api:keyword', NS):
            all_labels.append(parse_keyword(kw))
    group.all_labels = all_labels
    
    return group


def parse_relationship(elem) -> Relationship:
    """Parse a relationship element."""
    id = int(elem.get('id'))
    type_id = int(elem.get('type-id'))
    type = elem.get('type')
    last_modified_when = elem.get('last-modified-when')
    href = elem.get('href')
    
    privacy_level = elem.find('api:privacy-level', NS).text if elem.find('api:privacy-level', NS) is not None else ''
    effective_privacy_level = elem.find('api:effective-privacy-level', NS).text if elem.find('api:effective-privacy-level', NS) is not None else ''
    is_favourite = parse_bool(elem.find('api:is-favourite', NS))
    
    related = []
    for rel in elem.findall('api:related', NS):
        related.append(parse_related_object(rel))
    
    return Relationship(
        id=id,
        type_id=type_id,
        type=type,
        last_modified_when=last_modified_when,
        href=href,
        privacy_level=privacy_level,
        effective_privacy_level=effective_privacy_level,
        is_favourite=is_favourite,
        related=related
    )


def parse_related_object(elem) -> RelatedObject:
    """Parse a related object."""
    direction = elem.get('direction')
    category = elem.get('category')
    id = int(elem.get('id'))
    obj = parse_object(elem.find('api:object', NS))
    
    return RelatedObject(
        direction=direction,
        category=category,
        id=id,
        object=obj
    )


def parse_journal(elem) -> Journal:
    """Parse a journal element."""
    issn = elem.get('issn')
    title = elem.find('api:title', NS).text if elem.find('api:title', NS) is not None else ''
    href = elem.get('href')
    
    records = []
    records_elem = elem.find('api:records', NS)
    if records_elem is not None:
        for rec in records_elem.findall('api:record', NS):
            records.append(parse_record(rec))
    
    return Journal(
        issn=issn,
        title=title,
        href=href,
        records=records
    )


def parse_record(elem) -> Record:
    """Parse a record element."""
    record = Record()
    
    record.format = elem.get('format', '')
    record.id = int(elem.get('id')) if elem.get('id') is not None else None
    record.source_id = int(elem.get('source-id', 0))
    record.source_name = elem.find('api:source-name', NS).text if elem.find('api:source-name', NS) is not None else ''
    record.source_display_name = elem.find('api:source-display-name', NS).text if elem.find('api:source-display-name', NS) is not None else ''
    record.id_at_source = elem.find('api:native-id', NS).text if elem.find('api:native-id', NS) is not None else ''
    
    citation_count = elem.find('api:citation-count', NS)
    record.citation_count = int(citation_count.text) if citation_count is not None else None
    
    native = []
    native_elem = elem.find('api:native', NS)
    if native_elem is not None:
        for field in native_elem.findall('api:field', NS):
            native.append(parse_field(field))
    record.native = native
    
    fields = []
    fields_elem = elem.find('api:fields', NS)
    if fields_elem is not None:
        for field in fields_elem.findall('api:field', NS):
            fields.append(parse_field(field))
    record.fields = fields
    
    return record


def parse_field(elem) -> Field:
    """Parse a field element."""
    name = elem.get('name')
    type = elem.get('type')
    display_name = elem.get('display-name')
    
    text = elem.find('api:text', NS)
    text = text.text if text is not None else None
    
    items = []
    items_elem = elem.find('api:items', NS)
    if items_elem is not None:
        for item in items_elem.findall('api:item', NS):
            items.append(item.text)
    
    people = []
    people_elem = elem.find('api:people', NS)
    if people_elem is not None:
        for person in people_elem.findall('api:person', NS):
            people.append(parse_person(person))
    
    links = []
    links_elem = elem.find('api:links', NS)
    if links_elem is not None:
        for link in links_elem.findall('api:link', NS):
            links.append(parse_link(link))
    
    date = elem.find('api:date', NS)
    date = parse_date(date) if date is not None else None
    
    pagination = elem.find('api:pagination', NS)
    pagination = parse_pagination_field(pagination) if pagination is not None else None
    
    keywords = []
    keywords_elem = elem.find('api:keywords', NS)
    if keywords_elem is not None:
        for kw in keywords_elem.findall('api:keyword', NS):
            keywords.append(parse_keyword(kw))
    
    addresses = []
    addresses_elem = elem.find('api:addresses', NS)
    if addresses_elem is not None:
        for addr in addresses_elem.findall('api:address', NS):
            addresses.append(parse_address(addr))
    
    identifiers = []
    identifiers_elem = elem.find('api:identifiers', NS)
    if identifiers_elem is not None:
        for ident in identifiers_elem.findall('api:identifier', NS):
            identifiers.append(parse_identifier(ident))
    
    academic_appointments = []
    apps_elem = elem.find('api:academic-appointments', NS)
    if apps_elem is not None:
        for app in apps_elem.findall('api:academic-appointment', NS):
            academic_appointments.append(parse_academic_appointment(app))
    
    degrees = []
    degrees_elem = elem.find('api:degrees', NS)
    if degrees_elem is not None:
        for deg in degrees_elem.findall('api:degree', NS):
            degrees.append(parse_degree(deg))
    
    email_addresses = []
    emails_elem = elem.find('api:email-addresses', NS)
    if emails_elem is not None:
        for email in emails_elem.findall('api:email-address', NS):
            email_addresses.append(parse_email_address(email))
    
    phone_numbers = []
    phones_elem = elem.find('api:phone-numbers', NS)
    if phones_elem is not None:
        for phone in phones_elem.findall('api:phone-number', NS):
            phone_numbers.append(parse_phone_number(phone))
    
    web_addresses = []
    webs_elem = elem.find('api:personal-websites', NS) or elem.find('api:web-addresses', NS)
    if webs_elem is not None:
        for web in webs_elem.findall('api:web-address', NS):
            web_addresses.append(parse_web_address(web))
    
    non_academic_employments = []
    emps_elem = elem.find('api:non-academic-employments', NS)
    if emps_elem is not None:
        for emp in emps_elem.findall('api:non-academic-employment', NS):
            non_academic_employments.append(parse_non_academic_employment(emp))
    
    decimal = elem.find('api:decimal', NS)
    decimal = float(decimal.text) if decimal is not None else None
    
    boolean = elem.find('api:boolean', NS)
    boolean = parse_bool(boolean)
    
    return Field(
        name=name,
        type=type,
        display_name=display_name,
        text=text,
        items=items,
        people=people,
        links=links,
        date=date,
        pagination=pagination,
        keywords=keywords,
        addresses=addresses,
        identifiers=identifiers,
        academic_appointments=academic_appointments,
        degrees=degrees,
        email_addresses=email_addresses,
        phone_numbers=phone_numbers,
        web_addresses=web_addresses,
        non_academic_employments=non_academic_employments,
        decimal=decimal,
        boolean=boolean
    )


def parse_person(elem) -> Person:
    """Parse a person element."""
    last_name = elem.find('api:last-name', NS).text if elem.find('api:last-name', NS) is not None else ''
    initials = elem.find('api:initials', NS).text if elem.find('api:initials', NS) is not None else ''
    first_names = elem.find('api:first-names', NS).text if elem.find('api:first-names', NS) is not None else ''
    
    separate_first_names = []
    sep_elem = elem.find('api:separate-first-names', NS)
    if sep_elem is not None:
        for name in sep_elem.findall('api:first-name', NS):
            separate_first_names.append(name.text)
    
    addresses = []
    addresses_elem = elem.find('api:addresses', NS)
    if addresses_elem is not None:
        for addr in addresses_elem.findall('api:address', NS):
            addresses.append(parse_address(addr))
    
    links = []
    links_elem = elem.find('api:links', NS)
    if links_elem is not None:
        for link in links_elem.findall('api:link', NS):
            links.append(parse_link(link))
    
    identifiers = []
    identifiers_elem = elem.find('api:identifiers', NS)
    if identifiers_elem is not None:
        for ident in identifiers_elem.findall('api:identifier', NS):
            identifiers.append(parse_identifier(ident))
    
    return Person(
        last_name=last_name,
        initials=initials,
        first_names=first_names,
        separate_first_names=separate_first_names,
        addresses=addresses,
        links=links,
        identifiers=identifiers
    )


def parse_link(elem) -> Link:
    """Parse a link element."""
    return Link(
        type=elem.get('type'),
        href=elem.get('href')
    )


def parse_date(elem) -> Date:
    """Parse a date element."""
    year = int(elem.find('api:year', NS).text) if elem.find('api:year', NS) is not None else 0
    month = elem.find('api:month', NS)
    month = int(month.text) if month is not None else None
    day = elem.find('api:day', NS)
    day = int(day.text) if day is not None else None
    
    return Date(year=year, month=month, day=day)


def parse_pagination_field(elem) -> Pagination:
    """Parse pagination field."""
    begin_page = elem.find('api:begin-page', NS)
    if begin_page is not None and begin_page.text is not None:
        try:
            begin_page = int(begin_page.text)
        except ValueError:
            begin_page = begin_page.text
    else:
        begin_page = None
    
    end_page = elem.find('api:end-page', NS)
    if end_page is not None and end_page.text is not None:
        try:
            end_page = int(end_page.text)
        except ValueError:
            end_page = end_page.text
    else:
        end_page = None
    
    return Pagination(begin_page=begin_page, end_page=end_page)


def parse_keyword(elem) -> Keyword:
    """Parse a keyword element."""
    return Keyword(
        scheme=elem.get('scheme'),
        text=elem.text,
        origin=elem.get('origin'),
        source=elem.get('source')
    )


def parse_address(elem) -> Address:
    """Parse an address element."""
    iso_country_code = elem.get('iso-country-code')
    line = []
    for l in elem.findall('api:line', NS):
        line.append(l.text)
    
    grid = elem.find('api:grid', NS)
    grid = parse_grid(grid) if grid is not None else None
    
    return Address(
        iso_country_code=iso_country_code,
        line=line,
        grid=grid
    )


def parse_grid(elem) -> Grid:
    """Parse a grid element."""
    lat_str = elem.get('latitude')
    lon_str = elem.get('longitude')
    return Grid(
        id=elem.get('id'),
        latitude=float(lat_str) if lat_str is not None else None,
        longitude=float(lon_str) if lon_str is not None else None
    )


def parse_identifier(elem) -> Identifier:
    """Parse an identifier element."""
    return Identifier(
        scheme=elem.get('scheme'),
        text=elem.text
    )


def parse_academic_appointment(elem) -> AcademicAppointment:
    """Parse an academic appointment."""
    institution = parse_institution(elem.find('api:institution', NS))
    position = elem.find('api:position', NS).text if elem.find('api:position', NS) is not None else ''
    start_date = elem.find('api:start-date', NS)
    start_date = parse_date(start_date) if start_date is not None else None
    end_date = elem.find('api:end-date', NS)
    end_date = parse_date(end_date) if end_date is not None else None
    
    return AcademicAppointment(
        institution=institution,
        position=position,
        start_date=start_date,
        end_date=end_date
    )


def parse_institution(elem) -> Institution:
    """Parse an institution."""
    iso_country_code = elem.get('iso-country-code')
    line = []
    for l in elem.findall('api:line', NS):
        line.append(l.text)
    
    return Institution(
        iso_country_code=iso_country_code,
        line=line
    )


def parse_degree(elem) -> Degree:
    """Parse a degree."""
    name = elem.find('api:name', NS).text if elem.find('api:name', NS) is not None else ''
    institution = parse_institution(elem.find('api:institution', NS))
    field_of_study = elem.find('api:field-of-study', NS).text if elem.find('api:field-of-study', NS) is not None else ''
    start_date = elem.find('api:start-date', NS)
    start_date = parse_date(start_date) if start_date is not None else None
    end_date = elem.find('api:end-date', NS)
    end_date = parse_date(end_date) if end_date is not None else None
    
    return Degree(
        name=name,
        institution=institution,
        field_of_study=field_of_study,
        start_date=start_date,
        end_date=end_date
    )


def parse_email_address(elem) -> EmailAddress:
    """Parse an email address."""
    return EmailAddress(
        address=elem.find('api:address', NS).text if elem.find('api:address', NS) is not None else '',
        type=elem.find('api:type', NS).text if elem.find('api:type', NS) is not None else ''
    )


def parse_phone_number(elem) -> PhoneNumber:
    """Parse a phone number."""
    return PhoneNumber(
        number=elem.find('api:number', NS).text if elem.find('api:number', NS) is not None else '',
        type=elem.find('api:type', NS).text if elem.find('api:type', NS) is not None else ''
    )


def parse_web_address(elem) -> WebAddress:
    """Parse a web address."""
    return WebAddress(
        url=elem.find('api:url', NS).text if elem.find('api:url', NS) is not None else None,
        label=elem.find('api:label', NS).text if elem.find('api:label', NS) is not None else None,
        type=elem.find('api:type', NS).text if elem.find('api:type', NS) is not None else None
    )


def parse_non_academic_employment(elem) -> NonAcademicEmployment:
    """Parse non-academic employment."""
    employer = parse_employer(elem.find('api:employer', NS))
    position = elem.find('api:position', NS).text if elem.find('api:position', NS) is not None else ''
    start_date = elem.find('api:start-date', NS)
    start_date = parse_date(start_date) if start_date is not None else None
    end_date = elem.find('api:end-date', NS)
    end_date = parse_date(end_date) if end_date is not None else None
    
    return NonAcademicEmployment(
        employer=employer,
        position=position,
        start_date=start_date,
        end_date=end_date
    )


def parse_employer(elem) -> Employer:
    """Parse an employer."""
    line = []
    for l in elem.findall('api:line', NS):
        line.append(l.text)
    
    return Employer(line=line)


def parse_user_search_settings(elem) -> UserSearchSettings:
    """Parse user search settings."""
    default = parse_search_settings(elem.find('api:default', NS))
    return UserSearchSettings(default=default)


def parse_search_settings(elem) -> SearchSettings:
    """Parse search settings."""
    affiliation = elem.find('api:affiliation', NS).text if elem.find('api:affiliation', NS) is not None else ''
    name = elem.find('api:name', NS).text if elem.find('api:name', NS) is not None else ''
    return SearchSettings(affiliation=affiliation, name=name)


def parse_user_identifier_association(elem) -> UserIdentifierAssociation:
    """Parse user identifier association."""
    return UserIdentifierAssociation(
        scheme=elem.get('scheme'),
        status=elem.get('status'),
        decision=elem.get('decision')
    )


def parse_group_properties(elem) -> GroupProperties:
    """Parse group properties."""
    name = elem.find('api:name', NS).text if elem.find('api:name', NS) is not None else ''
    group_description = elem.find('api:group-description', NS).text if elem.find('api:group-description', NS) is not None else ''
    
    parent = None
    parent_elem = elem.find('api:parent', NS)
    if parent_elem is not None:
        parent = Parent(
            id=int(parent_elem.get('id')),
            href=parent_elem.get('href')
        )
    
    children = []
    children_elem = elem.find('api:children', NS)
    if children_elem is not None:
        for child in children_elem.findall('api:child', NS):
            children.append(Child(id=int(child.get('id'))))
    
    group_membership = parse_group_membership(elem.find('api:group-membership', NS))
    
    return GroupProperties(
        name=name,
        group_description=group_description,
        parent=parent,
        children=children,
        group_membership=group_membership
    )


def parse_group_membership(elem) -> GroupMembership:
    """Parse group membership."""
    explicit = elem.find('api:explicit-group-members', NS).get('href')
    implicit = elem.find('api:implicit-group-members', NS).get('href')
    
    return GroupMembership(
        explicit_group_members_href=explicit,
        implicit_group_members_href=implicit
    )


def parse_bool(elem) -> Optional[bool]:
    """Parse a boolean element."""
    if elem is None:
        return None
    text = elem.text
    if text is None:
        return None
    return text.lower() == 'true'