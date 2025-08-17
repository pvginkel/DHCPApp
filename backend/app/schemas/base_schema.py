"""Base Marshmallow schema definitions."""

from marshmallow import Schema, fields


class BaseSchema(Schema):
    """Base schema with common configuration."""
    
    class Meta:
        """Schema configuration."""
        ordered = True  # Preserve field order in output


class SuccessResponseSchema(BaseSchema):
    """Schema for successful API responses."""
    
    # This is a flexible schema as success responses directly return data
    # without wrapper attributes according to ResponseHelper.success_response
    pass


class PaginationSchema(BaseSchema):
    """Schema for pagination metadata (future use)."""
    
    page = fields.Integer(
        required=True,
        metadata={"description": "Current page number", "example": 1}
    )
    per_page = fields.Integer(
        required=True,
        metadata={"description": "Items per page", "example": 20}
    )
    total = fields.Integer(
        required=True,
        metadata={"description": "Total number of items", "example": 150}
    )
    pages = fields.Integer(
        required=True,
        metadata={"description": "Total number of pages", "example": 8}
    )
