__all__ = [
    "AuthenticatedUser",
    "AuthenticatedUserWithCollectionIds",
    "BriefCollectionSchema",
    "BriefProductSchema",
    "BriefUserSchema",
    "Collection",
    "CollectionCreate",
    "CollectionPatch",
    "CollectionProductLink",
    "CollectionSchema",
    "Product",
    "ProductSchema",
    "User",
    "UserCartLink",
    "UserCreate",
    "UserPatch",
    "UserSchema",
]

from .catalog import BriefProductSchema, Product, ProductSchema
from .collection import (
    BriefCollectionSchema,
    Collection,
    CollectionCreate,
    CollectionPatch,
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
    UserPatch,
    UserSchema,
)

UserSchema.model_rebuild()
CollectionSchema.model_rebuild()
