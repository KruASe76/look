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
    "CollectionSchemaWithOwner",
    "Interaction",
    "InteractionType",
    "Product",
    "ProductSchema",
    "SearchMeta",
    "User",
    "UserCartLink",
    "UserCreate",
    "UserPatch",
    "UserSchema",
    "UserWithPreferencesSchema",
]

from .catalog import BriefProductSchema, Product, ProductSchema
from .collection import (
    BriefCollectionSchema,
    Collection,
    CollectionCreate,
    CollectionPatch,
    CollectionProductLink,
    CollectionSchema,
    CollectionSchemaWithOwner,
)
from .interaction import Interaction, InteractionType
from .misc import SearchMeta
from .user import (
    AuthenticatedUser,
    AuthenticatedUserWithCollectionIds,
    BriefUserSchema,
    User,
    UserCartLink,
    UserCreate,
    UserPatch,
    UserSchema,
    UserWithPreferencesSchema,
)

UserSchema.model_rebuild()
CollectionSchema.model_rebuild()
CollectionSchemaWithOwner.model_rebuild()
