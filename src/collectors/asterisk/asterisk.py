# coding=utf-8

import diamond.collector
import subprocess

class AsteriskCollector(diamond.collector.Collector):

    def __init__(self, *args, **kwargs):
        self.__totals = {}
        super(AsteriskCollector, self).__init__(*args, **kwargs)

    def get_default_config_help(self):
        config_help = super(AsteriskCollector, self).get_default_config_help()
        config_help.update({
            'peers':'Peers to be tracked by mointoring latency'
                    '',
            'sudo':'If send sudo asterisk command'
                   ''
        })

    def get_default_config(self):
        config = super(AsteriskCollector, self).get_default_config()
        config.update({
            'path':     'asterisk',
            'peers':    [],
            'sudo':     False
        })
        return config

    def collect(self):
        show_curcall_cmd = "'core show calls' | grep 'active calls' | awk '{print $1}'"
        self.publish("show_cur_call", self.send_cmd(show_curcall_cmd))

        show_totalcalls_cmd = "'core show calls' | grep 'calls processed' | awk '{print $1}'"
        self.publish("show_total_calls", self.send_cmd(show_totalcalls_cmd))

        for peer in self.config['peers']:
            show_peer_lat_cmd = "'sip show peer %s' | grep 'Status' | awk '{gsub(/\(/,\"\",$4);print $4}'" % peer
            self.publish("show_peer_lat_%s" % peer, self.send_cmd(show_peer_lat_cmd))

        show_online_cmd = "'sip show peers' | grep --text -i 'sip peers' | awk '{print $5}'"
        self.publish("show_online", self.send_cmd(show_online_cmd))

        show_offline_cmd = "'sip show peers'|grep --text -i 'sip peers'|awk '{print $7}'"
        self.publish("show_offline", self.send_cmd(show_offline_cmd))

        show_uptime_cmd = "'core show uptime seconds' | grep 'System uptime:' | awk '{print $3}'"
        self.publish("show_uptime", self.send_cmd(show_uptime_cmd))

        show_reload_uptime_cmd = "'core show uptime seconds' | grep 'Last reload:' | awk '{print $3}'"
        self.publish("show_reload_uptime", self.send_cmd(show_reload_uptime_cmd))

    def send_cmd(self, cmd):
        cmd = "asterisk -vx " + cmd
        if self.config['sudo']:
            cmd = 'sudo ' + cmd
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        value = process.communicate()[0].strip()
        return value if value else 0
