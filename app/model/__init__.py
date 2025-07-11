__all__ = [
    "AuthenticatedUser",
    "AuthenticatedUserWithCollectionIds",
    "BriefCollectionSchema",
    "BriefProductSchema",
    "BriefUserSchema",
    "Collection",
    "CollectionCreate",
    "CollectionProductLink",
    "CollectionSchema",
    "Product",
    "ProductSchema",
    "User",
    "UserCartLink",
    "UserCreate",
    "UserSchema",
]

from .catalog import BriefProductSchema, Product, ProductSchema
from .collection import (
    BriefCollectionSchema,
    Collection,
    CollectionCreate,
    CollectionProductLink,
    CollectionSchema,
)
from .user import (
    AuthenticatedUser,
    AuthenticatedUserWithCollectionIds,
    BriefUserSchema,
    User,
    UserCartLink,
    UserCreate,
    UserSchema,
)

UserSchema.model_rebuild()
CollectionSchema.model_rebuild()
