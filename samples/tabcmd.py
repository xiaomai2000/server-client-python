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
        parser.add_argument('--complete', '-c', required=True, action='store_true', help='Require all rows to be valid for any change to succeed')      # TODO NOTSUPPORTED this isn't currently supported in TSC
        parser.add_argument('--users', '-u', required=True, help='File that contains a list of users (one per line) to add to the group')
        # now that we're inside a subcommand, ignore the first TWO argvs, ie the command (tabcmd) and the subcommand (addusers)
        args = parser.parse_args(sys.argv[2:])
        print('Running tabcmd {0}, groupname={1}, complete={2}, users={3}'.format(sys._getframe().f_code.co_name, args.groupname, args.complete, args.users))

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
        # print('Running tabcmd {0}, name={1}, description={2}, contentpermissions={3}'.format(sys._getframe().f_code.co_name, args.name, args.description, args.contentpermissions))

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

    # TODO NotImplemented
    def createsiteusers(self):
        print('Creating site users')

    # TODO NotImplemented
    def createusers(self):
        print('Creating users')


    def delete(self):                                                                                                                                           # TODO making assumption that we will delete any & all items with the name
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


    # TODO NotImplemented
    def deletesiteusers(self):
        print('Deleting site users')

    # TODO NotImplemented
    def deleteusers(self):
        print('Deleting users')


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

        all_views = list(TSC.Pager(server.views))

        for v in all_views:
            print('view: ' + v.name)
            if v.name == args.name:
                our_view = v
        
        if not our_view is None:
            print('in!!!')
            if args.format == 'ascii':
                # Set our path for the output
                udd = user_data_dir('Tabcmd', 'Tableau')        # the directory for our user data directory
                file_name = os.path.join(udd, "tempViewImage.png")

                # Save the view as png
                self.save_view_as_png(server, our_view, file_name)

                # Print to ascii
                self.png_to_ascii(file_name)

            elif args.format == 'csv':
                print('NotImplemented: csv export')

            elif args.format == 'pdf':
                print('NotImplemented: pdf export')

            elif args.format == 'pdf-full':
                print('NotImplemented: pdf-full export')

            elif args.format == 'png':
                png_file = args.filename or "tabcmd-output.png"
                self.save_view_as_png(server, our_view, png_file)

    # TODO NotImplemented
    def get(self):
        print('Getting a file from the server')

    # TODO NotImplemented
    def help(self):
        print('Help for tabcmd commands')

    # TODO NotImplemented
    def initialuser(self):
        print('Creating an initial user on an uninitialized server')


    # TODO NOTSUPPORTED we don't have TSC/REST API support for domains
    def listdomains(self):
        print('Listing domains')

    # TODO NotImplemented
    def listsites(self):
        print('Listing sites for user')

    def login(self):
        parser = argparse.ArgumentParser(description='Sign in to the server')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--password', '-p', required=True, help='Use the specified password')
        parser.add_argument('--server', '-s', required=True, help='Use the specified Tableau Server URL. If no protocol is specified, http:// is assumed')
        parser.add_argument('--site', '-t', required=True, help='Use the specified Tableau Server site. Specify an empty string "" to force use of the default site')
        parser.add_argument('--username', '-u', required=True, help='Use the specified Tableau Server user name')
        args = parser.parse_args(sys.argv[2:])
        print ('Running tabcmd login, server={0}, site={1}, username={2}'.format(args.server, args.site, args.username))
        tableau_auth = TSC.TableauAuth(args.username, args.password)
        server = TSC.Server(args.server)
        server.auth.sign_in(tableau_auth)

        # write our session file
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

        new_sf = {
            "username": args.username,
            "user-id": server.user_id,
            "base-url": args.server,
            "authenticity-token": server.auth_token,
            "site-prefix": args.site,
            "site-namespace": args.site,
            "site-displayname": args.site,
            "site-id": server.site_id,
            "updated-at": now_str
        }
        print('the file: {0}'.format(new_sf))
        self.write_session_info(new_sf)

    # TODO NotImplemented
    def logout(self):
        print('Signing out from the server')

    # TODO NotImplemented
    def publish(self):
        print('Publishing a workbook, data source, or extract to the server')

    # TODO NotImplemented
    def refreshextracts(self):
        print('Refreshing the extracts of a workbook or data source on the server')

    # TODO NotImplemented
    def removeusers(self):
        print('Removing users from a group')

    # TODO NotImplemented
    def runschedule(self):
        print('Running a schedule')

    # TODO NotImplemented
    def set(self):
        print('Setting a setting on the server')

    # TODO NotImplemented
    def syncgroup(self):
        print('Synchronizing the server with an Active Directory group')

    # TODO NotImplemented  
    def version(self):
        print('Printing version information')


    ########################################
    # Utility Functions
    ########################################
    def write_session_info(self, sf):
        udd = user_data_dir('Tabcmd', 'Tableau')        # the directory for our user data directory

        if not os.path.exists(udd):
            os.makedirs(udd)

        with open(os.path.join(udd, "tabcmd-session.json"), 'w') as our_file:
            json.dump(sf, our_file)



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