# Docs at http://onlinehelp.tableau.com/current/server/en-us/tabcmd_cmd.htm#id1999d76f-638e-47d4-86ac-fe8e206ed364 have lots of great content and often better descriptions in the tabcmd help. We should align this stuff.

from appdirs import *
import argparse
import csv
from datetime import datetime
import json
import os
import sys
import tableauserverclient as TSC

class tabcmd(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='tabcmd in Python',
            usage='''tabcmd <command> [<args>]

The available tabcmd commands are:
   addusers           Add users to a group
   creategroup        Create a local group
   createproject      Create a project
   createsite         Create a site
   createsiteusers    Create users on the current site
   createusers        Create users on the server
   delete             Delete a workbook or data source from the server
   deletegroup        Delete a group
   deleteproject      Delete a project
   deletesite         Delete a site
   deletesiteusers    Delete site users
   deleteusers        Delete users
   editdomain         Edit a domain
   editsite           Edit a site
   export             Export the data or image of a view from the server
   get                Get a file from the server
   help               Help for tabcmd commands
   initialuser        Create an initial user on an uninitialized server
   listdomains        List domains
   listsites          List sites for user
   login              Sign in to the server
   logout             Sign out from the server
   publish            Publish a workbook, data source, or extract to the server
   refreshextracts    Refresh the extracts of a workbook or data source on the server
   removeusers        Remove users from a group
   runschedule        Run a schedule
   set                Set a setting on the server
   syncgroup          Synchronize the server with an Active Directory group
   version            Print version information
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def addusers(self):
        parser = argparse.ArgumentParser(description='Add users to a group')
        parser.add_argument('groupname', help='Name of the group')
        # parser.add_argument('--complete', '-c', required=True, action='store_true', help='Require all rows to be valid for any change to succeed')      # TODO NOTSUPPORTED this isn't currently supported in TSC
        parser.add_argument('users', help='File that contains a list of users (one per line) to add to the group')                                # TODO change from tabcmd -> making this a positional argument
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (addusers)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, groupname={1}, users={2}'.format(sys._getframe().f_code.co_name, args.groupname, args.users))

        server = self.set_server_from_session_file()

        # Get our groups, iterate to find the one we want               # TODO NOTSUPPORTED We should have a filter on groups
        for g in TSC.Pager(server.groups):
            if g.name == args.groupname:
                with open(args.users, newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        server.groups.add_user(g,row[0])            # TODO this is failing for some reason with 404002 error (Resource not found)



    def creategroup(self):
        parser = argparse.ArgumentParser(description='Create a local group')
        parser.add_argument('groupname', help='Name of the group to create')        # positional, required argument
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (creategroup)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, groupname={1}'.format(sys._getframe().f_code.co_name, args.groupname))

        server = self.set_server_from_session_file()
        new_group = TSC.GroupItem(args.groupname)
        group = server.groups.create(new_group)

    def createproject(self):
        parser = argparse.ArgumentParser(description='Create a project')
        parser.add_argument('name', help='Name of the project to create')        # positional, required argument                                # TODO this is a change from tabcmd -> making this positional arg since it's always req'd
        # parser.add_argument('--contentpermissions', '-c', required=False, help='Used to lock permissions on the project')                       # TODO NOTINTABCMD this is not something supported by tabcmd but is in the REST API + TSC
        parser.add_argument('--description', '-d', required=False, help='Description of the project')
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (createproject)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, name={1}, description={2}'.format(sys._getframe().f_code.co_name, args.name, args.description))
        
        server = self.set_server_from_session_file()
        new_project = TSC.ProjectItem(args.name, args.description)
        project = server.projects.create(new_project)


    # TODO BROKEN -> errors with 409004: Invalid Parameter errors.bad_request.detail.generic_create_site which make no sense because adminMode is set to ContentAndUsers
    def createsite(self):
        parser = argparse.ArgumentParser(description='Create a site')
        parser.add_argument('name', help='Name of the site to create')        # positional, required argument                                                                                                   # TODO this is a change from tabcmd -> called "SITENAME" in tabcmd
        parser.add_argument('--allow-subscriptions', '-as', required=False, default=True, action='store_true', 
                            help='Allow [or deny] subscriptions for this site. Default is the server default setting. Subscriptions cannot be enabled if server subscriptions are disabled')                    # TODO Do we have a bug lurking? Tabcmd says it uses server default. CONFUSINGNAMING this is "allow-subscriptions" in tablcmd but "disable-subscriptions" in TSC/REST API
        parser.add_argument('--site-mode', '-sm', required=False, default=True, action='store_true', help='Allow [or deny] site administrator from user management on site')                                    # TODO CONFUSINGNAMING this is "Site Mode" in tabcmd but "admin-mode" in TSC/REST API
        parser.add_argument('--url', '-r', required=True, help='Site ID of the site')                                                                                                                          # TODO CHANGE -> this isn't required in tabcmd; CONFUSINGNAMING We call this "url"/"Site ID" in tabcmd but it's "content_url" in TSC.
        parser.add_argument('--storage-quota', '-sq', required=False, help='Site storage quota in MB')
        parser.add_argument('--user-quota', '-uq', required=False, help='Maximum site users')                                                                                                                   # TODO CONFUSINGNAMING this is "user-quota" in tabcmd but "num-users" in TSC/REST API

        # parser.add_argument('--allow-mobile-snapshots', '-ams', required=False, default=True, action='store_true', help='Allow [or-deny] mobile snapshots. Default is to allow mobile snapshots')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--allow-web-authoring', '-awa', required=False, default=True, action='store_true', help='Allow [or deny] web authoring for this site. Default is to allow web authoring')          # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--subscription-email', '-e', required=False, help='Email used for subscriptions')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--subcription-footer', '-f', required=False, help='Footer used for subscriptions')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--guest-access-enabled', '-g', required=False, help='Guest access permission to see views for those that are not signed into a Tableau Server account')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--metrics-level', '-m', required=False, help='0 for no collection, 100 for all collections')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (createsite)
        args = parser.parse_args(sys.argv[2:])
        print('Running tabcmd {0}, name={1}, allow-subscriptions={2}, site-mode={3}, url={4}, storage-quota={5}, user-quota={6}'.format(sys._getframe().f_code.co_name, args.name, args.allow_subscriptions, args.site_mode, args.url, args.storage_quota, args.user_quota))
        server = self.set_server_from_session_file()

        # Set-up our SiteItem's AdminMode
        am = TSC.SiteItem.AdminMode.ContentAndUsers
        if args.site_mode == False:
            am = TSC.SiteItem.AdminMode.ContentOnly

        print('about to call with disable_subcriptions={0}'.format(not args.allow_subscriptions))
        print('am is {0}'.format(am))
        new_site = TSC.SiteItem(name=args.name, content_url=args.url, admin_mode=am, user_quota=args.user_quota, storage_quota=args.storage_quota, disable_subscriptions= not args.allow_subscriptions)
        site = server.sites.create(new_site)


    # TODO I didn't list out the deprecated settings from tabcmd (--publisher, --admin-type, --license)
    # TODO this won't overwrite existing users...is that OK?
    def createsiteusers(self):
        parser = argparse.ArgumentParser(description='Create users on the current site. The users are read from the given CSV file.')
        parser.add_argument('users', help='File that contains a list of users (one per line) to add to the group')
        parser.add_argument('--role', '-r', choices=['ServerAdministrator', 'SiteAdministrator', 'Publisher', 'Interactor', 'ViewerWithPublish', 'Viewer', 'UnlicensedWithPublish', 'Unlicensed'], default='Unlicensed', help='Sets the default role for all affected users.')
        # parser.add_argument('--complete', '-c', required=False, action='store_true', help='Require all rows to be valid for any change to succeed')      # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--auth-type', '-at', required=False, choices=['tableauid, saml'], default='tableauid', help='(Tableau Online only) Assigns the authentication type for all users in the CSV file. TYPE may be: TableauID, SAML. Default: TableauID')      # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--nowait', '-n', required=False, help='Do not wait for the job to complete')      # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--silent-progress', '-sp', required=False, help='Do not display progress messages for the job')      # TODO NOTSUPPORTED this isn't currently supported in TSC -> not adding this because it seems random (why not do this globally?)
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (createsiteusers)
        args = parser.parse_args(sys.argv[2:])

        server = self.set_server_from_session_file()

        with open(args.users, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                # Initialize a new user item
                user_item = TSC.UserItem('-', TSC.UserItem.Roles.Unlicensed)

                user_item.name = row[0]

                # user_password = row[1] or None        # TODO NOTSUPPORTED we don't enable this in TSC
                # user_fullname = row[2] or None      # TODO NOTSUPPORTED we don't enable setting fullname for user item in TSC

                # Override the default site role if we have something in the csv
                if len(row) > 2 and row[3] is not None:
                    user_item.site_role = row[3]

                # user_admin = row[4] or None         # TODO NOTSUPPORTED is this something we need to implement in TSC or this just dupe of the site role?
                # user_publisher = row[5] or None     # TODO NOTSUPPORTED is this something we need to implement in TSC or this just dupe of the site role?
                # user_email = row[6] or None         # TODO tabcmd says this is for Tableau Public only...what do we do with this?

                # Override the site role if we have an arg passed in
                if args.role == 'ServerAdministrator':
                    user_item.site_role = TSC.UserItem.Roles.ServerAdministrator
                elif args.role == 'SiteAdministrator':
                    user_item.site_role = TSC.UserItem.Roles.SiteAdministrator
                elif args.role == 'Publisher':
                    user_item.site_role = TSC.UserItem.Roles.Publisher
                elif args.role == 'Interactor':
                    user_item.site_role = TSC.UserItem.Roles.Interactor
                elif args.role == 'ViewerWithPublish':
                    user_item.site_role = TSC.UserItem.Roles.ViewerWithPublish
                elif args.role == 'Viewer':
                    user_item.site_role = TSC.UserItem.Roles.Viewer
                elif args.role == 'UnlicensedWithPublish':
                    user_item.site_role = TSC.UserItem.Roles.UnlicensedWithPublish

                server.users.add(user_item)

    # TODO NOTSUPPORTED There isn't a way to add a server user via TSC that isn't a member of a site
    def createusers(self):
        print('Creating users')

        # C:\Program Files\Tableau\Tableau Server\10.2\extras\Command Line Utility>tabcmd help createusers
        # Tableau Server Command Line Utility -- 10200.17.0131.2030

        # Create users. The users are read from the given CSV file. The file can have the columns in the order shown below.
        # 1. Username
        # 2. Password        (Ignored if using Active Directory)
        # 3. Friendly Name   (Ignored if using Active Directory)
        # 4. License Level (Interactor, Viewer, or Unlicensed)
        # 5. Administrator (system/site/content/none)
        # 6. Publisher (yes/true/1 or no/false/0)
        # 7. Email (only for Tableau Public)
        # The file can have fewer columns. For example, it can be a simple list with one user name per line. You can use quotation
        # marks if a value contains commas. Tabcmd waits for the createusers task to complete.  You may choose not to wait for the
        # task to complete on the server and instead return immediately by passing the --nowait flag

        # tabcmd createusers <CSV FILE> [options]
        # Command options:
        #     --[no-]complete        Require [or not] that all rows be valid for any change to succeed. Default: --complete
        #     --[no-]publisher       [Deprecated] Assigns [or removes] the publish right for all users in the CSV file. This
        #                             setting may be overridden by the values on individual rows in the CSV file. Default if not
        #                             specified: false for new users, unchanged for existing users
        #     --admin-type <TYPE>    [Deprecated] Assigns [or removes] the site admin right for all users in the CSV file. This
        #                             setting may be overridden by the values on individual rows in the CSV file. TYPE can be:
        #                             system, site, content, or none. Default if not specified: none for new users, unchanged
        #                             for existing users
        #     --license <LEVEL>      [Deprecated] Sets the default license level for all users. This may be overridden by the
        #                             value in the CSV file. LEVEL can be Interactor, Viewer, or Unlicensed
        #     --nowait               Do not wait for the job to complete
        #     -r,--role <ROLE>          Sets the default role for all affected users. Legal values for ROLE: ServerAdministrator,
        #                             SiteAdministrator, Publisher, Interactor, ViewerWithPublish, Viewer,
        #                             UnlicensedWithPublish, Unlicensed. If unspecified, server uses default value: Unlicensed
        #     --silent-progress      Do not display progress messages for the job


    def delete(self):                   # TODO making assumption that we will delete any & all items with the name
        parser = argparse.ArgumentParser(description='Delete a workbook or data source from the server')
        parser.add_argument('type', choices=['w', 'd'], help='Type of object to delete. Can be "w" or "d" for workbook or data source')        # positional, required argument     #TODO this is a change from tabcmd -> i don't like how tabcmd is structured here...cleaner 
        parser.add_argument('name', help='Name of the workbook or data source to delete')        # positional, required argument                            #TODO this is a change from tabcmd -> i don't like how tabcmd is structured here...cleaner 
        parser.add_argument('--project', '-p', required=False, default='Default', help='The project. Default project is "Default"')

        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (delete)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, type={1}, name={2}, project={3}'.format(sys._getframe().f_code.co_name, args.type, args.name, args.project))

        server = self.set_server_from_session_file()

        # Get the project item for the named project
        our_proj = None
        for p in TSC.Pager(server.projects):
            if p.name == args.project:
                our_proj = p
                break

        # Set-up our filter so we only get items with the name passed in
        request_options = TSC.RequestOptions()
        request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, args.name))
        
        # Delete workbook
        if args.type == 'w':
            all_workbooks = list(TSC.Pager(server.workbooks, request_options))
            for w in all_workbooks:
                if w.project_id == our_proj.id:
                    server.workbooks.delete(w.id)

        else:
            all_datasources = list(TSC.Pager(server.datasources, request_options))
            for d in all_datasources:
                if d.project_id == our_proj.id:
                    server.datasources.delete(d.id)

    def deletegroup(self):
        parser = argparse.ArgumentParser(description='Delete a group')
        parser.add_argument('groupname', help='Name of the group to delete')        # positional, required argument
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (deletegroup)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, groupname={1}'.format(sys._getframe().f_code.co_name, args.groupname))

        server = self.set_server_from_session_file()

        # Iterate through all the groups, deleting any with the name
        all_groups = list(TSC.Pager(server.groups))
        for g in all_groups:
            if g.name == args.groupname:
                server.groups.delete(g.id)

    def deleteproject(self):
        parser = argparse.ArgumentParser(description='Delete a project')
        parser.add_argument('projectname', help='Name of the project to delete')        # positional, required argument
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (deleteproject)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, projectname={1}'.format(sys._getframe().f_code.co_name, args.projectname))

        server = self.set_server_from_session_file()

        # Iterate through all the projects, deleting any with the name
        all_projects = list(TSC.Pager(server.projects))
        for p in all_projects:
            if p.name == args.projectname:
                server.projects.delete(p.id)

    # TODO BROKEN -> this is not working because we don't have an auth token for the site we want to delete...how to handle this?
    def deletesite(self):
        parser = argparse.ArgumentParser(description='Delete a site')
        parser.add_argument('sitename', help='Name of the site to delete')        # positional, required argument
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (deletesite)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, sitename={1}'.format(sys._getframe().f_code.co_name, args.sitename))

        server = self.set_server_from_session_file()

        # Iterate through all the sites, deleting any with the name
        all_sites = list(TSC.Pager(server.sites))
        for s in all_sites:
            print(s.name)
            if s.name == args.sitename:
                dest_server = self.set_server_from_session_file(s.id)
                print(server.site_id)
                print(dest_server.site_id)
                dest_server.sites.delete(s.id)


    # TODO tabcmd docs say this will delete from server if user is a member of only this site
    def deletesiteusers(self):
        parser = argparse.ArgumentParser(description='Delete site users (from the site you are logged into). The users are read from the given CSV file. The file is a simple list of one user name per line')
        parser.add_argument('users', help='File that contains a list of users (one per line) to remove from the site')
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (deletesiteusers)
        args = parser.parse_args(sys.argv[2:])

        server = self.set_server_from_session_file()

        with open(args.users, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                # Set-up our filter so we get the user id we need
                request_options = TSC.RequestOptions()
                request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, row[0]))

                users = list(TSC.Pager(server.users, request_options))

                try:
                    server.users.remove(users[0].id)
                except:
                    pass



    # TODO how do we sign-in to each site w/out username & password?
    def deleteusers(self):
        parser = argparse.ArgumentParser(description='Delete users The users are read from the given CSV file. The file is a simple list of one user name per line')
        parser.add_argument('users', help='File that contains a list of users (one per line) to remove from the site')
        parser.add_argument('--username', '-u', required=True, help='Username for server admin')
        parser.add_argument('--password', '-p', required=True, help='Password for server admin')
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (deletesiteusers)
        args = parser.parse_args(sys.argv[2:])

        server = self.set_server_from_session_file()

        # Keep track of the current site for later so we can get back
        current_site = server.sites.get_by_id(server.site_id)
        current_server = server

        # Get all the sites
        all_sites = list(TSC.Pager(server.sites))

        # Iterate thru all sites, deleting each user from each StopIteration
        for site in all_sites:
            # Login to the site
            sn = site.name
            if site.name == 'Default':      # fix up for default site
                sn = ""

            self.login_and_save_session_file(server._server_address, sn, args.username, args.password)
            server = self.set_server_from_session_file()

            with open(args.users, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # Set-up our filter so we get the user id we need
                    request_options = TSC.RequestOptions()
                    request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, row[0]))

                    users = list(TSC.Pager(server.users, request_options))

                    try:
                        server.users.remove(users[0].id)
                    except:
                        pass
        
        # Sign in again to original site
        osn = current_site.name
        if current_site.name == 'Default':
            osn = ""
        
        self.login_and_save_session_file(server._server_address, osn, args.username, args.password)


    # TODO NOTSUPPORTED we don't have TSC/REST API support for domains
    def editdomain(self):
        print('Editing a domain')

    # TODO BROKEN -> Getting 403010: Forbidden (User 'workgroupuser' is authenticated for site 'c288a76c-fdef-4ffb-ac61-d9bb2be96fe5' and may not access or modify resources on site 'ea7fd654-076c-4272-9ae3-2145a86d3acd'.)
    def editsite(self):
        parser = argparse.ArgumentParser(description='Edit a site')
        parser.add_argument('name', help='Name of the site to edit')        # positional, required argument                                                                                                   # TODO this is a change from tabcmd -> called "SITENAME" in tabcmd
        parser.add_argument('--allow-subscriptions', '-as', required=False,
                            help='Allow [or deny] subscriptions for this site. Default is the server default setting. Subscriptions cannot be enabled if server subscriptions are disabled')                    # TODO Do we have a bug lurking? Tabcmd says it uses server default. CONFUSINGNAMING this is "allow-subscriptions" in tablcmd but "disable-subscriptions" in TSC/REST API
        parser.add_argument('--site-name', '-sn', required=False, help='Name to change the site to')                   
        parser.add_argument('--site-mode', '-sm', required=False, help='Allow [or deny] site administrator from user management on site')                                    # TODO CONFUSINGNAMING this is "Site Mode" in tabcmd but "admin-mode" in TSC/REST API
        parser.add_argument('--url', '-r', required=False, help='Site ID of the site')                                                                                                                          # TODO CHANGE -> this isn't required in tabcmd; CONFUSINGNAMING We call this "url"/"Site ID" in tabcmd but it's "content_url" in TSC.
        parser.add_argument('--status', '-s', required=False, choices=['active', 'suspended'], help='Change availability of site. Must be either "active" or "suspended"')
        parser.add_argument('--storage-quota', '-sq', required=False, help='Site storage quota in MB')
        parser.add_argument('--user-quota', '-uq', required=False, help='Maximum site users')                                                                                                                   # TODO CONFUSINGNAMING this is "user-quota" in tabcmd but "num-users" in TSC/REST API

        # parser.add_argument('--allow-mobile-snapshots', '-ams', required=False, default=True, action='store_true', help='Allow [or-deny] mobile snapshots. Default is to allow mobile snapshots')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--allow-web-authoring', '-awa', required=False, default=True, action='store_true', help='Allow [or deny] web authoring for this site. Default is to allow web authoring')          # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--cache-warmup', '-cs', required=False, default=True, action='store_true', help='Allow [or deny] cache warmup for this site')          # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--cache-warmup-threshold', '-cwt', required=False, help='Threshold in days for how recently a view must have been viewed to trigger warmup')          # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--subscription-email', '-e', required=False, help='Email used for subscriptions')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--subcription-footer', '-f', required=False, help='Footer used for subscriptions')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--guest-access-enabled', '-g', required=False, help='Guest access permission to see views for those that are not signed into a Tableau Server account')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        # parser.add_argument('--metrics-level', '-m', required=False, help='0 for no collection, 100 for all collections')               # TODO NOTSUPPORTED this isn't currently supported in TSC
        
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (editsite)
        args = parser.parse_args(sys.argv[2:])
        # print('Running tabcmd {0}, name={1}, allow-subscriptions={2}, site-name={3}, site-mode={4}, url={5}, status={6}, storage-quota={7}, user-quota={8}'.format(sys._getframe().f_code.co_name, args.name, args.allow_subscriptions, args.site_name, args.site_mode, args.url, args.status, args.storage_quota, args.user_quota))
        server = self.set_server_from_session_file()

        # Get the site item for this site
        our_site = None
        all_sites = list(TSC.Pager(server.sites))
        for s in all_sites:
            if s.name == args.name:
                our_site = s
                break

        # Set-up our SiteItem's AdminMode
        am = None
        if args.site_mode == True:
            am = TSC.SiteItem.AdminMode.ContentAndUsers
        elif args.site_mode == False:
            am = TSC.SiteItem.AdminMode.ContentOnly

        # Set-up the State
        state = None
        if args.status == 'active':
            state = TSC.SiteItem.State.Active
        elif args.status == 'suspended':
            state = TSC.SiteItem.State.Suspended
        
        # Set/keep site values
        s.name = args.site_name or s.name
        s.content_url = args.url or s.content_url
        s.admin_mode = am or s.admin_mode
        s.user_quota = args.user_quota or s.user_quota
        s.storage_quota = args.storage_quota or s.storage_quota
        s.disable_subscriptions = not args.allow_subscriptions or s.disable_subscriptions
        s.state = state or s.state

        # Update the site
        server.sites.update(s)

    def export(self):
        parser = argparse.ArgumentParser(description='Export the data or image of a view from the server')
        parser.add_argument('name', help='Name of the workbook or view to use')        # positional, required argument                  # TODO this is a change from tabcmd -> there is no explicit arg in tabcmd
        parser.add_argument('--format', '-fo', required=True, choices=['ascii', 'csv', 'pdf', 'pdf-full', 'png'], help='Format for export. Must be "ascii", "csv", "pdf", "pdf-full", or "png"')    # TODO this is a change from tabcmd -> ascii is new and the others are all switches one their own
        parser.add_argument('--filename', '-f', required=False, help='Name to save the file as')
        # parser.add_argument('--csv', '-csv', required=False, help='Export data in CSV format')                                           # TODO this is default in tabcmd so this is breaking. NOTSUPPORTED we can't export data from TSC/REST API
        # parser.add_argument('--fullpdf', '-fp', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # parser.add_argument('--height', '-h', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # parser.add_argument('--pagelayout', '-pl', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # parser.add_argument('--pagesize', '-ps', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # parser.add_argument('--pdf', '-pdf', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # parser.add_argument('--png', '-png', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # parser.add_argument('--width', '-w', required=False, help='Export visual views in PDF format (if workbook was published with tabs)')              # TODO NOTSUPPORTED we can't export pdf from TSC/REST API
        # TODO NOTSUPPORTED Docs say you can pass in URL paramter of '?:refresh=yes'. We don't support refresh in TSC/REST API
        
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (export)
        args = parser.parse_args(sys.argv[2:])
        print('Running tabcmd {0}, name={1}, format={2}, filename={3}'.format(sys._getframe().f_code.co_name, args.name, args.format, args.filename))
        server = self.set_server_from_session_file()
        server.version = 2.5

        # TODO Only implementing views for now
        
        # Get the view item using a filter
        our_view = None
        request_options = TSC.RequestOptions()
        request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, args.name))

        all_views = list(TSC.Pager(server.views, request_options))

        for v in all_views:
            if v.name == args.name:
                our_view = v
        
        if not our_view is None:
            if args.format == 'ascii':
                # Set our path for the output
                udd = user_data_dir('Tabcmd', 'Tableau')        # the directory for our user data directory
                file_name = os.path.join(udd, "tempViewImage.png")

                # Save the view as png
                self.save_view_as_png(server, our_view, file_name)

                # Print to ascii
                self.png_to_ascii(file_name)

            elif args.format == 'csv':
                print('Not yet supported: csv export')

            elif args.format == 'pdf':
                print('Not yet supported: pdf export')

            elif args.format == 'pdf-full':
                print('Not yet supported: pdf-full export')

            elif args.format == 'png':
                png_file = args.filename or "tabcmd-output.png"
                self.save_view_as_png(server, our_view, png_file)


    # TODO Not implementing this because it seems duplicative in many ways of export. Not clear there's any functional difference.
    def get(self):
        print('Not yet available -- Getting a file from the server')

    # TODO Need to figure out how to implement this. using the if/elif structure actually calls the commands if there is only one positional arg (e.g. createsite) and doesn't display help
    def help(self):
        parser = argparse.ArgumentParser(description='Help for tabcmd')
        parser.add_argument('command', nargs='?', default=None, help='Command')

        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (help)
        args = parser.parse_args(sys.argv[2:])


        # if args.command == 'addusers':
        #     self.addusers()

        # elif args.command == 'creategroup':
        #     self.creategroup()
            
        # elif args.command == 'createproject':
        #     self.createproject()

        # if args.command == 'createsite':
        # if args.command == 'createsiteusers':
        # if args.command == 'createusers':
        # if args.command == 'delete':
        # if args.command == 'deletegroup':
        # if args.command == 'deleteproject':
        # if args.command == 'deletesite':
        # if args.command == 'deletesiteusers':
        # if args.command == 'deleteusers':
        # if args.command == 'editdomain':
        # if args.command == 'editsite':
        # if args.command == 'export':
        # if args.command == 'get':
        # if args.command == 'help':
        # if args.command == 'initialuser':
        # if args.command == 'listdomains':
        # if args.command == 'listsites':
        # if args.command == 'login':
        # if args.command == 'logout':
        # if args.command == 'publish':
        # if args.command == 'refreshextracts':
        # if args.command == 'removeusers':
        # if args.command == 'runschedule':
        # if args.command == 'set':
        # if args.command == 'syncgroup':
        # if args.command == 'version:


        #     print('''
        # tabcmd help             -- Help for tabcmd commands
        # tabcmd help <a command> -- Show Help for a specific command
        # tabcmd help commands    -- List all available commands

        # tabcmd help <a command> | commands
        #     ''')

        # else:
        #     print('nothing')





    # TODO NOTSUPPORTED MIGRATETSM We don't have support for this in TSC/REST API. I don't think it even makes sense to. This feels like TabAdmin/TSM functionality
    def initialuser(self):
        print('Creating an initial user on an uninitialized server')


    # TODO NOTSUPPORTED MIGRATETSM we don't have TSC/REST API support for domains...should this be tabadmin/TSM???
    def listdomains(self):
        print('Listing domains')


    def listsites(self):
        parser = argparse.ArgumentParser(description='Returns a list of sites to which the logged in user belongs.')

        server = self.set_server_from_session_file()

        # Iterate through all the sites, deleting any with the name
        all_sites = list(TSC.Pager(server.sites))
        for s in all_sites:
            print(s.name)

    def login(self):
        parser = argparse.ArgumentParser(description='Sign in to the server')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--password', '-p', required=True, help='Use the specified password')
        parser.add_argument('--server', '-s', required=True, help='Use the specified Tableau Server URL. If no protocol is specified, http:// is assumed')
        parser.add_argument('--site', '-t', required=True, help='Use the specified Tableau Server site. Specify an empty string "" to force use of the default site')
        parser.add_argument('--username', '-u', required=True, help='Use the specified Tableau Server user name')
        args = parser.parse_args(sys.argv[2:])
        print ('Running tabcmd login, server={0}, site={1}, username={2}'.format(args.server, args.site, args.username))

        self.login_and_save_session_file(args.server, args.site, args.username, args.password)

    def logout(self):
        # Remove info from our session file
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        session_file = self.create_session_file(None, None, None, None, None, None, now_str)
        self.write_session_info(session_file)

    # TODO NotImplemented
    def publish(self):
        parser = argparse.ArgumentParser(description='Publishes the specified workbook (.twb(x)), data source (.tds(x)), or data extract (.tde) to Tableau Server.')
        parser.add_argument('file', help='Path to the file to publish')
        parser.add_argument('--append', required=False, help='Append extract file to existing data source')
        parser.add_argument('--description', '-d', required=False, help='Description of the workbook or data source')
        parser.add_argument('--db-password', required=False, help='Database password for all data sources')
        parser.add_argument('--db-username', required=False, help='Database username for all data sources')
        parser.add_argument('--name', '-n', required=False, help='Workbook/data source name on the server. If omitted, the workbook/data source will be named after the file name, without the twb(x), tds(x), or tde extension. Publishing a .tde file will create a data source')
        parser.add_argument('--overwrite', '-o', required=False, help='Overwrite the existing workbook/data source, if any')
        parser.add_argument('--oauth-username', required=False, help='Use the credentials saved on the server keychain associated with USERNAME to publish')
        parser.add_argument('--project', '-p', required=False, help='Project to publish the workbook/data source to')          # TODO change from tabcmd which uses '-r'
        parser.add_argument('--replace', required=False, help='Replace extract file to existing data source')
        parser.add_argument('--save-db-password', required=False, action='store_true', help='Store the database password on server')
        parser.add_argument('--save-oauth', required=False, help='Embed the OAuth credentials specified with --oauth-username')
        parser.add_argument('--tabbed', required=False, help='Publish with tabbed views enabled')
        # parser.add_argument('--async', '-a', required=False, help='Publish asyncronously')                                                                                      # TODO is this supported by TSC? Not sure what to do here.
        # parser.add_argument('--restart', required=False, help='Restarts the file upload')                                                                                       # TODO NOTSUPPORTED can't restart file upload via TSC/REST API
        # parser.add_argument('--thumbnail-group', required=False, help='If the workbook contains any user filters, impersonate this group while computing thumbnails')           # TODO NOTSUPPORTED via TSC/REST API
        # parser.add_argument('--thumbnail-username', required=False, help='If the workbook contains any user filters, impersonate this user while computing thumbnails')         # TODO NOTSUPPORTED via TSC/REST API
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (publish)
        args = parser.parse_args(sys.argv[2:])

        server = self.set_server_from_session_file()

        ###################################
        # Common Settings
        ###################################
        our_file = args.file
        target_project = None
        description = None
        name = None
        publish_mode = TSC.Server.PublishMode.CreateNew        # We will create a new object unless told otherwise
        tabbed = False
        db_username = None
        db_password = None
        embed = False
        oauth_username = None
        save_oauth = False
        connection_credentials = None

        # Get the file name (no extension) and file type
        file_name, our_file_type = self.get_tableau_filetype(our_file)

        ##### Project
        # Get the project id for the specified project or for default project
        all_projects = TSC.Pager(server.projects)
        if args.project:
            target_project = next((project for project in all_projects if project.name == args.project), None)

            if target_project is None:
                raise Exception('No project named {0} was found!'.format(args.project))
        else:
            target_project = next((project for project in all_projects if project.is_default()), None)

        ###### Description
        if args.description:
            description = args.description
        
        ##### Name
        if args.name:
            name = args.name
        else:
            name = file_name

        ##### Publish Mode
        if args.overwrite:
            publish_mode = TSC.Server.PublishMode.Overwrite

        ##### Tabbed
        if args.tabbed:
            tabbed = True
        
        ##### DB Password
        if args.db_password:
            db_password = True
        
        ##### DB Username
        if args.db_username:
            db_username = True

        ##### Embed
        if args.save_db_password:
            embed = True

        ##### Embed Oauth
        if args.save_oauth:
            save_oauth = True

        ##### Oauth Username
        if args.oauth_username:
            oauth_username = args.oauth_username

        ##### Save Oauth
        if args.save_oauth:
            save_oauth = True
        
        # Change user name if oauth
        if save_oauth:
            db_username = oauth_username

        if save_oauth:
            embed = save_oauth

        ##### Connection credentials
        if (db_username and db_password):
            connection_credentials = TSC.ConnectionCredentials(db_username, db_password, embed, save_oauth)

        ## Append
        if args.append:
            publish_mode = TSC.Server.PublishMode.Append
        
        ###################################
        # Logic for different file types
        ###################################
        ##### Datasource
        if our_file_type == self.TableauFileType.Datasource:
            print('Processing a datasource...')

            datasource_item = TSC.DatasourceItem(target_project.id, name)

            if publish_mode == TSC.Server.PublishMode.Overwrite:
                # Use a filter to get the existing workbook
                request_options = TSC.RequestOptions()
                request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, name))

                all_datasources = list(TSC.Pager(server.datasources, request_options))
                datasource_item = all_datasources[0]

            server.datasources.publish(datasource_item, our_file, publish_mode, connection_credentials)
        
        ##### Extract
        elif our_file_type == self.TableauFileType.Extract:
            print('Processing an extract...')

            ## Replace
            if args.replace:
                publish_mode = TSC.Server.PublishMode.Overwrite
                
            extract_item = TSC.DatasourceItem(target_project.id, name)

            server.datasources.publish(extract_item, our_file, publish_mode)
        
        ##### Workbook
        elif our_file_type == self.TableauFileType.Workbook:
            print('Processing a workbook...')

            workbook_item = TSC.WorkbookItem(target_project.id, name, tabbed)

            if publish_mode == TSC.Server.PublishMode.Overwrite:
                # Use a filter to get the existing workbook
                request_options = TSC.RequestOptions()
                request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, name))

                all_workbooks = list(TSC.Pager(server.workbooks, request_options))
                workbook_item = all_workbooks[0]
                workbook_item.show_tabs = tabbed

            server.workbooks.publish(workbook_item, our_file, publish_mode, connection_credentials)

        else:
            print('Invalid file type. Must be one of [".tde", ".tds(x)", ".twb(x)"]')

    # TODO NOTSUPPORTED we don't have refresh support in REST API/TSC
    def refreshextracts(self):
        print('Refreshing the extracts of a workbook or data source on the server')

        # C:\Program Files\Tableau\Tableau Server\10.2\extras\Command Line Utility>tabcmd help refreshextracts
        # Tableau Server Command Line Utility -- 10200.17.0131.2030

        # Refresh the extracts of a workbook or data source on the server

        # tabcmd refreshextracts <WORKBOOK_URL> [options]
        # Command options:
        #     --datasource <DATASOURCE_NAME>    The name of the data source to refresh
        #     --incremental                     Perform an incremental refresh (if supported)
        #     --project <PROJECT_NAME>          The name of the project that contains the workbook/data source. Only necessary
        #                                         if --workbook or --daatsource is specified. If unspecified, the default project
        #                                         'Default' is used
        #     --synchronous                     Wait for the refresh to run and finish before exiting
        #     --url <WORKBOOK_URL>              The canonical name for the workbook or view as it appears in the URL
        #     --workbook <WORKBOOK_NAME>        The name of the workbook to refresh



        


    def removeusers(self):
        parser = argparse.ArgumentParser(description='Remove users from a group')
        parser.add_argument('groupname', help='Name of the group')
        # parser.add_argument('--complete', '-c', required=True, default=True, action='store_true', help='Require all rows to be valid for any change to succeed')      # TODO NOTSUPPORTED this isn't currently supported in TSC
        parser.add_argument('users', help='File that contains a list of users (one per line) to remove from the group')                                # TODO change from tabcmd -> making this a positional argument
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (removeusers)
        args = parser.parse_args(sys.argv[2:])

        server = self.set_server_from_session_file()

        # Get our groups, iterate to find the one we want               # TODO NOTSUPPORTED We should have a filter on groups
        for g in TSC.Pager(server.groups):
            if g.name == args.groupname:
                with open(args.users, newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        # Set-up our filter so we get the user id we need
                        request_options = TSC.RequestOptions()
                        request_options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, row[0]))

                        users = list(TSC.Pager(server.users, request_options))

                        try:
                            server.groups.remove_user(g,users[0].id)
                        except:
                            pass

    # TODO NOTSUPPORTED we don't have support for running a schedule via TSM/REST API
    def runschedule(self):
        print('Running a schedule')


        # C:\Program Files\Tableau\Tableau Server\10.2\extras\Command Line Utility>tabcmd help runschedule
        # Tableau Server Command Line Utility -- 10200.17.0131.2030

        # Run a schedule

        # tabcmd runschedule <SCHEDULE> [options]
        # Command options:

    # TODO NOTSUPPORTED MIGRATETSM we don't have support for server settings via TSC/REST API -> better in tabadmin/TSM.
    def set(self):
        print('Setting a setting on the server')


        # C:\Program Files\Tableau\Tableau Server\10.2\extras\Command Line Utility>tabcmd help set
        # Tableau Server Command Line Utility -- 10200.17.0131.2030

        # Set a setting on the server. Use !setting to turn a setting off

        # tabcmd set <SETTING> [options]
        # Command options:

    # TODO NOTSUPPORTED MIGRATETSM we don't have support in TSC/REST API for syncing to AD. Is this REST API or better in TSM???
    def syncgroup(self):
        print('Synchronizing the server with an Active Directory group')

        # C:\Program Files\Tableau\Tableau Server\10.2\extras\Command Line Utility>tabcmd help syncgroup
        # Tableau Server Command Line Utility -- 10200.17.0131.2030

        # Synchronize the server with an Active Directory group

        # tabcmd syncgroup <GROUPNAME> [options]
        # Command options:
        #     --[no-]publisher          [Deprecated. Use --role instead.] Assigns [or removes] the publish right for all users
        #                                 in the group.
        #     --administrator <TYPE>    [Deprecated. Use --role instead.] Assigns [or removes] the admin right for all users in
        #                                 the group. TYPE can be: system, site, content, or none.
        #     --license <LEVEL>         [Deprecated. Use --role instead.] Sets the default license level for all users in the
        #                                 group. LEVEL can be Interactor, Viewer, or Unlicensed.
        #     --overwritesiterole       Allows a users site role to be changed to a less privileged one when using --role,
        #                                 overriding the default behavior.
        #     -r,--role <ROLE>             Sets the default role for all users in the group. Legal values for LEVEL:
        #                                 ServerAdministrator, SiteAdministrator, Publisher, Interactor, ViewerWithPublish,
        #                                 Viewer, UnlicensedWithPublish, Unlicensed. If a user already exists, the given role is
        #                                 only applied if its less restrictive than the users current role. If unspecified,
        #                                 default is Unlicensed for new users and unchanged for existing users
        #     --silent-progress         Do not display progress messages for the job

    # TODO Need to implement this later after we figure out how we are shipping this 
    def version(self):
        print('Printing version information')

        # C:\Program Files\Tableau\Tableau Server\10.2\extras\Command Line Utility>tabcmd help version
        # Tableau Server Command Line Utility -- 10200.17.0131.2030

        # Print version information

        # tabcmd version
        # Command options:


    ########################################
    # Utility Functions
    ########################################
    class TableauFileType:
        Datasource = 'Datasource'
        Extract = 'Extract'
        Workbook = 'Workbook'

    def create_session_file(self, username, user_id, server, auth_token, site, site_id, now_str):
        new_sf = {
            "username": username,
            "user-id": user_id,
            "base-url": server,
            "authenticity-token": auth_token,
            "site-prefix": site,
            "site-namespace": site,
            "site-displayname": site,
            "site-id": site_id,
            "updated-at": now_str
        }

        return new_sf
    
    def get_tableau_filetype(self, path):
        tableau_file_type = 'Unknown'

        # Get just the file (no path)
        filename = os.path.basename(path)

        # Now get the extension
        filenoext, ext = os.path.splitext(filename)

        if (ext == '.tds') or (ext == '.tdsx'):
            tableau_file_type = self.TableauFileType.Datasource
        elif ext == '.tde':
            tableau_file_type = self.TableauFileType.Extract
        elif (ext == '.twb') or (ext == '.twbx'):
            tableau_file_type = self.TableauFileType.Workbook

        return filenoext, tableau_file_type

    def login_and_save_session_file(self, server, site, username, password):
        print('About to login with server={0}, site={1}, username={2}'.format(server, site, username))
        tableau_auth = TSC.TableauAuth(username, password, site)
        target_server = TSC.Server(server)
        target_server.auth.sign_in(tableau_auth)

        # write our session file
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

        session_file = self.create_session_file(username, target_server.user_id, server, target_server.auth_token, site, target_server.site_id, now_str)
        print('the file: {0}'.format(session_file))
        self.write_session_info(session_file)

    def write_session_info(self, session_file):
        udd = user_data_dir('Tabcmd', 'Tableau')        # the directory for our user data directory

        if not os.path.exists(udd):
            os.makedirs(udd)

        with open(os.path.join(udd, "tabcmd-session.json"), 'w') as our_file:
            json.dump(session_file, our_file)



    def png_to_ascii(self, png_path):
        from fabulous import image
        print(image.Image(png_path))

    def save_view_as_png(self, server, view, output_file):
        server.version = 2.5

        # Query the image endpoint and save the image to the specified location
        image_req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High)
        server.views.populate_image(view, image_req_option)

        with open(output_file, "wb") as image_file:
            image_file.write(view.image)

    # TODO There's a bug somewhere. Some function calls this with the site_id but isn't signing in again properly I think which means we don't have valid auth token
    def set_server_from_session_file(self, site_id=None):
        udd = user_data_dir('Tabcmd', 'Tableau')

        with open(os.path.join(udd, "tabcmd-session.json"), 'r') as json_data:
            f = json.load(json_data)

            server = TSC.Server(f["base-url"])

            if not site_id is None:
                server._set_auth(site_id, f["user-id"], f["authenticity-token"])
            else:
                server._set_auth(f["site-id"], f["user-id"], f["authenticity-token"])
        
        return server

if __name__ == '__main__':
    tabcmd()