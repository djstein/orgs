from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema

from .models import Member, Organization, Team, TeamMember

UserModel = get_user_model()


class UserSchema(ModelSchema):
    class Config:
        model = UserModel
        model_fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class OrganizationSchema(ModelSchema):
    class Config:
        model = Organization
        model_fields = [
            "name",
            "slug",
            "publicly_visible",
        ]


class CreateUpdateOrganizationSchema(ModelSchema):
    class Config:
        model = Organization
        model_fields = [
            "name",
            "publicly_visible",
        ]


class AddMemberSchema(Schema):
    username: str
    role: str = "MEMBER"


class MemberSchema(ModelSchema):
    user: UserSchema

    class Config:
        model = Member
        model_fields = ["role"]


class TeamSchema(ModelSchema):
    class Config:
        model = Team
        model_fields = ["name", "slug", "visible_to_organization"]


class CreateUpdateTeamSchema(ModelSchema):
    class Config:
        model = Team
        model_fields = ["name", "visible_to_organization"]


class UpdateMemberSchema(ModelSchema):
    class Config:
        model = Member
        model_fields = ["role"]


class TeamMemberSchema(ModelSchema):
    member: MemberSchema

    class Config:
        model = TeamMember
        model_fields = ["team_role"]


class AddTeamMemberSchema(Schema):
    username: str
    role: str = "MEMBER"


class UpdateTeamMemberSchema(ModelSchema):
    class Config:
        model = TeamMember
        model_fields = ["team_role"]
