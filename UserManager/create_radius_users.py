from .models import RadCheck, RadGroupCheck, RadUserGroup, RadGroupReply  # Import your Registration model


def create_radius_user(user):
    """Creates a RADIUS user for the given user."""

    # Create a RADIUS user in radcheck table
    RadCheck.objects.create(username=user.email,
                            attribute='Cleartext-Password',
                            value=user.password,
                            op=':=')

    # Create a RADIUS group if it doesn't exist
    RadGroupCheck.objects.get_or_create(groupname='vip',
                                        attribute='Mikrotik-Group',
                                        op=':=',
                                        value=user.profile)
    RadGroupCheck.objects.get_or_create(groupname='viip',
                                        attribute='Mikrotik-Group',
                                        op=':=',
                                        value=user.profile)

    # Create associations for users in radusergroup
    RadUserGroup.objects.get_or_create(username=user.email,
                                       groupname='vip',
                                       priority=1)
    RadUserGroup.objects.get_or_create(username=user.email,
                                       groupname='viip',
                                       priority=1)

    # Create RADIUS group reply attributes
    RadGroupReply.objects.get_or_create(groupname='vip', attribute='Some-Attribute', op=':=',
                                        value='Some-Value')
    RadGroupReply.objects.get_or_create(groupname='viip', attribute='Some-Attribute', op=':=',
                                        value='Some-Value')

    return user
