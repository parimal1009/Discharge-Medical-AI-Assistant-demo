"""
Tests for Patient Database
"""

import pytest
from backend.database.patient_db import PatientDatabase

def test_patient_db_initialization():
    """Test patient database initialization"""
    db = PatientDatabase()
    assert db is not None
    assert db.get_patient_count() > 0

def test_patient_retrieval_exact_match():
    """Test exact name match"""
    db = PatientDatabase()
    patient = db.get_patient("John Smith")
    assert patient is not None
    assert patient["patient_name"] == "John Smith"

def test_patient_retrieval_partial_match():
    """Test partial name match"""
    db = PatientDatabase()
    patient = db.get_patient("John")
    assert patient is not None
    assert "John" in patient["patient_name"]

def test_patient_retrieval_last_name():
    """Test last name match"""
    db = PatientDatabase()
    patient = db.get_patient("Smith")
    assert patient is not None
    assert patient["patient_name"].endswith("Smith")

def test_patient_not_found():
    """Test non-existent patient"""
    db = PatientDatabase()
    patient = db.get_patient("NonExistent Person")
    assert patient is None

def test_patient_data_structure():
    """Test patient data has required fields"""
    db = PatientDatabase()
    patient = db.get_patient("John Smith")
    
    required_fields = [
        "patient_name",
        "discharge_date",
        "primary_diagnosis",
        "medications",
        "dietary_restrictions",
        "follow_up",
        "warning_signs",
        "discharge_instructions"
    ]
    
    for field in required_fields:
        assert field in patient

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
