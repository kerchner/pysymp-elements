"""Tests for pySympElements library."""

import unittest
from pysymp_elements import APIClient
from pysymp_elements.parsers import parse_object
from lxml import etree


class TestAPIClient(unittest.TestCase):
    """Test the APIClient class."""

    def test_client_creation(self):
        """Test that APIClient can be created."""
        client = APIClient('https://example.com', 'user', 'pass')
        self.assertIsInstance(client, APIClient)


class TestParsers(unittest.TestCase):
    """Test the XML parsers."""

    def test_parse_publication(self):
        """Test parsing a publication object."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<api:object category="publication" id="123" href="/publications/123" type="publication" type-id="1" type-display-name="Publication" xmlns:api="http://www.symplectic.co.uk/publications/api">
    <api:privacy-level>Public</api:privacy-level>
    <api:last-modified-when>2023-01-01T00:00:00Z</api:last-modified-when>
    <api:created-when>2023-01-01T00:00:00Z</api:created-when>
    <api:ever-approved>true</api:ever-approved>
    <api:allow-type-switching>false</api:allow-type-switching>
    <api:relationships href="/publications/123/relationships"/>
    <api:records>
        <api:record>
            <api:source-id>456</api:source-id>
            <api:source-name>Web of Science</api:source-name>
            <api:native-id>WOS:123456</api:native-id>
            <api:last-imported-when>2023-01-01T00:00:00Z</api:last-imported-when>
            <api:created-when>2023-01-01T00:00:00Z</api:created-when>
            <api:last-modified-when>2023-01-01T00:00:00Z</api:last-modified-when>
            <api:ever-approved>true</api:ever-approved>
            <api:approval-status>approved</api:approval-status>
            <api:approval-status-display-name>Approved</api:approval-status-display-name>
            <api:approval-status-description>Record has been approved</api:approval-status-description>
            <api:approval-status-updated-when>2023-01-01T00:00:00Z</api:approval-status-updated-when>
            <api:approval-status-updated-by>user@example.com</api:approval-status-updated-by>
            <api:fields>
                <api:field name="title" display-name="Title">
                    <api:text>Sample Publication Title</api:text>
                </api:field>
                <api:field name="open-access-status" display-name="Open access status">
                    <api:text>Green OA</api:text>
                </api:field>
                <api:field name="publication-date" type="date" display-name="Publication date">
                    <api:date>
                        <api:year>2023</api:year>
                        <api:month>5</api:month>
                        <api:day>15</api:day>
                    </api:date>
                </api:field>
            </api:fields>
        </api:record>
    </api:records>
</api:object>"""

        root = etree.fromstring(xml.encode('utf-8'))
        obj = parse_object(root)

        self.assertEqual(obj.category, 'publication')
        self.assertEqual(obj.id, 123)
        self.assertEqual(len(obj.records), 1)
        self.assertEqual(obj.records[0].source_name, 'Web of Science')
        self.assertEqual(len(obj.records[0].fields), 3)
        self.assertEqual(obj.records[0].fields[0].name, 'title')
        self.assertEqual(obj.records[0].fields[0].text, 'Sample Publication Title')
        self.assertEqual(obj.open_access_status, 'Green OA')
        self.assertIsNotNone(obj.publication_date)
        self.assertEqual(obj.publication_date.year, 2023)
        self.assertEqual(obj.publication_date.month, 5)
        self.assertEqual(obj.publication_date.day, 15)


if __name__ == '__main__':
    unittest.main()