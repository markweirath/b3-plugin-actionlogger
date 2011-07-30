#
# Actionlogger Plugin for BigBrotherBot(B3) (www.bigbrotherbot.com)
# Copyright (C) 2011 Mark Weirath (xlr8or@xlr8or.com)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Changelog:

__version__ = '0.1'
__author__  = 'xlr8or'

import b3
import b3.events
import b3.plugin
import b3.output

#--------------------------------------------------------------------------------------------------
class ActionloggerPlugin(b3.plugin.Plugin):
    _logfile = 'admin.log'
    _loglevel = 40
    _log2console = False

    def startup(self):
      """\
      Initialize plugin settings
      """
      # get the admin plugin so we can register commands
      self._adminPlugin = self.console.getPlugin('admin')
      if not self._adminPlugin:
        # something is wrong, can't start without admin plugin
        self.error('Could not find admin plugin')
        return False
      # register our commands
      if 'commands' in self.config.sections():
        for cmd in self.config.options('commands'):
          level = self.config.get('commands', cmd)
          sp = cmd.split('-')
          alias = None
          if len(sp) == 2:
            cmd, alias = sp
          func = self.getCmd(cmd)
          if func:
            self._adminPlugin.registerCommand(self, cmd, level, func, alias)
      self._adminPlugin.registerCommand(self, 'aclversion', 0, self.cmd_aclversion, 'aclver')

      # Register our events
      self.verbose('Registering events')
      self.registerEvent(b3.events.EVT_CLIENT_SAY)
      self.registerEvent(b3.events.EVT_CLIENT_TEAM_SAY)
      self.registerEvent(b3.events.EVT_CLIENT_PRIVATE_SAY)

      self.debug('Started')

    def onLoadConfig(self):
        try:
          self._logfile = self.config.get('settings', 'logfile')
        except:
          self.debug('using default setting')
        try:
          self._loglevel = self.config.getint('settings', 'loglevel')
        except:
          self.debug('using default setting')
        try:
          self._log2console = self.config.getboolean('settings', 'log2console')
        except:
          self.debug('using default setting')

        self.log = b3.output.getInstance(self._logfile, 1, self._log2console)


    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None

    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if not self.isEnabled:
            return None

        if event.type == b3.events.EVT_CLIENT_SAY:
            self.logIt('Say', event.client, event.data)
        elif event.type == b3.events.EVT_CLIENT_TEAM_SAY:
            self.logIt('TeamSay', event.client, event.data)
        if event.type == b3.events.EVT_CLIENT_PRIVATE_SAY:
            self.logIt('PrivateSay', event.client, event.data)
        else:
            self.dumpEvent(event)

    def dumpEvent(self, event):
        self.debug('actionlogger.dumpEvent -- Type %s, Client %s, Target %s, Data %s',
                   event.type, event.client, event.target, event.data)

    def cmd_aclversion(self, data, client, cmd=None):
        """\
        This command identifies Plugin version and creator.
        """
        cmd.sayLoudOrPM(client, 'I am Actionlogger version %s by %s' % (__version__, __author__))
        return None

    def logIt(self, type, client, data):
        """
        Logs a b3-command to a separate logfile
        """
        if client.maxLevel >= self._loglevel:
            if data[:1] in (self._adminPlugin.cmdPrefix, self._adminPlugin.cmdPrefixLoud, self._adminPlugin.cmdPrefixBig):
                _message = '%s (%s): %s (using %s cmd)' %(client.name, client.maxLevel, data, type)
                self.log.bot(_message)


if __name__ == '__main__':
    from b3.fake import fakeConsole
    from b3.fake import admin, joe
    import time

    from b3.config import XmlConfigParser

    conf = XmlConfigParser()
    conf.setXml("""
<configuration plugin="stats">
  <settings name="settings">
    <set name="logfile">admin.log</set>
    <set name="loglevel">40</set>
    <set name="log2console">false</set>
  </settings>
</configuration>
    """)


    p = ActionloggerPlugin(fakeConsole, conf)
    p.onStartup()
    p.onLoadConfig()

    time.sleep(1)
    joe.connects(cid=3)
    joe.says("!help")

    admin.connects(cid=2)
    admin.says("hello all")
    admin.says("!help")
    admin.says("@admins")
    admin.says2team("&warn joe rule1")
