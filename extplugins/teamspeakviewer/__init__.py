# -*- coding: utf-8 -*-
#
# Teamspeakviewer Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.5'

import b3
import b3.plugin
import b3.cron
from b3 import clients
from b3.functions import getCmd

from ts3 import TS3Server
from xml.etree.ElementTree import *

def ts3test(adresse, ts3portquery, admin, pwd, id):

    try:
    
        serverts3 = TS3Server(adresse, ts3portquery, id)
        serverts3.login(admin, pwd)

        return True
   
    except:
  
        return False 

class TeamspeakviewerPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _cronTab = None
    
    _ts3adresse = "localhost"
    _ts3hostname = "teamspeak.example.com"
    _ts3admin = "serveradmin"
    _ts3pwd = "password"
    _ts3portquery = 10011
    _ts3virtualserverid = 1
    _interval = 10
    _ts3mess1 = "Currently Online"
    _ts3mess2 = "Currently there is no people online"
    _ts3actived = True
	
    def onLoadConfig(self):

        self._ts3adresse = self.getSetting('settings', 'ts3adresse', b3.STRING, self._ts3adresse)
        self._ts3hostname = self.getSetting('settings', 'ts3hostname', b3.STRING, self._ts3hostname)
        self._ts3portquery = self.getSetting('settings', 'ts3portquery', b3.STRING, self._ts3portquery)
        self._ts3virtualserverid = self.getSetting('settings', 'ts3virtualserverid', b3.INT, self._ts3virtualserverid)
        self._ts3admin = self.getSetting('settings', 'ts3admin', b3.STRING, self._ts3admin)
        self._ts3pwd = self.getSetting('settings', 'ts3pwd', b3.STRING, self._ts3pwd)
        self._interval = self.getSetting('settings', 'interval', b3.INT, self._interval)
        self._ts3mess1 = self.getSetting('settings', 'ts3mess1', b3.STRING, self._ts3mess1)
        self._ts3mess2 = self.getSetting('settings', 'ts3mess2', b3.STRING, self._ts3mess2)
        self._ts3actived = self.getSetting('settings', 'ts3actived', b3.BOOLEAN, self._ts3actived)

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

        if self._cronTab:
            
            self.console.cron - self._cronTab

        self._cronTab = b3.cron.PluginCronTab(self, self.ts3update, minute='*/%s'%(self._interval))
        self.console.cron + self._cronTab
    
    def ts3update(self):

        if not self._ts3actived:
           
           self.debug('TeamSpeakViewer %s'%(self._ts3actived))
           return False

        if self._ts3actived:
            
            self.debug('TeamSpeakViewer %s'%(self._ts3actived))

            if ts3test(self._ts3adresse, self._ts3portquery, self._ts3admin, self._ts3pwd, self._ts3virtualserverid) == True:

                list = self.tslistclients()
                listclients = None
            
                for tsclient in list:
        
                    if listclients == None:

                        listclients = tsclient
                        
                    else:

                        listclients = listclients + ', ' + tsclient

                if listclients != None:
                    
                    self.console.say('^3TeamSpeak3 Server: ^5%s'%(self._ts3hostname))					
                    self.console.say('^3%s: '%(self._ts3mess1))
                    self.console.say('^5%s'%(listclients))       
					
                else:

                    self.console.say('^3TeamSpeak3 Server: ^5%s'%(self._ts3hostname))              

    def cmd_ts3(self, data, client, cmd=None):
        
        """\
        list of people on ts3
        """

        if ts3test(self._ts3adresse, self._ts3portquery, self._ts3admin, self._ts3pwd, self._ts3virtualserverid) == True:

            list = self.tslistclients()
            listclients = None
            
            for tsclient in list:
        
                if listclients == None:

                    listclients = tsclient
                        
                else:

                    listclients = listclients + ', ' + tsclient

            if listclients != None:
                    
                client.message('^3TeamSpeak3 Server: ^5%s'%self._ts3hostname)					
                client.message('^3%s: '%(self._ts3mess1))
                client.message('^5%s^7'%(listclients))       
					
            else:

                client.message('^3TeamSpeak3 Server: ^5%s'%(self._ts3hostname)) 
                client.message('^3%s^7'%(self._ts3mess2))
        else:

            client.message('^1ERROR TS3 SERVER')

    def cmd_ts3kick(self, data, client, cmd=None):
        
        """\
        ts3 kick
        """

        adminb3=client.name.replace("|", "*")
        adminb3=client.name.replace("/", "*")
        adminb3=client.name.replace("\\", "*")

        clid = None        

        if data:
            
            input = data.split(" ")
        
        else:

            client.message('!ts3kick <teamspeak user> <reason>')
            return
	
        listclients = None

        tslistclients = self.tslistclients()
		
        if len(input) < 2:
            reason = "You have been kicked by %s"%client.name

        else:
            reason = None
            datareason = input[1:]
            for d in datareason:
                if reason == None:
                    reason = d
                else:
                    reason = reason + " " + d

        if input[0].isdigit():
            userts = self.searchtsclid(input[0])
            self.kicktsclient(input[0], reason, adminb3)
            client.message('^3TeamSpeak Server ^2You kicked: ^5%s'%(userts))
            client.message('for ^5%s^7'%(reason))

        else:

            tsuser=input[0].lower()
            
            if len(tsuser) < 3:
                client.message('^1Need a minimum of 3 characters for the TeamSpeak user name^7')            
                return
               
            n = 0
            lusers = None
            
            for cl in tslistclients:
                  
                if tsuser in cl.lower():

                    n = n + 1
                    clid = self.tsclid(cl)
                    
                    if lusers == None:
                        clts = cl
                        lusers = "%s:%s"%(clid, cl)
                    else:
                        lusers = lusers + ", %s:%s"%(clid, cl)

            if n == 0:

                client.message('^1No Teamspeak User found^7')

            if n > 1:
                         
                client.message('^3User TeamSpeak found: ^2%s^7'%(lusers))
                    
            if n == 1:
                
                clid = self.tsclid(clts)
                self.kicktsclient(clid, reason, adminb3)
                client.message('^3TeamSpeak ^2Server You kicked: ^5%s'%(clts))
                client.message('^2for ^5%s^7'%(reason))

    def cmd_ts3poke(self, data, client, cmd=None):
        
        """\
        ts3 poke
        """

        adminb3=client.name.replace("|", "*")
        adminb3=client.name.replace("/", "*")
        adminb3=client.name.replace("\\", "*")

        clid = None        

        if data:

            input = data.split(" ")
        
        else:

            client.message('!ts3poke <teamspeak user> <message>')
            return

        listclients = None

        tslistclients = self.tslistclients()

        if len(input) < 2:
            message = "Hello !!!"

        else:
            message = None
            datamessage = input[1:]
            for d in datamessage:
                if message == None:
                    message = d
                else:
                    message = message + " " + d

        if input[0].isdigit():
            userts = self.searchtsclid(input[0])
            self.poketsclient(input[0], message, adminb3)
            client.message('^3TeamSpeak Server ^2You poke: ^5%s'%(userts))
            client.message('^2message: ^5%s^7'%(message))

        else:

            tsuser=input[0].lower()
            
            if len(tsuser) < 3:
                client.message('^1Need a minimum of 3 characters for the TeamSpeak user name^7')            
                return
                
            n = 0
            lusers = None
            
            for cl in tslistclients:
                   
                if tsuser in cl.lower():

                    n = n + 1
                    clid = self.tsclid(cl)
                    if lusers == None:
                        clts = cl
                        lusers = "%s:%s"%(clid, cl)
                    else:
                        lusers = lusers + ", %s:%s"%(clid, cl)

            if n == 0:

                client.message('^1No Teamspeak User found^7')
            if n > 1:
                         
                client.message('^3User TeamSpeak found: ^2%s^7'%(lusers))
                    
            if n == 1:
                
                clid = self.tsclid(clts)
                self.poketsclient(clid, message, adminb3)
                client.message('^3TeamSpeak Server ^2You poke: ^5%s'%(clts))
                client.message('^2message: ^5%s^7'%(message))

    def cmd_ts3msg(self, data, client, cmd=None):
        
        """\
        ts3 message
        """

        adminb3=client.name.replace("|", "*")
        adminb3=client.name.replace("/", "*")
        adminb3=client.name.replace("\\", "*")

        clid = None        

        if data:
            
            input = data.split(" ")
        
        else:

            client.message('!ts3msg <teamspeak user> <message>')
            return

        listclients = None

        tslistclients = self.tslistclients()

        if len(input) < 2:
            message = "Hello !"

        else:
            message = None
            datamessage = input[1:]
            for d in datamessage:
                if message == None:
                    message = d
                else:
                    message = message + " " + d

        if input[0].isdigit():
            
            userts = self.searchtsclid(input[0])
            self.tsclientmsg(input[0], message, adminb3)
            client.message('^3TeamSpeak Server ^2Your message to ^5%s ^2:'%(userts))
            client.message('^5%s^7'%(message))

        else:

            tsuser=input[0].lower()
            
            if len(tsuser) < 3:
                client.message('^1Need a minimum of 3 characters for the TeamSpeak user name^7')            
                return
                
            n = 0
            lusers = None
            
            for cl in tslistclients:
                   
                if tsuser in cl.lower():

                    n = n + 1
                        
                    clid = self.tsclid(cl)
                    
                    if lusers == None:
                        clts = cl
                        lusers = "%s:%s"%(clid, cl)
                    else:
                        lusers = lusers + ", %s:%s"%(clid, cl)

            if n == 0:

                client.message('^1No Teamspeak User found^7')

            if n > 1:
                         
                client.message('^3User TeamSpeak found: ^2%s^7'%(lusers))
                    
            if n == 1:
                
                clid = self.tsclid(clts)
                self.tsclientmsg(clid, message, adminb3)
                client.message('^3TeamSpeak Server ^2Your message to ^5%s^2:'%(clts))
                client.message('^5%s^7'%(message))

    def cmd_ts3channelmsg(self, data, client, cmd=None):
        
        """\
        ts3 channel message
        """

        adminb3=client.name.replace("|", "*")
        adminb3=client.name.replace("/", "*")
        adminb3=client.name.replace("\\", "*")
        
        if data:
            
            input = data
        
        else:

            client.message('!ts3channelmsg <message>')
            return

        listclients = None

        tslistclients = self.tslistclients()

        message = input


        self.tschanmsg(message, adminb3)

        client.message('^3TeamSpeak Server ^2Your message to default Channel:')
        client.message('^5%s^7'%(message))

    def cmd_ts3ban(self, data, client, cmd=None):
        
        """\
        ts3 ban
        """

        adminb3=client.name.replace("|", "*")
        adminb3=client.name.replace("/", "*")
        adminb3=client.name.replace("\\", "*")

        clid = None        

        if data:
            
            input = data.split(" ")
        
        else:

            client.message('!ts3ban <teamspeak user> <reason> <duration>')
            client.message('duration: <#mxx><#hxx><#dxx><#wxx><#p>')
            client.message('ex: #m15 for 15 minutes, #h2 for 2 hours, #d3 for 3 days, #w5 for 5 weeks, #p for permanent')

            return
	
        listclients = None

        tslistclients = self.tslistclients()

        if len(input) < 2:
            
            reason = "You have been banned by %s"%client.name
            duree = "#p"

        elif len(input) < 3:

            datax = input[1]

            if datax[:2] in "#m, #h, #d, #w, #p":
                duree = datax
                reason = "You have been banned by %s"%client.name
            
            else:
                reason = None
                datareason = input[1:]
                duree = "#p"
				
                for d in datareason:
                    if reason == None:
                        reason = d
                    else:
                        reason = reason + " " + d

        elif len(input) >= 3:

            reason = None
            datax = input[-1:]
            datay = datax[0]

            if datay[:2] in "#m, #h, #d, #w, #p":
                duree = datay
                datareason = input[1:-1]
            else:
                duree = "#p"
                datareason = input[1:]

            for d in datareason:
                if reason == None:
                    reason = d
                else:
                    reason = reason + " " + d

        if duree == "#p":
            
            time = "permanent"
            xtime = " Permanent"
        
        else:

            if duree[:2] == "#m":
                time = int(duree[2:]) * 60
                xtime = " %s minute(s)"%duree[2:]
            if duree[:2] == "#h":
                time = int(duree[2:]) * 3600
                xtime = " %s hour(s)"%duree[2:]
            if duree[:2] == "#d":
                time = int(duree[2:]) * 86400
                xtime = " %s day(s)"%duree[2:]
            if duree[:2] == "#w":
                time = int(duree[2:]) * 604800
                xtime = " %s week(s)"%duree[2:]
    
        if input[0].isdigit():
 
            userts = self.searchtsclid(input[0])
            self.bantsclient(input[0], time, reason, adminb3)
            client.message('^3TeamSpeak Server ^2You banned: ^5%s ^1%s'%(userts, xtime))
            client.message('^2for ^5%s^7'%(reason))

        else:

            tsuser=input[0].lower()
            
            if len(tsuser) < 3:
                client.message('^1Need a minimum of 3 characters for the TeamSpeak user name^7')            
                return
                
            n = 0
            lusers = None
            
            for cl in tslistclients:
                   
                if tsuser in cl.lower():

                    n = n + 1
                    clid = self.tsclid(cl)
            
                    if lusers == None:
                        clts = cl
                        lusers = "%s:%s"%(clid, cl)
                    else:
                        lusers = lusers + ", %s:%s"%(clid, cl)

            if n == 0:

                client.message('^1No Teamspeak User found^7')

            if n > 1:
                         
                client.message('^3User TeamSpeak found: ^2%s^7'%(lusers))
                    
            if n == 1:
                
                clid = self.tsclid(clts)
                self.bantsclient(clid, time, reason, adminb3)
                client.message('^3TeamSpeak Server ^2You banned: ^5%s ^1%s'%(clts, xtime))
                client.message('^2for ^5%s^7'%(reason))

    def cmd_ts3actived(self, data, client, cmd=None):
        
        """\
        activate / deactivate teamspeakviewer messages 
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
        
            if self._ts3actived:

                client.message('teamspeakviewer messages ^2activated')

            else:

                client.message('teamspeakviewer messages ^1deactivated')

            client.message('!ts3actived <on / off>')
            return

        if input[0] == 'on':

            if not self._ts3actived:

                self._ts3actived = True
                message = '^2activated'

            else:

                client.message('teamspeakviewer messages is already ^2activated') 

                return False

        if input[0] == 'off':

            if self._ts3actived:

                self._ts3actived = False
                message = '^1deactivated'

            else:
                
                client.message('teamspeakviewer messages is already ^1disabled')                

                return False

        client.message('teamspeakviewer messages %s'%(message))

        fichier = self.config.fileName
        tree = parse(fichier)
        root = tree.getroot()

        variables = root.find('settings')

        for a in variables:
           
            if a.get('name') == 'ts3actived':
      
                a.text = input[0]
        
        tree.write(fichier)

    def tslistclients(self):
	
        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
		
        clientslist = serverts3.send_command("clientlist")
        #clientslist = serverts3.clientlist()
        listclients = []
        ip = None    
        
        #for clientts in clientslist.values():
        for clientts in clientslist.data:
            dataclient = serverts3.send_command("clientinfo clid=%s"%clientts['clid'])
            
            for a in dataclient.data:
                try:
                    ip = a['connection_client_ip']
                except:
                    ip = None				

            if ip != None:
                
                client = clientts['client_nickname']            
                client = client.replace('\xc3\xa9','e')
                client = client.replace('\xc3\xa8','e')
                client = client.decode('utf-8')

                listclients.append(client)
            
        return listclients

    def searchtsclid(self, clid):

        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        
        clientslist = serverts3.clientlist()
         
        for user in clientslist.values():
            cliduser = user['clid']
            if clid == cliduser:
                username = user['client_nickname']
            
        return username
        
    def kicktsclient(self, clid, reason, client):

        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        serverts3.send_command('clientupdate client_nickname=%s(B3)'%client)
        
        serverts3.send_command('clientkick', keys={'clid': clid, 'reasonid': 5, 'reasonmsg': reason})

    def bantsclient(self, clid, time, reason, client):
        
        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        serverts3.send_command('clientupdate client_nickname=%s(B3)'%client)
        if time == "permanent":
            serverts3.send_command('banclient', keys={'clid': clid, 'banreason': reason})
        else:

            serverts3.send_command('banclient', keys={'clid': clid, 'time': time, 'banreason': reason})

    def poketsclient(self, clid, message, client):

        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        serverts3.send_command('clientupdate client_nickname=%s(B3)'%client)

        serverts3.send_command('clientpoke', keys={'clid': clid, 'msg': message})

    def tschanmsg(self, message, client):

        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        serverts3.send_command('clientupdate client_nickname=%s(B3)'%client)

        serverts3.send_command('sendtextmessage', keys={'targetmode': 2,'msg': message})

    def tsclientmsg(self, clid, message, client):

        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        serverts3.send_command('clientupdate client_nickname=%s(B3)'%client)

        serverts3.send_command('sendtextmessage', keys={'targetmode': 1, 'target': clid, 'msg': message})
    
    def tsclid(self, tsuser):

        serverts3 = TS3Server(self._ts3adresse, self._ts3portquery, self._ts3virtualserverid)
        serverts3.login(self._ts3admin, self._ts3pwd)
        clientslist = serverts3.clientlist()

        for clientts in clientslist.values():

            if tsuser == clientts['client_nickname']:
                
                return clientts['clid']
				
   
