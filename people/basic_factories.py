from .repositories import PersonRepo, BlockRepo
from .validators import PersonPermissionsValidator


def create_person_repo():
    return PersonRepo()


def create_block_repo():
    return BlockRepo()


def create_person_permissions_validator():
    return PersonPermissionsValidator(person_repo=create_person_repo())
