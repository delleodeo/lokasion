"""Utility functions for serializing MongoDB documents"""
from bson import ObjectId

def serialize_doc(doc):
    """Convert MongoDB document ObjectIds to strings"""
    if doc is None:
        return None
    
    # Convert the document's _id
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    # Convert common ObjectId fields
    for field in ["department_id", "teacher_id", "user_id", "event_id", "enrollment_id", "reviewed_by"]:
        if field in doc and doc[field] and isinstance(doc[field], ObjectId):
            doc[field] = str(doc[field])
    
    return doc

def serialize_list(docs):
    """Convert a list of MongoDB documents"""
    if docs is None:
        return []
    return [serialize_doc(doc) for doc in docs]
