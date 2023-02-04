import json
import os
from pprint import pprint

from services.google_api import GoogleAdminSDKDirectoryAPI

from modules.data_structures import Node, Graph
from config.settings import ROOT_DIR


def main():
    graph = build_GCP_permission_graph(os.path.join(
        ROOT_DIR, 'assets', 'data', 'gcp_permissions.json'))

    # Task 1
    display_task_number(1)
    print(graph)

    # Task 2
    display_task_number(2)
    ancestors = graph.get_resource_ancestors(
        Node(id='projects/p1111', type='resource'))
    pprint(ancestors)

    # Task 3
    display_task_number(3)
    resources_permissions = graph.get_resources_and_permissions_of_identity_node(
        Node(id='user:ron@test.authomize.com', type='identity'))
    pprint(resources_permissions)

    # Task 4
    display_task_number(4)
    identities_permissions = graph.get_identities_and_permissions_of_resource_node(
        Node(id='projects/p1111', type='resource'))
    pprint(identities_permissions)

    # Task 5
    display_task_number(5)
    api_client = GoogleAdminSDKDirectoryAPI()
    users = api_client.get_all_users()
    if not users:
        print('No users in the domain.')
    else:
        print('Users')
        for user in users:
            print(
                f'{user.get("primaryEmail","")} ({user.get("name",{}).get("fullName","")})')

    groups = api_client.get_all_groups()
    if not groups:
        print('No Groups in the domain')
    else:
        print('\nGroups')
        for group in groups:
            print(f'{group.get("email","")} ({ group.get("name","")})')

    print('\nMembers of each groups:')
    for group in groups:
        group_email = group.get('email', '')
        members = api_client.get_members_by_group(group_email)
        if not members:
            print(f'\nNo members in the group {group_email}')
        else:
            print(f'\nMembers of group {group_email}')
            for member in members:
                print(
                    f'{member.get("email","")} {member.get("role","")} {member.get("type","")}')

    # Task 6
    # Todo


def build_GCP_permission_graph(json_file_path: str):
    graph = Graph()
    gcp_resource_list = []

    with open(json_file_path, 'r') as gcp_permissions_json_file:
        gcp_resource_list = json.load(gcp_permissions_json_file)

    for resource in gcp_resource_list:
        resource_id = resource.get('name', '').split('.googleapis.com/')[-1]
        resource_type = resource.get('asset_type', '').split('/')[-1]
        ancestors = resource.get('ancestors', [])

        resource_node = graph.get_or_insert_node(
            Node(id=resource_id, type='resource', resource_type=resource_type))

        try:
            parent_id = ancestors[1]
            parent_node = graph.get_or_insert_node(
                Node(id=parent_id, type='resource'))
            graph.insert_edge(parent_node, resource_node,
                              'is_parent_resource_of')
        except IndexError as e:
            # resource_node is the root node and has no parent node
            pass

        bindings = resource.get('iam_policy', {}).get('bindings', [])
        for binding in bindings:
            role = binding.get('role', '')
            for identity in binding.get('members', []):
                identity_type = identity.split(':')[0]
                identity_node = graph.get_or_insert_node(
                    Node(id=identity, type='identity', identity_type=identity_type))
                graph.insert_edge(identity_node, resource_node, role)

    return graph


def display_task_number(task_number):
    print('\n', '-'*30, 'Task', task_number, '-'*30, '\n')


if (__name__ == '__main__'):
    main()
